# WorldPulse v2.4D.13 — Multilingual Geographic Evidence Recovery

## GitHub direct upload

Upload **both** Python files, keeping these paths:

- `scripts/update.py` — REPLACE the existing file.
- `scripts/geo_recovery_d13.py` — ADD this file.
- `tests/test_d13_recovery.py` — ADD this file.

Retain all earlier `scripts/` modules, `data/` assets and previous tests. Do not delete existing files; do not edit `.github/workflows/update.yml`.

Run **Actions → Refresh geographic news → Run workflow**. Then inspect `data/feed-contribution-audit.json` → `d13_multilingual_recovery`.

## What is new

- Global audit, not Vietnam-only: runs for every selected location.
- Accented and translated aliases for a curated set of countries.
- Manually curated, high-confidence locality-to-country cases (for example Con Dao → Vietnam); not an exhaustive worldwide gazetteer and **not** automatic geocoding.
- Three recovery evidence outcomes: independent headline match, cleaned-description match, or still unsupported.
- `affected_only_recovery_class_counts` shows recovery among cases which D.12 shadow comparison loses or changes.
- Round-robin sampling gives other affected locations room alongside Vietnam, up to four examples per place (maximum 120 total).

## Safety

This is **shadow-only**. Existing globe locations are unchanged. The audit cannot prove event location from place-name mentions. D.13 alias and parent evidence are not inserted into the live geographic matcher, and no publisher edition/URL is treated as event evidence. The D.12 candidate comparison does not fully replicate live guardrails; confirm samples before enabling cleaned matching.

## Tests

`python -m pytest -q tests/test_d13_recovery.py`

The test file checks country aliases, accents, parent localities, publisher contamination avoidance, and geographic sample balance. No third-party Python dependencies added.
