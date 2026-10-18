# WorldPulse v2.0E.3 — Geographic Confidence Refinement

**Original repository only:** `DVExperiments/WorldPulse`, not `WorldPulse-2`.

This diagnostic-only update adds `geo_confidence_evidence` to the already committed `data/unmatched-review.json` (no workflow changes). It classifies mapped feed occurrences as `explicit_headline`, `description_context`, `conflicting_evidence`, `ambiguous_headline`, `url_context`, or `other_heuristic`. These are evidence categories, **not verified probabilities of correctness**. Missing entries in the small reviewed catalogue are separately counted, not misrepresented as weak matches. No map pins are moved, added, or removed. It does not claim verified incident locations.

## Install
1. Upload `scripts/geo_confidence.py` and `scripts/apply_e3_patch.py` and `tests/test_e3.py` into the same folders in the **original** repo, then commit the uploaded files in GitHub.
2. In the original WorldPulse Codespace:

```bash
git pull origin main
python scripts/apply_e3_patch.py
python -m py_compile scripts/update.py scripts/geo_confidence.py
python -m unittest discover -s tests -p 'test_e3.py' -v
GIT_PAGER=cat git diff -- scripts/update.py
```

3. If successful:

```bash
git add scripts/update.py
git commit -m "Add v2.0E.3 geographic evidence diagnostics"
git push origin main
```

4. GitHub Actions > **Refresh geographic news** > Run workflow on main. Upload `data/unmatched-review.json` afterwards.

**Requirements:** E.2 already installed; the patch deliberately stops if the expected anchors differ, to avoid corrupting customized collectors. The previous E.1 report is retained alongside the new report for comparison. Categories are method-derived; they are not externally ground-truthed. Where headlines contain several places, review flags are not proof the chosen one is wrong.
