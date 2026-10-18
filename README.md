# WorldPulse 2.0D.3 — Geographic Mapping Precision (first-pass repair)

**Upload into `DVExperiments/WorldPulse` (original collector), NOT `WorldPulse-2`.**

## Purpose

The source-health results show numerous functioning feeds with low / zero mapped stories. This conservative improvement tries a second geography pass only when the existing resolver fails. It does not use the publisher's location, article language, or the news edition as a fake story location.

### What's added

- Unicode/diacritic-insensitive explicit place detection; for example Whangārei vs Whangarei
- Candidate names are checked for duplicates, with ambiguous short/generic labels suppressed
- Strict URL geography-path fallback only for explicit `/city/auckland`, `/country/france` etc.
- Existing `locate()` remains primary; news and geographic points retain their existing shape
- Unit tests for positive and negative mapping cases

This is a focused accuracy enhancement, **not a full solution** for zero-mapping feeds. Some articles have no explicit geographic subject in the metadata, and those must stay unmapped. Additional work is needed to compare unmatched samples and add verified context handling.

## Installation (browser-only, without replacing update.py)

1. Open the **original** `WorldPulse` GitHub repository and upload `scripts/geo_mapping_enhancements.py`, `scripts/apply_geo_patch.py`, and `tests/test_geo_mapping_enhancements.py` into the matching folders. Do not upload into WorldPulse-2.
2. Open the original repo's existing GitHub Codespace (Code → Codespaces).
3. In its terminal run: `python scripts/apply_geo_patch.py`
4. Check the result. The script modifies the existing `scripts/update.py` **in place**, retaining the rest of your pipeline. It aborts if the expected insertion point isn't found, and is safe to run twice.
5. In the Codespace Source Control panel, commit/push `scripts/update.py` (plus any uploaded files not yet committed). If files were already uploaded and committed, `update.py` may be the only uncommitted change.
6. Wait for the normal news workflow. The existing `.github/workflows/update.yml` is **not changed**.

## Verification

Run optional tests: `python -m unittest discover -s tests -p 'test_geo_mapping_enhancements.py'`

Check subsequent `data/source-health.json`, `data/data-health.json`, and `data/unmatched-review.json`. The first patch may recover some place mentions but does not guarantee large gains. Continue to distinguish publisher country from the geographic subject of the story.

## Revert

If the collector fails, use GitHub's revert of the commit containing the code changes. Or remove the import and the two-line `find_explicit` fallback from `scripts/update.py`.
