# Urban Density Workflow

Urban Density Workflow is an open-source research prototype for reproducible physical urban-density analysis and exploratory spatial analysis. It measures building-based density and contextual urban morphology within a user-defined analysis area. The results are intended for research and exploratory use.

## Workflow stages

1. Define an analysis area and settings in the local Streamlit application or a YAML configuration.
2. Acquire Overture Maps Buildings for the selected area.
3. Clean and clip building geometries, select a metric CRS, and create a regular grid.
4. Calculate the enabled density and contextual morphology indicators.
5. Aggregate building-level and intersection-based results to grid cells.
6. Write spatial outputs, quality diagnostics, and indicator-readiness reports.


## Implemented indicators

| Indicator | Unit | Role | Implemented calculation and inputs |
|---|---:|---|---|
| GSI / Building Coverage Ratio | ratio | Primary 2D density | Geometric union of intersected mapped-building footprints divided by grid-cell area. Overlap is counted once. |
| FAR/FSI | ratio | Conditional density | Sum of intersected footprint area multiplied by valid floor count, divided by grid-cell area. Requires building footprints and valid floor-count data. |
| Built Volume Density | m3/m2 | Conditional 3D density | Sum of intersected footprint area multiplied by valid building height, divided by grid-cell area. |
| Average nearest-building distance | m | Contextual morphology | Mean grid-cell value of each assigned building's nearest footprint-to-footprint distance. |
| Street-profile height-to-width ratio | ratio | Contextual morphology | Building height relative to an estimated street-profile width, where the required height, street, and profile evidence are available. |

### FAR/FSI support

The implemented FAR/FSI formula is:

```text
sum(intersected footprint area x valid number of floors) / grid-cell area
```

### Average nearest-building distance

For each building, the workflow:

1. identifies the nearest **other** building;
2. measures the minimum footprint-to-footprint distance in metres;
3. assigns the building-level value to a grid cell using the building's representative point; and
4. averages the assigned nearest-building distances within each grid cell.

Touching or overlapping footprints can legitimately have a distance of zero.

## Primary density and contextual morphology

GSI / Building Coverage Ratio is the primary 2D physical-density indicator. FAR/FSI and Built Volume Density add vertical information when floor-count and height support are sufficient.

Average nearest-building distance describes building spacing. Street-profile height-to-width ratio describes contextual height-width morphology around streets. These are contextual morphology indicators.

## Implemented data sources

- **Overture Maps Buildings** is the implemented automated building source.
- **OpenStreetMap**, accessed through OSMnx, supplies street context.
- **Global Building Atlas LoD1** is an optional source for filling missing building heights.
- **CARTO and OpenStreetMap tiles** may provide visual basemaps; basemap features are not scientific workflow inputs.

The Streamlit application runs locally, and workflow results are processed and stored locally. When automated acquisition is enabled, the workflow sends spatial queries for the selected analysis area to the relevant external providers. It therefore requires network communication with Overture Maps data hosting, OpenStreetMap services through OSMnx, and optionally Global Building Atlas hosting. No external datasets are included in this repository.

## Installation

Python 3.11 or 3.12 is supported. From the repository root, create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

For development, tests, and documentation, use the platform-independent command below after activating the environment:

```bash
python -m pip install -e ".[test,docs]"
```

The project uses compiled geospatial packages. If pip cannot install compatible binaries on a platform, create a suitable Conda environment and install the project within it.

## Streamlit quick start

Start the local browser-based application with:

```bash
python -m streamlit run 03_code/app.py
```

The equivalent command in an activated environment is:

```bash
streamlit run 03_code/app.py
```

Windows users can also run:

```powershell
.\start_app.bat
```

The application lets users draw an analysis area, choose an analysis mode and grid size, run the workflow, inspect indicator maps and cell values, review data quality, and recalculate a completed area at another grid size.

## Configuration-based execution

Run the bundled example configuration:

```bash
python 03_code/run_workflow.py 03_code/config/example_urban_area_100m.yaml
```

Generate a bounding-box configuration without running the workflow:

```bash
python 03_code/scripts/create_config_from_bbox.py --run-name example_area --min-lon 4.477 --min-lat 51.918 --max-lon 4.483 --max-lat 51.922 --grid-size 100 --mode quick_2d --output 03_code/config/generated/example_area.yaml
```

The supported configuration-generator modes are:

- `quick_2d`: GSI only; height enrichment and contextual processing are disabled.
- `standard`: GSI, FAR/FSI, and Built Volume Density; optional height enrichment is enabled.
- `full_context`: the standard indicators plus Average nearest-building distance and street-profile processing.


## Analysis area

In Streamlit, draw one rectangle on the setup map. The application passes its WGS84 longitude/latitude bounds to the workflow. The configuration generator accepts the same analysis area as `--min-lon`, `--min-lat`, `--max-lon`, and `--max-lat` decimal degrees.

Automated source coverage can vary. Buildings visible on a basemap may come from a different source and do not prove that corresponding Overture footprints are available.

## Grid size and recalculation

Grid size is specified in metres. Smaller cells provide finer local summaries but create more cells and generally require more processing.

The Streamlit application can recalculate a selected completed analysis at another grid size. It preserves the stored analysis-area definition and scientific settings, then requests compatible reuse of prepared building, height, neighbour, and street-context products. Cache compatibility remains mandatory. Grid creation, exact building-grid intersections, grid aggregation, diagnostics, and dashboard presentation are recalculated.

## Reuse and provenance

Version 0.3.2 records independent compatibility contracts for cleaned
buildings, height-enriched buildings, neighbour context, grids, and street
context. This permits a later contextual run to reuse compatible upstream
artifacts while recalculating only the newly requested context. Cleaned and
height-enriched building layers have separate hashes, so a changed height
policy cannot reuse an enriched layer as its pre-enrichment input.

Regular grids use stable row/column identifiers assigned before AOI edge
clipping. Street acquisition records its OSMnx settings; advanced YAML users
may optionally supply `street_context.acquisition.overpass_endpoint` and
`timeout_seconds`. If omitted, installed OSMnx defaults are used.

## Outputs

Each run is written beneath `04_outputs/<run_name>/`. Depending on the configured output mode, principal products include:

- `processed/`: cleaned or enriched buildings and the aggregation grid;
- `indicators/`: grid indicators and building-level contextual diagnostics;
- `tables/`: tabular summaries;
- `reports/indicator_readiness.md`: user-facing interpretation guidance;
- `reports/quality_report.md`: data-quality and geometry diagnostics;
- `reports/workflow_summary.json`: resolved workflow summary;
- `reports/stage_timings.json`: processing-stage timings;
- `reports/segmented_crs_summary.json`: segmented UTM diagnostics when applicable.

The Streamlit application presents maps, selected-cell values, readiness, and limitations without requiring manual file inspection.

## Readiness statuses

The dashboard translates stored readiness evidence into five consistent user-facing statuses:

- **OK:** sufficient support for normal interpretation.
- **LIMITED:** interpretable with the stated limitations.
- **WEAK:** weak input support; strong conclusions are discouraged.
- **UNAVAILABLE:** the indicator cannot be calculated from the available inputs.
- **NOT REPORTED:** no readiness assessment exists for that result.

Read `reports/indicator_readiness.md` before interpreting results, followed by `reports/quality_report.md`. A calculated value may still have limited support when height, floor, street-match, or grid-cell coverage is incomplete.

## Missing and zero values

Missing input data and true zero values have different meanings:

- missing height is not zero height;
- missing floor count is not zero floors;
- missing building attributes are not filled with zero;
- a grid cell containing no mapped building footprints may legitimately have GSI = 0 and FAR/FSI = 0 relative to the available footprint dataset;

The official union-based GSI remains within its physical 0-1 range. The independently summed raw coverage remains available only as an overlap diagnostic.

## Optional GBA height enrichment

Global Building Atlas LoD1 enrichment is optional. It fills missing heights only and preserves valid existing heights. Availability and practical download size depend on the selected analysis area; network and storage requirements may be substantial, and the source is not guaranteed to be usable for every run.

The adapter behaviour, metric matching, minimum-overlap rules, and fill-missing-only behaviour are covered by offline tests. Global Building Atlas availability and download size remain analysis-area dependent.

## Cache-aware repeated runs

Reuse flags mean **reuse only when compatible**. Cache checks include the analysis area, exact resolved source release and provider, processing and CRS settings, relevant stage parameters, and recorded manifests. Incompatible cache products are rejected rather than silently mixed with a new run. New interface analyses use `overture_release: auto`, which resolves one dated release at run start; reproducible studies should pin a dated release.

Compatible cached products can reduce repeated processing, especially when changing only grid size. Shared cache directories are separate from individual run folders, and overwrite behavior is limited to the selected run directory.

## Limitations

- Intrinsic checks do not establish authoritative footprint completeness, positional accuracy, height accuracy, or floor-count accuracy.
- Missing footprints cannot be detected without an external reference; no mapped footprint is not proof that no building exists.
- Height and floor-count availability vary by location, directly limiting conditional indicators.
- GBA availability and practical tile size vary by analysis area.
- Street-profile results depend on OpenStreetMap coverage, profile construction, building height, and building-to-street matching.
- External acquisition depends on network services and is not temporally reproducible unless source inputs are fixed or cached.
- Grid size changes local distributions and mapped patterns.
- Segmented UTM processing is staged and retains documented cache and static-map limitations.
- Readiness supports cautious interpretation but does not establish universal accuracy or regulatory suitability.

## Repository structure

```text
03_code/
  app.py                  Local Streamlit application
  run_workflow.py         Configuration-based workflow entry point
  config/                 Public example configuration
  scripts/                Configuration and web-map utilities
  src/                    Production GIS and reporting modules
  tests/                  Compact synthetic core test suite
docs/                     Concise documentation
.streamlit/               Local application configuration
```

Generated outputs and caches are excluded from version control.

## Attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) for data-provider and basemap attribution and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for software dependency notices. Users remain responsible for complying with upstream terms when acquiring, publishing, or redistributing derived material.

## Citation

Citation metadata are provided in [CITATION.cff](CITATION.cff). No ORCID or institutional affiliation is asserted.

## License

The software is released under the [MIT License](LICENSE), Copyright (c) 2026 Agata Kiseleva. The software license does not grant rights to redistribute Overture Maps, OpenStreetMap, Global Building Atlas, or basemap data.
