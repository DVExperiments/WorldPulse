# WorldPulse v1.5.4B — Worldwide Publisher Network

## Installation (patch to working v1.5.4A)

1. Replace **`scripts/update.py`** with this ZIP's version.
2. Add **`scripts/publisher_network.py`** beside `update.py`.
3. Optionally add **`tests/test_publisher_network.py`**.
4. **Do not replace or rename `.github/workflows/update.yml`**. Your existing workflow still calls `scripts/run_all.py`, which imports and runs the updated collector. Its existing push retry is preserved.
5. Keep your live `data/*.json`, GeoNames resolver, and website files unchanged.
6. Commit the changes and start a **new** Actions → Refresh geographic news run. Check that the log says `WorldPulse v1.5.4B` and succeeds.
7. Open `data/data-health.json` and inspect `publisher_network_contributions` and `coverage_overview`.

## Scope

- Keeps **88 regional Google News searches** and the existing independent feeds.
- Adds a registry of **18 candidate public publisher RSS/Atom feeds**. The merge process skips an existing URL so the effective increase may be lower (RNZ Pacific is already configured).
- Feeds cover multiple editorial regions and several languages; titles are not translated by the collector.
- Records direct-only URL contributions, Google-only URL contributions, overlap and direct-feed sources. These are **URL-based approximations**, not verified story-level novelty. Google RSS redirect URLs mean overlap is generally underestimated.
- Provides country-labelled articles and distinct geolocated centers; this is not continent-wide coverage measurement yet.
- The current geocoder still cannot interpret every language, and no feed location is used as the location of an article. Uncertain articles remain unmapped.

## Data quality and licensing

Only headline/title, timestamp, limited summary metadata, publisher name and article link are collected. Never scrape full publisher article bodies. Publisher RSS availability and permissions can change. Failed candidates are recorded in feed diagnostics and do not stop the pipeline while other sources work. Follow article links to read the full work at its publisher.

## Known risks

- Several candidate URLs may be stale, blocked, malformed or have no articles in the past 24 hours. Their inclusion isn't proof of working coverage.
- The existing collector uses synchronous feed requests, so more feeds lengthen the run. Existing GitHub workflow timeout applies.
- Higher volume is not evidence of accuracy. Compare successful feeds, distinct mapped articles, place-level matches and source contributions after the new run.
