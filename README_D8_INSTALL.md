# WorldPulse v2.4D.8 — Geographic Subject Resolution & Ambiguity Hardening

## GitHub direct upload
Upload these files at the specified relative paths:

- `scripts/update.py` — replace existing
- `scripts/geo_subject_d8.py` — new
- `tests/test_d8_subject.py` — new
- `tests/test_d7_semantic.py` — update existing regression test's version assertion

**Do not delete or replace other collector modules.** Keep `.github/workflows/update.yml` unchanged; the feed contribution audit is already committed by the current workflow.

Run **Refresh geographic news** under Actions, then inspect `data/feed-contribution-audit.json` > `d8_geographic_subject`.

## Behaviour and limits

- Adds review-only headline-country detection for a bounded alias dictionary; mentions never create new mapped positions.
- Withholds narrow `Anand` person-name collisions and unsupported `Paraná` assignments for Russia-focused headlines, unless local-place language supports Paraná.
- Preserves explicit locality such as `in Paraná`, `in Anand`, `near Sparks` and nested Mexico/Toluca cases.
- Marks multi-country headlines for review rather than selecting a primary event location.
- Preserves D.3–D.7 audit sections.
- This is not full semantic role labeling: it cannot reliably determine country roles or verify event locations without article evidence.

## Local regression tests

`python tests/test_d8_subject.py`

`python tests/test_d7_semantic.py`

The tests are offline; a live GitHub Actions run is still required.
