"""Known-answer tests for union-based GSI coverage."""

from pathlib import Path
import sys

import geopandas as gpd
import pytest
from shapely.geometry import box


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from indicators import calculate_gsi, run_indicators  # noqa: E402


CRS = "EPSG:32633"


def _units(*geometries):
    return gpd.GeoDataFrame(
        {"unit_id": [f"cell_{index}" for index in range(len(geometries))]},
        geometry=list(geometries),
        crs=CRS,
    )


def _buildings(*geometries):
    return gpd.GeoDataFrame(
        {"building_id": [f"building_{index}" for index in range(len(geometries))]},
        geometry=list(geometries),
        crs=CRS,
    )


def _run_config(shared_area_intersections: bool):
    return {
        "indicators": {
            "gsi": True,
            "far_fsi": False,
            "built_volume_density": False,
            "neighbor_distance": False,
            "height_to_distance_ratio": False,
        },
        "performance": {
            "shared_area_intersections": shared_area_intersections,
        },
    }


def test_gsi_uses_union_for_overlapping_and_duplicate_footprints():
    result = calculate_gsi(
        _buildings(box(0, 0, 4, 4), box(2, 0, 6, 4)),
        _units(box(0, 0, 10, 10)),
    ).iloc[0]
    assert result.gsi == pytest.approx(0.24)
    assert result.gsi_raw_sum == pytest.approx(0.32)
    assert result.building_footprint_union_area_m2 == pytest.approx(24.0)
    assert result.footprint_overlap_area_m2 == pytest.approx(8.0)
    assert result.footprint_overlap_flag

    duplicate = calculate_gsi(
        _buildings(box(0, 0, 10, 10), box(0, 0, 10, 10)),
        _units(box(0, 0, 10, 10)),
    ).iloc[0]
    assert duplicate.gsi == pytest.approx(1.0)
    assert duplicate.gsi_raw_sum == pytest.approx(2.0)
    assert duplicate.gsi_overlap_difference == pytest.approx(1.0)


def test_gsi_partitions_crossing_footprints_and_preserves_true_zeros():
    crossing = calculate_gsi(
        _buildings(box(5, 0, 15, 10)),
        _units(box(0, 0, 10, 10), box(10, 0, 20, 10)),
    ).set_index("unit_id")
    assert crossing.loc["cell_0", "gsi"] == pytest.approx(0.5)
    assert crossing.loc["cell_1", "gsi"] == pytest.approx(0.5)

    empty = calculate_gsi(_buildings(), _units(box(0, 0, 10, 10))).iloc[0]
    assert empty.gsi == 0.0
    assert empty.gsi_raw_sum == 0.0


@pytest.mark.parametrize("shared_area_intersections", [True, False])
@pytest.mark.parametrize(
    ("geometries", "expected_gsi", "expected_raw_gsi"),
    [
        ([box(0, 0, 5, 10)], 0.5, 0.5),
        ([box(0, 0, 4, 10), box(6, 0, 10, 10)], 0.8, 0.8),
        ([box(0, 0, 6, 10), box(4, 0, 10, 10)], 1.0, 1.2),
        ([box(0, 0, 5, 10), box(0, 0, 5, 10)], 0.5, 1.0),
    ],
    ids=["single", "non_overlapping", "overlapping", "duplicate"],
)
def test_normal_indicator_path_preserves_union_based_gsi(
    shared_area_intersections,
    geometries,
    expected_gsi,
    expected_raw_gsi,
):
    result = run_indicators(
        buildings=_buildings(*geometries),
        units=_units(box(0, 0, 10, 10)),
        config=_run_config(shared_area_intersections),
    ).iloc[0]

    assert result.gsi == pytest.approx(expected_gsi)
    assert result.gsi_raw_sum == pytest.approx(expected_raw_gsi)
    assert result.building_footprint_union_area_m2 == pytest.approx(
        expected_gsi * 100
    )
    assert result.building_footprint_area_raw_sum_m2 == pytest.approx(
        expected_raw_gsi * 100
    )
    if expected_gsi != expected_raw_gsi:
        assert result.gsi_raw_sum != pytest.approx(result.gsi)
        assert result.footprint_overlap_flag


@pytest.mark.parametrize("shared_area_intersections", [True, False])
def test_normal_indicator_path_partitions_crossing_footprints(
    shared_area_intersections,
):
    result = run_indicators(
        buildings=_buildings(box(5, 0, 15, 10)),
        units=_units(box(0, 0, 10, 10), box(10, 0, 20, 10)),
        config=_run_config(shared_area_intersections),
    ).set_index("unit_id")

    assert result.loc["cell_0", "gsi"] == pytest.approx(0.5)
    assert result.loc["cell_1", "gsi"] == pytest.approx(0.5)


def test_shared_intersections_preserve_far_and_bvd_overlap_semantics():
    buildings = gpd.GeoDataFrame(
        {
            "building_id": ["building_0", "building_1"],
            "num_floors": [2.0, 3.0],
            "height_m": [10.0, 20.0],
        },
        geometry=[box(0, 0, 6, 10), box(4, 0, 10, 10)],
        crs=CRS,
    )
    config = {
        "indicators": {
            "gsi": True,
            "far_fsi": True,
            "built_volume_density": True,
            "neighbor_distance": False,
            "height_to_distance_ratio": False,
        },
    }

    shared = run_indicators(
        buildings,
        _units(box(0, 0, 10, 10)),
        {**config, "performance": {"shared_area_intersections": True}},
    ).iloc[0]
    individual = run_indicators(
        buildings,
        _units(box(0, 0, 10, 10)),
        {**config, "performance": {"shared_area_intersections": False}},
    ).iloc[0]

    assert shared.far_fsi == pytest.approx(individual.far_fsi)
    assert shared.built_volume_density == pytest.approx(
        individual.built_volume_density
    )
    assert shared.floor_data_valid_area_share == pytest.approx(
        individual.floor_data_valid_area_share
    )
    assert shared.height_valid_area_share == pytest.approx(
        individual.height_valid_area_share
    )
