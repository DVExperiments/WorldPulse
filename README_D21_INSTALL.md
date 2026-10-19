# WorldPulse v2.4D.21 — Geographic Evidence Review & Correction Readiness

This **shadow-only** patch does not activate live filtering. Upload all included files to their matching repo folders; `scripts/update.py` is a complete replacement and `scripts/geo_readiness_d21.py` is new. Keep all other historical scripts, including `geo_review_d20.py`.

The evidence file has three matched Google News RSS URLs and original publisher URLs. Original publisher pages were read on 19 October 2026, and an **AI-assisted** source evidence summary is provided. These are NOT authenticated human approvals and do NOT populate `data/d20-review-evidence.json` or D18 live approval manifests.

After GitHub Actions `Refresh geographic news`, view `data/feed-contribution-audit.json` -> `d21_geographic_correction_readiness`. The D21 queue is intentionally present **within the audit**, so no extra workflow commit settings are required. `data/d21-source-evidence.json` must be uploaded as part of this patch. Later editing of this evidence file alone must not enable any corrections.

Live activation is NO-GO until signed human review, completely reconstructed signal history, story-cluster and cross-border dependents, and full published metrics have passed production-shaped tests. A source's article content can change after review, so re-validate exact URLs at activation.
