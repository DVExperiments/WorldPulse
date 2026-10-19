# WorldPulse v2.4D.5 — Geographic Evidence & Regional Coverage Intelligence

Incremental collector update from the working v2.4D.4 build. This release adds *audit-only* evidence diagnostics. No automatic feed disabling, no changed geolocation acceptance, no new place pins, no frontend changes, and no changes to GitHub Actions scheduling.

## Upload to the repository root

1. `scripts/update.py` — replace existing.
2. `scripts/geo_evidence_d5.py` — NEW file.
3. `tests/test_d5_geo_evidence.py` — NEW, optional offline test.

Keep the existing `scripts/geo_recovery_d4.py` and all other original source files. **Do not delete them.** Keep `.github/workflows/update.yml` unchanged; it already commits `data/feed-contribution-audit.json` from v2.4D.3.

Open GitHub → Actions → Refresh geographic news → Run workflow. Confirm the refreshed `data/feed-contribution-audit.json` includes `"release": "v2.4D.5"` and `"d5_geographic_evidence"`.

## New audit fields

`d5_geographic_evidence` contains:

- `mapped_by_literal_evidence`: a trace separating literal matched names in headline vs description vs contextual/alias matches. The categories are *not* calibrated probabilities or proof of event location.
- `mapped_by_method`, `mapped_by_place_level`, `mapped_by_place_top`, `globe_by_place_top`, and `mapped_by_hemisphere`.
- `discovery_edition_vs_actual_match`: geographic subject matches are counted independently from the Google News edition or publisher's configured editorial region. An edition is **not** evidence of an event's location.
- `edition_to_country_subject_top`: observed feed-edition / matched-country pair counts, for analysis only.
- `unmatched_diagnostic_counts`, `unmatched_multi_country_rows`, and `unmatched_language_candidate_examples`: bounded review suggestions for selected country names in Spanish, Portuguese, German, French and English. **These never produce pins.**
- `matched_literal_evidence_examples` and `matched_contextual_review_examples`: bounded sample headlines to inspect matcher quality.
- `limitations`: explanation of precision and counting caveats.

This release is **coverage intelligence and evidence analysis, not a mass match expansion**. Country aliases in the review dictionary do not trigger automated mapping. Before adding any new mapping rules later, manually inspect candidates, test ambiguous place names, and confirm region coverage over multiple runs.

## Verify locally (optional)

From the repository root:

```
python tests/test_d5_geo_evidence.py
python tests/test_d4_recovery_efficiency.py
python tests/test_d3_pipeline_audit.py
```

Tests passed offline on the packaged files. A live GitHub Actions run is still required to verify real-world output. The output report uses per-feed mapped rows before deduplication for many diagnostic counts; `globe_serialized_articles` reflects the 20-article-per-location/category display cap. Neither measure is a worldwide news census.
