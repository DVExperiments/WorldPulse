# WorldPulse v2.0E.2 — Geographic Decision Correction

**Repository:** `DVExperiments/WorldPulse` (original collector), **not** `WorldPulse-2`.

## Purpose

The new `geo_decision.py` reviews mapped feed occurrences. A description-based geographic selection is replaced only when a *single, unambiguous place name in the headline* matches a reviewed v2.0E catalogue entry and differs from the selected place. Existing headline-based mapping remains untouched. Headlines containing multiple reviewed places do not trigger a replacement. No country is inferred from publisher, Google edition, or URL.

The two confirmed E.1 audit examples are covered by regression tests:
- Bihar government policy incorrectly anchored to Patna -> Bihar regional geographic subject.
- French-language `Cisjordanie occupée` (West Bank) incorrectly anchored to Israel -> West Bank geographic subject.

The updated place is a geographic **subject**, **not a verified incident location**. This is a conservative matching correction, not full fact verification. This version does not generally suppress uncertain pins; it leaves them unchanged and reports reasons for abstaining. Review correction examples after running.

## Upload via GitHub

1. Extract this ZIP locally.
2. Upload the *two* files from `scripts/` (`geo_decision.py`, `apply_e2_patch.py`) to the **existing** `scripts/` directory in the original repository.
3. Upload `tests/test_e2.py` to the existing `tests/` directory. Commit the uploaded files.
4. Open Codespaces for `DVExperiments/WorldPulse` and run:

```bash
git pull origin main
python scripts/apply_e2_patch.py
python -m py_compile scripts/update.py scripts/geo_decision.py
python -m unittest discover -s tests -p 'test_e2.py' -v
GIT_PAGER=cat git diff -- scripts/update.py
```

5. If checks pass:

```bash
git add scripts/update.py
git commit -m "Add v2.0E.2 geographic decision corrections"
git push origin main
```

6. Open GitHub **Actions > Refresh geographic news > Run workflow**.
7. Inspect `data/unmatched-review.json` -> `geo_decision_corrections` (`counts` and `examples`). You can upload that JSON here for interpretation.

## Design and safety

- The installer is fail-closed if expected source anchors are missing, and safe to rerun.
- All prior matchers, data shapes and frontend rendering remain unchanged.
- `geo_accuracy_audit` still runs and reports corrected records.
- `geo_decision_corrections` is embedded in an existing workflow-committed JSON file; no workflow change is required.
- Counters record feed *occurrences* (not distinct stories). This patch does not assert an accuracy rate or automatically alter all uncertain assignments.
