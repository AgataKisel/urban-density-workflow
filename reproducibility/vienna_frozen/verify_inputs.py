#!/usr/bin/env python3
"""Verify the external Vienna input bundle before offline reproduction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


PACKAGE_DIR = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_input_files(package_dir: Path = PACKAGE_DIR) -> list[str]:
    manifest_path = package_dir / "manifest.json"
    if not manifest_path.is_file():
        return [f"Missing package manifest: {manifest_path}"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for record in manifest.get("frozen_inputs", []):
        relative_path = Path(record["path"])
        path = package_dir / "inputs" / relative_path
        if not path.is_file():
            errors.append(f"Missing frozen input: inputs/{relative_path.as_posix()}")
            continue
        size = path.stat().st_size
        if size != record["size_bytes"]:
            errors.append(
                f"Size mismatch for inputs/{relative_path.as_posix()}: "
                f"expected {record['size_bytes']}, found {size}"
            )
        actual_hash = sha256(path)
        if actual_hash != record["sha256"]:
            errors.append(
                f"SHA-256 mismatch for inputs/{relative_path.as_posix()}: "
                f"expected {record['sha256']}, found {actual_hash}"
            )

    cache_manifest = package_dir / "inputs" / "reports" / "cache_manifest.json"
    if not cache_manifest.is_file():
        errors.append(f"Missing public cache compatibility metadata: {cache_manifest}")
    return errors


def main() -> int:
    errors = verify_input_files()
    if errors:
        print("Vienna frozen-input verification: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Vienna frozen-input verification: PASS")
    print("All four external files match the accepted byte sizes and SHA-256 values.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
