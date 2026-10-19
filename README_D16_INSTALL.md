# WorldPulse v2.4D.16 — Targeted Geographic Correction Trials & Precision Benchmarking

This is a **shadow-only** patch. It does not modify article pinning, matching, deduplication, or the globe UI.

Upload these files at the repository root, preserving folders:

- `scripts/update.py` — replace
- `scripts/geo_trials_d16.py` — add
- `tests/test_d16_trials.py` — add
- `README_D16_INSTALL.md` — optional

**Keep all previous scripts**, including `geo_semantic_d15.py`, `geo_hierarchy_d14.py`, `geo_recovery_d13.py`, and `geo_integrity_d12.py`. No change to `.github/workflows/update.yml`.

Run GitHub Actions > **Refresh geographic news**, then read `data/feed-contribution-audit.json` section `d16_targeted_correction_trials`.

The trial reports candidate retains, review-only withholds, review-only relocations, and deduplicated URL/location counts. Benchmark cases are **curated synthetic regressions**, *not* measured production accuracy. A hypothetical review-only withholding should not be treated as a confirmed false positive or proof of a desirable reduction in coverage. Do not enable these interventions until independent real-world labelled testing supports them.
