# WorldPulse v1.5.4A — Global Geographic Reference

## Install on existing WorldPulse v1.5.3a

Upload/replace only:

- `scripts/update.py` — replace existing file
- `scripts/global_geography.py` — add new file
- `tests/test_global_geography.py` — optional regression tests

**Do not replace** `app.js`, `index.html`, existing `data/*.json`, or `.github/workflows/update.yml`.

Go to Actions → Refresh geographic news → **Run workflow** (start a new run, don't rerun an old job). The existing GitHub Actions step `python scripts/update.py` automatically attempts a GeoNames import at startup.

## How geographic enrichment works

1. Download GeoNames `cities15000.zip` to memory (no commit, no paid key), parsing names, coordinates, country ISO code and population. This reference contains populated places of ~15,000 inhabitants and above plus some administrative centers; it is not exhaustive for small towns.
2. Prefer existing curated named places, contextual aliases and US/Canada/Mexico regional matchers.
3. If those do not match a headline, check for **globally unique, unambiguous** city names from GeoNames (minimum population 50,000). Reject frequently misleading names (e.g. `Nice`, `Mobile`, `Reading`) and duplicate city names (e.g. Springfield).
4. If a location is still missing, try the description (existing workflow).
5. If a new city name is found, keep its actual coordinates and record it as a **geographic subject**, not a verified event site.
6. If download/parsing fails, continue using existing curated geography; do not clear the news data. Each run may download GeoNames again because the ZIP is intentionally not committed to Git.

This is a **conservative first integration**, not complete world administrative geography. The next geography iteration should add country-aware city disambiguation, multilingual alternative names, ISO administrative hierarchies, GeoNames `allCountries` subset for smaller towns, and provenance/precision audits. Ambiguous names are *not* plotted automatically.

## Data health

`data/data-health.json` includes `global_gazetteer` with:
- `available`: whether the global dataset loaded
- `cities_loaded`, `candidate_names`, `ambiguous_names`
- `reason`: failure cause or loaded status

The existing `gazetteer_entries` metric still reflects the hand-curated entries; do **not** add it to GeoNames candidate names and present the total as uniquely recognized places.

## Constraints and attribution

GeoNames data: https://www.geonames.org/ , https://download.geonames.org/export/dump/ . GeoNames data is licensed under Creative Commons Attribution 4.0; credit **GeoNames.org (CC BY 4.0)** in site documentation/about panel if distributing the derived coordinates. See https://creativecommons.org/licenses/by/4.0/ .

Live download is not verified in this package-generation environment (no external DNS); check GitHub Actions for `Global geography: {'available': True, ...}` before claiming expanded data is active.

## Offline regression tests

`python -m unittest discover -s tests -p test_global_geography.py`

## Notes

- Country or region matching may still win over a city in some compound headlines: further entity-location ranking is planned.
- New matches are only geographic mentions in headlines/brief summaries.
- For a truly geographically balanced news globe, global gazetteer coverage must be paired with independent local-language news collection (planned v1.5.4B).
