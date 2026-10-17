# WorldPulse v1.6B.3 — Permanent Neon Country Borders

This fixes a confirmed code defect in the previous patch: `updateCartographicPaths()` was calling `pathsData([])` and clearing the already prepared borders.

## Install
Replace only root `app.js` with the included file. Keep `world-borders.geojson` in the repository root from v1.6B.1. Do not replace or edit `update.yml`, `index.html`, news files, or CSS. Commit directly to main and hard refresh after Pages deploys.

## Validation
Check the browser Console for `WorldPulse: permanent neon country paths rendered:`. A number above zero confirms paths were submitted to the renderer. If the line does not appear, check Network for `world-borders.geojson` returning HTTP 200, and send any Console errors.

The neon borders remain independent of news availability and category selection. Satellite mode hides the neon border overlay. This patch has been syntax-checked but not verified in your browser.
