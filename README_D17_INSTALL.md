# WorldPulse v2.4D.17 — Controlled Semantic Correction Pilot (SHADOW)

This patch upgrades the D.16 collector without enabling ANY live geographic suppression or relocation. The `PILOT_ENABLED = False` constant in `geo_pilot_d17.py` is an informational safety lock, **not** a wired live switch. Changing it alone does not activate corrections.

## Direct-upload contents

- Replace `scripts/update.py`
- Add `scripts/geo_pilot_d17.py`
- Add `tests/test_d17_pilot.py`
- Optional `README_D17_INSTALL.md`

Retain D.4–D.16 scripts and all existing files. No changes to `.github/workflows/update.yml`.

Run the existing **Refresh geographic news** workflow in GitHub Actions. Read the new `d17_controlled_semantic_pilot` section in `data/feed-contribution-audit.json`.

## What is trialled

A D.16-flagged language collision is *eligible for human review* only when a narrow Spanish phrase is present, the RSS feed is marked Spanish, D.15 does not show independent selected-place evidence, and neither the headline nor cleaned description explicitly supports the selected location. The pilot currently covers Spanish `lagos` (lakes) and `reunión` (meeting). It does not block these place names generally.

The report computes **exact serialized article-entry intersections** by (URL, selected place) against the current news signals. These are *potential* entry changes only; the actual `news.json` is never altered by this module. It also provides balanced samples, safety gates, and a synthetic regression benchmark. Full article text has not been independently verified; human source review is required before any enablement decision.

## Local testing

`python -m unittest discover -s tests -p 'test_d17*' -v`

## Rollback

To remove D.17, restore the previous v2.4D.16 `scripts/update.py` and optionally delete the D.17 module and test. The last-known `news.json` does not need rollback: D.17 never modifies it.
