# WorldPulse v1.4A.2 — Geographic Intelligence & Coverage Diagnostics

This is an **additive patch** to an existing working WorldPulse v1.4A.1 site. Keep the original `.github/workflows/update.yml` untouched; the working five-retry commit step already stages `data/news.json`, `data/history.json`, `data/source-health.json`, `data/article-history.json`, and `data/data-health.json`. Our new `data/places-extra.json` is static and must be committed once manually.

## Install

Upload these files into the same paths in your existing GitHub repo:
- Replace `scripts/update.py`
- Replace `app.js`
- Replace `index.html`
- **Add** `data/places-extra.json`

Do not upload a second workflow, do not replace any other data files or the existing push-retry workflow.

After committing these files, go to **Actions → Refresh geographic news → Run workflow** (start a *new* run, not re-run an old job). Inspect `data/data-health.json`, the website's Data Health view, and whether markers are distributed more broadly. Compare samples with caution: total RSS coverage and category changes affect counts.

## What's changed

- Enlarged local gazetteer with 715 additional named places, including regional cities in Africa, Asia, the Americas, Europe, and Oceania. Existing `data/places.json` remains unchanged.
- Curated multilingual spelling variants (e.g. Kyiv/Kiev). Case-independent word boundaries; some ambiguous place names are suppressed to reduce false positive pins.
- Data Health: distinct unmapped headline count, top unmapped feeds, geographic quadrant breakdown and total gazetteer size.
- Keeps headline-over-description matching, publisher deduplication, categories, three-hour sample velocity, source health, and thirty-day article records from 1.4A.1.

## Important limits

The 1,094-entry database is **not exhaustive**. A name in a headline or summary is a location *mention*, not verified where the event happened. Country coordinates are representative markers (often capitals) rather than event locations. Source feeds may reject automated requests. A larger gazetteer can also increase incidental matches: examine sampled links and diagnostics rather than treating an increase in pins as proof of improved accuracy.

The geographic quadrant counts are literal latitude/longitude quadrants (NE, NW, SE, SW), **not continents**. Unmapped entry counts can include duplicates and expired records. This upgrade does not introduce unverified automatic geocoding or claim global census-quality article counts.

### Testing

Syntax checks: `python -m py_compile scripts/update.py` and `node --check app.js`.

Live feed and globe behavior must be verified by GitHub Actions and the browser after deployment.
