# WorldPulse v1.5.2 — Geographic Understanding

This patch upgrades the existing **v1.5.1** RSS collector's geographic matching. It does not change your news search count, event layer, frontend, or GitHub Actions workflow.

## Install

1. **Replace only** `scripts/update.py` in your working repository.
2. Optionally add `tests/test_geography.py` (recommended).
3. Keep `.github/workflows/update.yml` exactly as it is. Keep `data/news.json`, all live JSON snapshots and the place databases unchanged.
4. Commit to `main`, then start a **new** `Refresh geographic news` Actions run using the manual *Run workflow* command.
5. Check `data/news.json` `version` is `1.5.2` and `data/data-health.json` reports `contextual_alias_groups`.

## How it works

The collector adds curated phrase rules for explicit localities and contextual regional names found in the 2026-10-17 unmatched-headline audit, including HCM City, Macquarie Island, the Strait of Hormuz, Khyber Pakhtunkhwa, Kalispell and Iraqi Kurdistan.

Markers remain **geographic subjects**. The new fields `location_role: geographic_subject` and `event_location_verified: false` make that explicit for consumers of the JSON. Headline evidence remains preferred over description evidence. Short ambiguous terms do not become free-standing matches.

The direct feeds, 88 regional searches, history, source audit, USGS event layer, classification and deduplication pipeline are unchanged. This patch does not implement full multilingual named-entity recognition, extract event sites from full articles, or infer location from publisher address. It does not automatically map unrelated or vague stories.

## Test

From a full repository checkout with both `data/places.json` and `data/places-extra.json` available:

```bash
python -m unittest discover -s tests -v
```

No network access is required for these tests. The Actions collection itself still requires the usual RSS networks and must be verified after deployment.

## Monitoring

Compare to the most recent baseline: 346 mapped sampled articles, 124 specific-place matches, 449 distinct unmatched headlines, and 112/119 successful feeds. These figures can vary independently as the news cycle changes. Review sample article links for incorrect geographic placements as well as changes in counts.
