# WorldPulse v2.5.0 — Integrated Intelligence Foundation

**Direct-upload patch for an existing working WorldPulse v2.4D.21 repository.** It is not a complete repository; retain all existing `scripts/` modules, `data/places*.json`, and news assets.

## What this changes together

1. Geographic correction *shadow only*: replay source-checked D.21 candidates against a deep copy of current signals, recompute uncapped local metrics, and rebuild the current pure story-cluster and cross-border functions in memory. Compare fingerprints and blocked groups. **No live corrections or human approvals.**
2. Source coverage: pre-dedup publisher concentration, location diversity, mapped/unmapped sample counts, successful-but-empty feeds and failed feeds.
3. Event-quality review: URLs represented at multiple geographic locations are flagged for human review, never removed automatically.
4. Reliability: observational snapshot consistency validation, bounded output, immutable-baseline checks, no extra network requests, no additional dependencies.
5. Accessible quality page: `quality.html` displays committed JSON directly on GitHub Pages.

## Installation

Upload every file in this ZIP preserving its relative path from the **repository root**:
- Replace `scripts/update.py`.
- Add `scripts/intelligence_v25.py`.
- Keep or replace `scripts/geo_review_d20.py` and `scripts/geo_readiness_d21.py` (included dependencies).
- Replace `.github/workflows/update.yml` (same existing schedule/steps; adds two JSON files to the *existing* commit allowlist).
- Add `quality.html` at repository root.
- Add `tests/test_v25_intelligence.py`; retain other tests.

Do not delete or overwrite `data/news.json` manually. If the GitHub workflow reports missing imports, preserve/restore all older modules from your working D.21 repo.

## Run

GitHub → Actions → **Refresh geographic news** → Run workflow. Then visit:
`https://dvexperiments.github.io/WorldPulse/quality.html`

Expected new committed reports:
- `data/quality-v25.json`
- `data/quality-validation-v25.json`

Also review `data/feed-contribution-audit.json` → `v25_shadow_consistency` and `v25_quality_dashboard`.

## Safety and boundaries

**D.21 live correction lock remains in force** (`d18_simulate(..., enabled=False)`). This release neither calls any paid APIs nor changes collection filters, feed counts, event placement, visual globe rendering, or history semantics. This is a substantial observational and shadow-testing integration, **not** an accuracy improvement already demonstrated on a labelled dataset. The downstream simulation excludes persisted story-history enrichment, article-history rewrites, feed attribution reconciliation, and signed human review; its gate remains **NO_GO_live_corrections**. The live news record is not changed by the shadow comparison.

`quality-validation-v25.json` is observational rather than a prepublication blocking gate. The quality dashboard does not replace the globe or independently fetch source websites.

## Local tests

`python -m unittest discover -s tests -p 'test_v25*.py' -v`

7 offline tests passed when packaged. A full live collector run requires all older repository modules and actual network feeds; it has not been performed inside this patch-only build environment.
