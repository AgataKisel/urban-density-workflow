# Changelog

## v0.2.0

- Makes official GSI union-based: overlapping footprint coverage is counted once.
- Retains raw summed GSI and overlap fields as diagnostics.
- Treats non-finite, non-positive, near-zero, zero-length, and topology-invalid street-profile denominators as missing rather than zero.
- Adds durable Overture release handling: `auto` resolves one dated release per run; pinned releases remain exact.
- Improves compatible grid-size reruns and deferred dashboard navigation.
- Unifies dashboard, static-map, and web-export missing, zero, palette, and legend semantics.

## v0.1.0

Initial public release.
