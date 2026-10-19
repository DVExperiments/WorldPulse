# WorldPulse v2.4D.7 — False Positive Suppression & Semantic Geographic Context

## Upload to the existing WorldPulse repository
- Replace `scripts/update.py`.
- Add `scripts/geo_semantic_d7.py`.
- Add `tests/test_d7_semantic.py`.

Keep all existing files, particularly scripts/geo_accuracy_d6.py, scripts/geo_evidence_d5.py and scripts/geo_recovery_d4.py. Do not change `.github/workflows/update.yml`.

Run **Refresh geographic news** under GitHub Actions. Then inspect `data/feed-contribution-audit.json` > `d7_semantic_accuracy` for counts, blocked article samples, and review samples.

## Scope and safeguards
This is deliberately a narrow false-positive patch, not general semantic geocoding. It suppresses exact contextual false matches such as ordinary Portuguese `liberdade`, English `sparks outrage`, `reading scores`, and `mobile phones`; geographic uses such as `in Sparks` are not blocked by those lexical rules. Suspected headline versus selected-place disagreements are **review only** unless the existing D6 blocker has already withheld the row. No feed is removed. No coordinate is created or changed. Multi-place headline contexts are inspected but not auto-relocated.

The implementation needs a live GitHub Actions run to validate full integration; offline tests only validate local rule outcomes and collector syntax. D6 release-specific test may require updating its strict version assertion (it checks for literal v2.4D.6, which is now v2.4D.7); do NOT overwrite historical tests simply to make that assertion pass.
