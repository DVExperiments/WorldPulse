# WorldPulse v2.0E.1 — Geographic Accuracy Audit

**For the ORIGINAL `DVExperiments/WorldPulse` repository only.** Not `WorldPulse-2`.

This is a diagnostic-first collector patch. It does **not** change the geographic matching algorithm or move/remove any globe pins. It highlights cases worth human review, with an intentionally incomplete screening catalogue from E's 158 reviewed geographic entries. Flags do not prove a mapping is wrong. The geographic subject is **not** a verified event location.

## Files to upload
- `scripts/geo_accuracy_audit.py` — zero-dependency accuracy auditor
- `scripts/apply_e1_patch.py` — safe installer for the existing v2.0E collector
- `tests/test_e1.py` — nine regression tests

Do **not** upload or overwrite `scripts/update.py` from another version; the installer updates your currently deployed file in place.

## Installation
1. Extract ZIP. Upload `geo_accuracy_audit.py` and `apply_e1_patch.py` to **original WorldPulse** repo's `scripts/` folder, and `test_e1.py` into `tests/`. Commit the uploads through GitHub.
2. Open the original WorldPulse Codespace, and run:

```bash
git pull origin main
python scripts/apply_e1_patch.py
python -m py_compile scripts/update.py scripts/geo_accuracy_audit.py
python -m unittest discover -s tests -p 'test_e1.py' -v
GIT_PAGER=cat git diff -- scripts/update.py
```

3. If successful:

```bash
git add scripts/update.py
git commit -m "Add v2.0E.1 geographic accuracy diagnostics"
git push origin main
```

4. Manually run **Refresh geographic news** via GitHub Actions for the **original** repository.
5. Inspect `data/unmatched-review.json` -> **`geo_accuracy_audit`**. Send that file for review.

## Diagnostics
- `risk_bands`: `low`, `watch`, `review_priority`, counted per eligible mapped *feed occurrence* (not distinct stories)
- `risk_flags`: `description_only_selection`, `url_path_selection`, `multiple_reviewed_headline_places`, `multiple_reviewed_description_places`, `description_overrides_named_headline_place`, `not_independently_confirmed_by_e_catalogue`
- `review_examples`: up to 45 examples needing attention, including chosen location, match method, title and reviewed place hints

The full diagnostic is additionally saved as `data/geo-accuracy-audit.json` during the workflow, but **only the embedded version** in the already-committed `data/unmatched-review.json` is guaranteed to persist under the current GitHub Actions workflow. No workflow changes required.

## Limitations and next steps
The 158-entry reviewed catalogue is used as a *screening* list, not a complete gazetteer. Thus a flag such as `not_independently_confirmed_by_e_catalogue` is expected for many legitimate matches and must not be treated as a definite error. This release creates evidence for a later precision refactor without risking the currently working globe.

Tested against a locally reconstructed v2.0E collector, not the live GitHub repository. Nine tests passed; syntax and repeat-installation checks passed. Verify workflow results after deployment.
