# WorldPulse v2.0E.4 — Collector evidence fields

This is an additive update for the **original `DVExperiments/WorldPulse` collector**, after E.3. It publishes per-article geographic evidence in `data/news.json` under each `points[].articles[]` record. Globe locations do not change.

1. Upload `scripts/geo_public_evidence.py`, `scripts/apply_e4_patch.py` and `tests/test_e4.py` into the original collector repository. Commit.
2. In Codespaces: `git pull origin main`; `python scripts/apply_e4_patch.py`; `python -m py_compile scripts/update.py scripts/geo_public_evidence.py`; `python -m unittest discover -s tests -p 'test_e4.py' -v`.
3. `git add scripts/update.py && git commit -m "Add E4 article-level geographic evidence" && git push origin main`.
4. Run the existing `Refresh geographic news` GitHub Action and inspect `data/news.json`.

Evidence is explanatory, NOT an actual calibrated probability or verified incident coordinate. The E.3 audit may classify individual matches as ambiguous or context-based; no retroactive event verification occurs.
