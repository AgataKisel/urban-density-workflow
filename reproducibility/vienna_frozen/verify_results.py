#!/usr/bin/env python3
"""Verify a public Vienna reproduction against accepted semantic results."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys


PACKAGE_DIR = Path(__file__).resolve().parent


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _close(actual: float, expected: float, absolute: float, relative: float) -> bool:
    return math.isclose(actual, expected, abs_tol=absolute, rel_tol=relative)


def _optional_float(value: str | None) -> float | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"", "nan", "na", "none", "null"}:
        return None
    parsed = float(value)
    return parsed if math.isfinite(parsed) else None


def verify_result(output_dir: Path, expected_path: Path | None = None) -> list[str]:
    expected = _load_json(expected_path or PACKAGE_DIR / "expected_results.json")
    summary_path = output_dir / "reports" / "workflow_summary.json"
    readiness_path = output_dir / "reports" / "indicator_readiness.json"
    grid_path = output_dir / "tables" / "grid_indicators.csv"
    required = [summary_path, readiness_path, grid_path]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        return [f"Missing required result file: {path}" for path in missing]

    summary = _load_json(summary_path)
    readiness = _load_json(readiness_path)
    errors: list[str] = []
    for key, expected_value in expected["run_identity"].items():
        if summary.get(key) != expected_value:
            errors.append(f"{key}: expected {expected_value!r}, found {summary.get(key)!r}")

    contract = expected["comparison_contract"]
    for key, expected_value in expected["indicator_means"].items():
        actual = summary.get(key)
        if actual is None or not _close(
            float(actual),
            float(expected_value),
            contract["absolute_tolerance"],
            contract["relative_tolerance"],
        ):
            errors.append(f"{key}: expected {expected_value!r}, found {actual!r}")

    for key, expected_value in expected["coverage"].items():
        actual = summary.get(key)
        if actual is None or not _close(
            float(actual),
            float(expected_value),
            contract["absolute_tolerance"],
            contract["relative_tolerance"],
        ):
            errors.append(f"{key}: expected {expected_value!r}, found {actual!r}")

    readiness_by_indicator = {record["indicator"]: record["status"] for record in readiness}
    for indicator, expected_status in expected["readiness"].items():
        actual_status = readiness_by_indicator.get(indicator)
        if actual_status != expected_status:
            errors.append(
                f"Readiness for {indicator}: expected {expected_status}, found {actual_status}"
            )

    with grid_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != expected["run_identity"]["n_grid_cells"]:
        errors.append(
            f"Grid row count: expected {expected['run_identity']['n_grid_cells']}, "
            f"found {len(rows)}"
        )
    for field, expected_counts in expected["grid_value_semantics"].items():
        if rows and field not in rows[0]:
            errors.append(f"Missing grid field: {field}")
            continue
        values = [_optional_float(row.get(field)) for row in rows]
        actual_counts = {
            "valid": sum(value is not None for value in values),
            "missing": sum(value is None for value in values),
            "zero": sum(value == 0.0 for value in values if value is not None),
        }
        if actual_counts != expected_counts:
            errors.append(
                f"{field} semantics: expected {expected_counts}, found {actual_counts}"
            )

    if summary.get("used_cached_enriched_buildings") is not True:
        errors.append("Frozen enriched buildings were not reported as reused.")
    if summary.get("cache_source_compatibility_status") != "compatible":
        errors.append("Frozen cache was not reported as compatible.")
    if summary.get("building_source_actual_source_used") != "external_cache":
        errors.append("Building source was not reported as the external frozen cache.")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args(argv)
    errors = verify_result(args.output_dir.resolve())
    if errors:
        print("Vienna frozen-result verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Vienna frozen-result verification: PASS")
    print("Counts, five means, readiness, and missing/zero semantics match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
