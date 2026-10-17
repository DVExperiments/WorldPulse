# WorldPulse v1.5.1 — Collection Intelligence

Targeted patch for the deployed v1.5 project. Does not replace existing snapshots.

## Install

- Replace `scripts/update.py`, `app.js`, and the **contents** of your only existing `.github/workflows/update.yml`.
- Add `data/unmatched-review.json` (initial placeholder; collection generates it).
- Do not delete `data/news.json`, `data/history.json`, `data/data-health.json`, `data/source-health.json`, `data/events.json`, or `data/article-history.json`.
- Commit these changes to `main`, and from the Actions page use **Run workflow** to start a *new* run (not Re-run jobs on an old run).

## Changes

- 8 **additional independent regional RSS feed configurations**: BBC Africa, Asia, Latin America, Middle East and Europe; RNZ Pacific; Guardian Africa and Asia. Each feed is best-effort. Failure does not interrupt the remaining news sources. Some articles will overlap and be deduplicated.
- Keeps the existing 88 Google News regional queries, and retains existing 23 direct sources. Now **119 configured searches/feeds**, not a verified count of active sources.
- New `data/unmatched-review.json`: bounded, ranked audit of 120 distinct unmatched headlines and links to help diagnose geography blind spots. It does not infer locations for headlines that lack reliable matches.
- Data Health gains a direct-publisher contribution metric and a linkable unmatched-audit filename. Pre-deduplication counts are not unique articles.
- Existing high-confidence versus country-level place labels and the USGS event layer are preserved.
- The original 5-attempt GitHub push retry remains intact; only `data/unmatched-review.json` has been appended to the commit list.

## Accuracy limitations

This is an incremental collector improvement. It does NOT implement comprehensive multilingual named-entity recognition, publisher-syndication lineage, verified event geocoding or an event-clustering engine. Geographic mentions are contextual. The experimental feed endpoints and geographic performance require a live Actions run. A count of 119 requests is not 119 independent editorial sources.

## Verify

Confirm the newest run logs state `WorldPulse v1.5.1` and the commit step succeeds. Check that `data/unmatched-review.json` is populated, and use the Data Health panel to compare the direct-publisher success/mapping rate and distinct mapped articles with the v1.5 baseline (374 mapped articles, 140 place matches, 1409 unmapped entries). No increase is guaranteed.
