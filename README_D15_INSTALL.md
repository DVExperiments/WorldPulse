# WorldPulse v2.4D.15 — Semantic Place Disambiguation & Hierarchy-Aware Validation

**Mode: shadow-only.** No article pins, collection criteria, feed configuration or GitHub Action schedule are changed.

## Direct GitHub upload

Upload at the repository root, respecting paths:

- `scripts/update.py` — replace current file
- `scripts/geo_semantic_d15.py` — add
- `tests/test_d15_semantic.py` — add
- `README_D15_INSTALL.md` — optional

Keep all files from D.4–D.14, including `scripts/geo_hierarchy_d14.py` and `scripts/geo_recovery_d13.py`. Do **not** change `.github/workflows/update.yml`.

Run **Actions → Refresh geographic news → Run workflow**. Inspect `data/feed-contribution-audit.json` → `d15_semantic_hierarchy_validation` and send the updated audit for interpretation.

## Scope and limitations

D.15 reclassifies D.14 findings with a small explicit set of city/region-to-country relationships, targeted ordinary-word collision clues, and review-only contradictions. It compares D.14 classifications with D.15 findings. It does **not** verify the actual location of an incident, independently verify every parent relationship, or automatically correct pins. A country name in a headline might be an actor rather than the event site. Pattern matches for common-word collisions are review signals, not confirmed errors. The module deliberately avoids heavy NLP and external services.

Offline tests: `python -m unittest discover -s tests -p 'test_d15_semantic.py' -v` (from repository root).
