# WorldPulse v1.5.3 — Spatial Precision

## Changes
- Add 94 curated US state, Canadian province/territory and Mexican state representative geographic anchors to `data/north-america-regions.json`.
- Match **explicit** administrative phrases first, keeping uncertain/abbreviated mentions unmapped. Administrative anchors are NOT incident sites; do not use them to claim event coordinates.
- Keep country-level stories in the data, but show them as broader animated coverage rings plus small selectable anchor points, rather than dominant isolated columns.
- Add a map precision filter: all / place / region / country; works alongside existing category filters and clustering.
- Keep existing event layer separate from sampled news coverage.

## GitHub installation
Replace **only** `scripts/update.py`, `app.js`, and `index.html`. Add `data/north-america-regions.json` and `tests/test_spatial.py`.

**Do not overwrite** `.github/workflows/update.yml` or any of the existing news, historical, or source-health JSON snapshots. Existing workflow automatically executes the updated `scripts/update.py` and commits its established outputs.

Start a **new** workflow run on main, wait until commit completes, then hard-refresh the GitHub Pages site. Check Data Health and compare counts with your previous snapshot.

## Cautions
- Regions use representative administrative coordinates, **not geocoded event locations**.
- Country rings are centered on a representative national anchor and illustrate uncertainty, not an actual geographical boundary or evidence of distributed local reporting.
- Ring markers are sampled coverage signals, not unique events.
- Names such as `California` without qualifying context can still be ambiguous, and may resolve according to legacy gazetteer ordering. Future versions should adopt a validated country-aware geocoder with article contexts.
- The country ring visualization relies on Globe.gl's rings API and must be smoke-tested in the deployed browser.
- The locale-specific sources have not been live-tested here. No new RSS feeds are introduced.

## Test locally
`python -m unittest discover -s tests -v`
`node --check app.js`

## Future improvements
Render actual country/state boundary shapes from licensed GeoJSON, and use named-entity recognition plus place-disambiguation context instead of approximate anchor rendering.
