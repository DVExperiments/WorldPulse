# WorldPulse v1.4A.1 — Data Quality Patch

This patch is based on the v1.4A collector + the **working 5-attempt push repair**. It does not include `data/news.json`, so your deployed globe stays populated during the upgrade.

## Apply to the existing GitHub repository

Replace `scripts/update.py`, `app.js`, `index.html`, and `.github/workflows/update.yml`. Add the initial `data/data-health.json` and `data/article-history.json`. Do not delete or replace `data/news.json`, `data/places.json`, `data/history.json`, `data/source-health.json`, or `style.css`.

**Important:** Only keep the existing `update.yml` workflow. Start a *new* workflow via Actions → Refresh geographic news → Run workflow, not Re-run jobs on an old run.

## Changes

- 11 topic identifiers: politics, environment, hazards, economy, science, conflict, health, education, rights, community and legacy society. New health/education/rights/community segments replace the broad society query. Legacy society remains supported on old snapshots.
- Searches expand from 28 to 44 regional Google News requests, plus 23 direct RSS feeds. Success varies by provider and language; no coverage guarantees.
- Place names in descriptions are used when none are found in the headline; `geo_match` records which field matched. Country points remain representative anchors. Multiple competing locations are not resolved into a verified event site.
- Data Health view shows feed availability, counted place precision, unmapped examples count, and topic mix.
- `article-history.json` keeps *up to 6,000* sampled article URLs over 30 days, suitable for later story-tracking research but not a full archive. Article history is populated from the up-to-20 preview article links per marker, so not every mapped article enters the archive.
- `data-health.json` lists a bounded sample of 35 unmapped headlines plus aggregations.
- Cluster bins are separated by topic. Category filters continue to work and can be toggled independently.

## Caveats

Not a verified event geocoder; description mentions can refer to background context rather than the event's actual location. Deduplication is approximate, especially across different languages. Article counts and topic velocity are RSS samples, not universal news totals. Browser translation is experimental. Regional continent coverage and broken-feed repair have NOT been implemented in this patch; the health view is intended to measure where to prioritize those improvements.

## Tests

`python -m py_compile scripts/update.py` and `node --check app.js`; local tests exercise description matching, broad category matching and aggregations. Live RSS retrieval must be confirmed on GitHub Actions.
