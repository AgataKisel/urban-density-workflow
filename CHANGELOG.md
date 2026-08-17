# Changelog

## v0.3.0

- Adds artifact-aware cache contracts for compatible reuse of preprocessing,
  height-enrichment, neighbour, grid, and street-context artifacts.
- Records separate stable physical hashes for cleaned and height-enriched
  building layers; incompatible enriched layers cannot be reused as cleaned
  building inputs.
- Adds canonical metric AOI and regular-grid identities, including stable
  row/column identifiers assigned before edge clipping.
- Records provenance for OSMnx street acquisition, including explicit endpoint
  selection when supplied. Failed queries do not silently fall back.
- Preserves the v0.2 scientific indicator definitions and readiness semantics.

## v0.2.0

- Makes official GSI union-based: overlapping footprint coverage is counted once.
- Retains raw summed GSI and overlap fields as diagnostics.
- Treats non-finite, non-positive, near-zero, zero-length, and topology-invalid street-profile denominators as missing rather than zero.
- Adds durable Overture release handling: `auto` resolves one dated release per run; pinned releases remain exact.
- Improves compatible grid-size reruns and deferred dashboard navigation.
- Unifies dashboard, static-map, and web-export missing, zero, palette, and legend semantics.

## v0.1.0

Initial public release.
