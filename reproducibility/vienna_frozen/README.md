# Frozen Vienna reproduction

This package reproduces one accepted Vienna workflow result with public Urban
Density Workflow version 0.3.2. It uses a 100 m grid, 1,306 frozen buildings,
195 aggregation cells, and all five final indicators. The exercise is a
bounded, offline reference case; it is not a claim of universal numerical or
cross-platform equivalence.

## External input bundle

The four frozen input files are not distributed in this Git repository. They
include Overture-derived building data, Global Building Atlas-derived height
attributes, and OpenStreetMap-derived street data. Redistribution remains
subject to the applicable source licences and attribution requirements. The
presence of this manifest is not a legal conclusion about redistribution.

After licence review, the input archive will be published at:

`FROZEN_INPUT_BUNDLE_URL_TO_BE_ADDED_AFTER_LICENCE_REVIEW`

Extract the archive into `reproducibility/vienna_frozen/inputs/` without
flattening its `processed/` and `reports/` directories. See
[`inputs/README.md`](inputs/README.md) for the required layout and checksums.

## Run from the repository root

Install the workflow as described in the main [README](../../README.md). Then
verify the external files before running anything:

```bash
python reproducibility/vienna_frozen/verify_inputs.py
```

Run the public workflow offline:

```bash
python 03_code/run_workflow.py reproducibility/vienna_frozen/vienna_frozen_reproduction.yaml
```

Validate the output semantically:

```bash
python reproducibility/vienna_frozen/verify_results.py 04_outputs/_reproducibility/vienna_frozen_public_v0_3_2
```

The configuration deliberately uses the unsupported source type
`frozen_overture_input`. A missing or incompatible frozen cache therefore
fails locally instead of falling back to Overture, GBA, or OSM acquisition.
The tracked cache manifest contains only compatibility metadata; it contains no
third-party spatial data.

## Expected result

The accepted public v0.3.2 result contains 1,306 buildings and 195 grid cells.
Readiness is `OK` for GSI, Built Volume Density, neighbour distance, and strict
street-profile H/W, and `LIMITED` for FAR/FSI because floor-valid footprint-area
support is approximately 0.705. `expected_results.json` records the five
indicator means and valid, missing, and true-zero cell counts.

The validator applies an absolute tolerance of `1e-8` and a relative tolerance
of `1e-9` to the five aggregate means. It requires exact counts, readiness
statuses, and missing/zero semantics. Historical thesis grid identifiers and
canonical hashes are informational only because public v0.3.2 uses its current
canonical grid identity.

## Provenance

- Public reproduction software: version 0.3.2, commit
  `bba9227291b8de2ec25984fd98fb0fa1a83bf757`.
- Historical frozen workflow: commit
  `1db1813055d84328f28201ea6256b03325bf38a2`.
- Historical evaluation tooling: commit
  `917882a02274aaea6be71df409273e3e5606cdd6`.
- Frozen Overture Buildings release: `2026-05-20.0`.

The original scientific inputs are unchanged. Public v0.3.2 recomputes the
grid and indicators from those frozen inputs and validates the result against
accepted semantic outcomes.
