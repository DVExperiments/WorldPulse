# WorldPulse v2.4D.6 — Geographic Attribution Accuracy & Headline Priority

Collector-only direct upload. Built from the v2.4D.5 package.

## Files to upload
- `scripts/update.py` (replace)
- `scripts/geo_accuracy_d6.py` (new)
- `tests/test_d6_accuracy.py` (new)

Leave the existing `update.yml` and all other `scripts/` modules intact (including `geo_evidence_d5.py` and `geo_recovery_d4.py`).

## Behavior
D6 examines selected geography **after** the existing decision audit. It records explicit known-place mentions in headline and description separately. If precisely one recognizable headline place conflicts with the selected description-place, the article is **withheld** from the mapped globe rather than relocated or guessed. Multiple headline place names, ambiguous place/person words, and other disputes are logged for inspection only. No new geocoding aliases or inferred coordinates are introduced.

The next `data/feed-contribution-audit.json` will contain `d6_attribution_accuracy`. This audit is **diagnostic** and places mentioned in text are not verified event sites. Sample records are bounded and are limited to 2,500 selected-match decisions; counts reflect that sample ceiling if exceeded. It is possible that the published globe article count will decrease because questionable pins were withheld. Archive/other site systems are unchanged.

## Test
`python tests/test_d6_accuracy.py`

After uploading, use GitHub Actions > Refresh geographic news and inspect the audit output. Test only verified offline; live feed collection still requires running the action.
