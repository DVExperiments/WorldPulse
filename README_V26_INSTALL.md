# WorldPulse v2.6.0 — Accuracy & Quality Release

Direct-upload patch: keep ALL earlier modules, `data/` files, `scripts/archive_news.py`, and live HTML/CSS/JS. Upload the files here to matching repository paths; replace `scripts/update.py`, `quality.html`, `.github/workflows/update.yml`.

## Improvements
1. Narrow **live** suppressions for two independently source-checked Spanish-language homonym patterns: *reunión interparlamentaria* wrongly mapped to Réunion Island; *lagos ... Chile* wrongly mapped to Lagos Nigeria. No relocation or inferred replacement coordinate. Preserves browse-only records. Conservative boundary and explicit island/Nigeria exemptions.
2. New `quality-v26.json` audit tracks suppressed articles, publisher concentration and cross-location URL reuse. Multiple-location articles are only flagged; not blindly deleted.
3. Bounded `quality-history-v26.json` of up to 96 recent refreshes, driving comparative rows in `quality.html`.
4. Existing v2.5 shadow integrity, D.21 evidence and geographic correction activation locks remain in place.
5. New tests for negative controls, canonical URL review, and reporting.

## Validation and limitations
Tests are offline fixtures: require a successful GitHub Actions refresh and inspect `data/feed-contribution-audit.json`, `data/quality-v26.json`, `data/quality-history-v26.json` and `quality.html`. This release does **not** deliver a fully labelled global precision/recall benchmark, new verified feeds or multilingual semantic clustering. Existing source diversity is still a problem. New rules apply only to narrow known errors; do not assume zero false positives globally. Read the quality report before widening them. Publisher-geography and live D18 correction activation remain disabled.

Workflow commit step includes new quality report files. Archive collection pipeline otherwise unchanged.
