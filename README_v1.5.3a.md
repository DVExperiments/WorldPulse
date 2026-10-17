# WorldPulse v1.5.3a — Quiet Globe visual hotfix

This is a **frontend-only** fix for the distracting, overlapping rings seen in v1.5.3.

## Install
Replace **only `app.js`** at the root of the WorldPulse GitHub repository. Commit to `main`, wait for GitHub Pages to publish, then hard-refresh (Ctrl+Shift+R).

There is **no need** to rerun the news collection workflow or modify `.github/workflows/update.yml`. Leave all `data/*.json` and `scripts/update.py` untouched.

## What changed
- Removes the repeating Globe.gl ring visualization.
- Restores country-level stories as small, category-colored clickable markers instead of a near-invisible ring anchor.
- Keeps map-layer selection, categories, precision filtering, clustering, and tooltip wording identifying country-level subjects as approximate.
- Existing news velocity stays in the tooltip/panel, but does **not** trigger animation: it was never what drove the old rings.

## Caution
Country-level markers still use representative country coordinates rather than verified news event sites. A future boundary/area layer would be a better portrayal of broad location uncertainty.
