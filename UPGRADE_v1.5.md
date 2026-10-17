# WorldPulse v1.5 — Global Data Network (first deployable milestone)

This upgrade extends v1.4A.2 without changing the globe's existing news schema.

## What's included

- Expanded Google News editions: US, GB, IN, AU, ZA, NG, PH and CA. Each of the eleven categories now runs in eight editions (88 regional searches) plus 23 independently configured direct feeds = 111 configured news requests.
- `scripts/run_all.py`: an orchestrator with independent news and official-event adapter execution.
- `scripts/events.py`: an independent USGS earthquake events 24-hour adapter; events are not news articles and are not included in article counts.
- A switchable **Recorded events** layer in the 3D viewer. Click a marker to access its USGS event detail page.
- Regional source-success and pre-deduplication coverage diagnostics in Data Health.
- Existing retry-on-conflict GitHub workflow retained, with new event output staged for commit.

## Installation

Preserve all current `data/*.json` files except that you may add the new `data/events.json` placeholder. Replace only:

- `scripts/update.py`
- `scripts/run_all.py` (new)
- `scripts/events.py` (new)
- `app.js`
- `index.html`
- `.github/workflows/update.yml` (replace the *contents* of the existing file; don't add a second workflow)
- `data/events.json` (new if missing)

Commit those files to `main` and run **Actions > Refresh geographic news > Run workflow** (new run, not retry of older run).

## Important limitations

- Google News results are sampled, not an exhaustive count of world journalism. Expanded editions may return overlapping articles. Success and mapped counts should be evaluated after a live run.
- `news.json` contains geographically matched mentions, which are not verified event sites. `events.json` contains reported earthquake coordinates from USGS and is separate.
- The event layer contains *earthquakes only*. This release does not yet integrate conflict-event datasets, other natural hazards, GDELT bulk files, or Media Cloud. These need further source-specific testing, license/access review, and mapping-quality gates before production.
- Translation continues to depend on optional browser support. Other publisher RSS feed problems may remain.
- If the USGS adapter fails, the existing `events.json` is retained and can be stale. News collection remains independent.
- Do not upload any bundled older or empty `news.json` over your live snapshot.
