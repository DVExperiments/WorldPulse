# WorldPulse v2.4D.4 — Geographic Matching Recovery & Feed Efficiency

Incremental collector update built on the v2.4D.3 `scripts/update.py`. Keep your existing GitHub Actions `update.yml` (including the `data/feed-contribution-audit.json` commit path) and all front-end files.

## Upload to repository root

1. `scripts/update.py` — replace existing
2. `scripts/geo_recovery_d4.py` — add new
3. `tests/test_d4_recovery_efficiency.py` — add optional offline test

Do not upload these into a nested folder under the repository. GitHub Actions workflow **Refresh geographic news** then regenerates `data/feed-contribution-audit.json`.

## Changes

- **Conservative recovery:** only explicitly qualified references (for instance `en México`, `no Brasil`) from a small curated multilingual phrase list. Targets must already exist as a *unique country* in the project's `data/places.json` / `places-extra.json`. Existing geography disambiguation still evaluates candidates; uncertain and multi-country headline matches are not recovered.
- **Unmatched diagnosis:** audit contains category counts for unmatched rows and examples of recovered records. No full unbounded article archive is created.
- **Feed efficiency:** audit reports canonical URL duplicate losses, near-title duplicate losses, and which feed first retained a duplicate. Attribution is affected by feed ordering and date sort; this is diagnostic, not a ranking of publisher reliability.
- **Non-destructive:** no feeds disabled, no guessed incident coordinates, no website UI or schedule changes.

## Verification

From the repository root:

`python tests/test_d4_recovery_efficiency.py`

`python tests/test_d3_pipeline_audit.py` (if the earlier test remains in repository)

After the GitHub action finishes, check `data/feed-contribution-audit.json` for `release: v2.4D.4`, `d4_recovery`, and `d4_efficiency` fields.

## Limitations

Only a small targeted set of multilingual country phrases is recovered, and only if the country is present and uniquely recognized in the gazetteer. The improvement may produce zero new recovered entries on some runs. Offline tests use representative examples and do not validate the actual live feeds; compare live audit counts before drawing conclusions about improvement. `globe_articles` represents a serialization cap of 20 per location/category. Aggregate duplicate-loss attribution should not be interpreted as an independent measure of feed usefulness.
