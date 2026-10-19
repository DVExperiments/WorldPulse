# WorldPulse v2.4D.14 — Global Geographic Hierarchy & Contradiction Analysis (SHADOW)

## Install in the existing GitHub Pages repository

Upload these files *at the indicated paths* (upload file contents into scripts/ and tests/, not a folder containing those folders):

- `scripts/update.py` — replace existing.
- `scripts/geo_hierarchy_d14.py` — add new.
- `tests/test_d14_hierarchy.py` — add new.
- `README_D14_INSTALL.md` — optional.

**Keep** all D.4–D.13 modules and the existing `data/places*.json` files. Do not change `.github/workflows/update.yml`.

Run Actions → **Refresh geographic news** → Run workflow. The next `data/feed-contribution-audit.json` should have `release: v2.4D.14` and a `d14_global_hierarchy_contradictions` section.

## Scope and safeguards

- No live location assignment, pin, deduplication, or collection filter is changed by D.14.
- Uses independent headline + D.12-cleaned description evidence; does not infer from publisher URL or feed edition.
- Curated parent-country relationships cover dozens of geographically distributed countries with examples; they are **not** a complete worldwide gazetteer. The matching rules intentionally favour qualified/recognisable place names.
- A foreign country in a headline is not a verified contradiction: comparison, diplomacy, trade, and multi-country reporting can mention other countries legitimately. All `potential_headline_country_contradiction` records require review.
- The new report is over unique `(URL, selected_place)` pairs and balances samples across locations.
- The report is diagnostic only; not sufficient to enable D.12 publisher stripping as the live matching input.

## Review priorities

Look for `classification_counts`, `review_counts_by_place`, and `balanced_review_samples` under `d14_global_hierarchy_contradictions`. Review explicit contradiction candidates before considering changed matching policy.

## Local smoke check

With the complete project and Python installed:

`python -m unittest discover -s tests -p 'test_d14_hierarchy.py'`

`python -m py_compile scripts/update.py scripts/geo_hierarchy_d14.py`
