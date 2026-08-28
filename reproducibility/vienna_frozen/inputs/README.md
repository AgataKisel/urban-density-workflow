# External Vienna input layout

Place the separately distributed frozen files at exactly these paths:

```text
inputs/
  processed/
    aoi_metric.gpkg
    buildings_height_enriched.gpkg
    streets_osmnx.gpkg
  reports/
    cache_manifest.json              # tracked compatibility metadata
    height_enrichment_quality.json   # external accepted provenance record
```

Required external files:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `processed/aoi_metric.gpkg` | 98,304 | `d0590b1201ce9b740871424ee5a8c0daa63f122c057ffce45da4bce1e1cbd018` |
| `processed/buildings_height_enriched.gpkg` | 1,171,456 | `4cc06265bcdd8780988909800d7cdc9f0d61ad2f127b7d20988747614f0402ff` |
| `processed/streets_osmnx.gpkg` | 253,952 | `e68bd4e92d6679c4f09f8b5f1f50bb9a9ef1e548588994f67d941e125faf24ca` |
| `reports/height_enrichment_quality.json` | 2,115 | `0ae74c8b54d581b1275214b941d6046854867d5e1dd9e66846fcc2809b16d111` |

Do not rename, edit, or resave the GeoPackages. Even semantically equivalent
rewrites will have different byte-level checksums. Run
`python reproducibility/vienna_frozen/verify_inputs.py` from the repository
root after extraction.

The building and height data derive from Overture Maps and the Global Building
Atlas; the street data derive from OpenStreetMap through OSMnx. Users must
review and comply with the applicable source licences and attribution terms.
