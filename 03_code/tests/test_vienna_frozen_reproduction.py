from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "reproducibility" / "vienna_frozen"


def _load_script(name: str):
    path = PACKAGE / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_frozen_input_manifest_records_the_accepted_files():
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    records = {record["path"]: record for record in manifest["frozen_inputs"]}
    assert set(records) == {
        "processed/aoi_metric.gpkg",
        "processed/buildings_height_enriched.gpkg",
        "processed/streets_osmnx.gpkg",
        "reports/height_enrichment_quality.json",
    }
    assert records["processed/buildings_height_enriched.gpkg"]["sha256"] == (
        "4cc06265bcdd8780988909800d7cdc9f0d61ad2f127b7d20988747614f0402ff"
    )


def test_input_verifier_accepts_exact_files_and_rejects_checksum_mismatch(tmp_path):
    verifier = _load_script("verify_inputs.py")
    package = tmp_path / "vienna_frozen"
    (package / "inputs" / "reports").mkdir(parents=True)
    (package / "inputs" / "processed").mkdir(parents=True)
    payloads = {
        "processed/aoi_metric.gpkg": b"aoi",
        "processed/buildings_height_enriched.gpkg": b"buildings",
        "processed/streets_osmnx.gpkg": b"streets",
        "reports/height_enrichment_quality.json": b"{}",
    }
    records = []
    for relative, payload in payloads.items():
        path = package / "inputs" / relative
        path.write_bytes(payload)
        records.append(
            {
                "path": relative,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    (package / "manifest.json").write_text(
        json.dumps({"frozen_inputs": records}), encoding="utf-8"
    )
    (package / "inputs" / "reports" / "cache_manifest.json").write_text(
        "{}", encoding="utf-8"
    )
    assert verifier.verify_input_files(package) == []

    (package / "inputs" / "processed" / "aoi_metric.gpkg").write_bytes(b"changed")
    errors = verifier.verify_input_files(package)
    assert any("aoi_metric.gpkg" in error and "mismatch" in error for error in errors)


def _write_valid_result(output: Path, expected: dict):
    (output / "reports").mkdir(parents=True)
    (output / "tables").mkdir(parents=True)
    summary = {
        **expected["run_identity"],
        **expected["indicator_means"],
        **expected["coverage"],
        "used_cached_enriched_buildings": True,
        "cache_source_compatibility_status": "compatible",
        "building_source_actual_source_used": "external_cache",
    }
    (output / "reports" / "workflow_summary.json").write_text(
        json.dumps(summary), encoding="utf-8"
    )
    readiness = [
        {"indicator": indicator, "status": status}
        for indicator, status in expected["readiness"].items()
    ]
    (output / "reports" / "indicator_readiness.json").write_text(
        json.dumps(readiness), encoding="utf-8"
    )
    fields = list(expected["grid_value_semantics"])
    row_count = expected["run_identity"]["n_grid_cells"]
    rows = []
    for index in range(row_count):
        row = {}
        for field, counts in expected["grid_value_semantics"].items():
            if index < counts["zero"]:
                row[field] = "0"
            elif index < counts["valid"]:
                row[field] = "1"
            else:
                row[field] = ""
        rows.append(row)
    with (output / "tables" / "grid_indicators.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_result_verifier_accepts_contract_and_detects_numeric_change(tmp_path):
    verifier = _load_script("verify_results.py")
    expected_path = PACKAGE / "expected_results.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    output = tmp_path / "result"
    _write_valid_result(output, expected)
    assert verifier.verify_result(output, expected_path) == []

    summary_path = output / "reports" / "workflow_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["gsi_mean"] += 0.01
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    errors = verifier.verify_result(output, expected_path)
    assert any(error.startswith("gsi_mean:") for error in errors)
