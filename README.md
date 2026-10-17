# WorldPulse v1.6B.4 — startup and cartography hotfix

## What was fixed

- `ReferenceError: Cannot access 'bordersLoading' before initialization`: the border-loading flag now initializes before `bind()` and before `loadBoundaries()` can run.
- Duplicate early calls to `loadBoundaries()` removed.
- Removed the incompatible `pathsData()` renderer for country boundaries, implicated by `t.Adder is not a constructor` in d3-geo on the deployed site. The bundled GeoJSON instead draws the real country/continent geometry into the neon globe texture, so it rotates with the Earth and does not depend on news records.
- Existing UI/data collector unchanged; favicon 404 is unrelated to news/globe.

## Install

Upload **app.js** to the repository root, replacing the current one. Ensure **world-borders.geojson** exists in the repository root (included here for convenience, overwrite if unsure). Do not alter `index.html`, styles, `data/` or `.github/workflows/update.yml`.

Commit changes, wait for GitHub Pages deployment, then hard-refresh (Ctrl+Shift+R). The globe should render coastlines/country borders without waiting for news articles. The underlying news may still show 'Partial feed' if some publisher feeds fail; that is independent of the map.

If country outlines are still missing: DevTools → Network → check `world-borders.geojson` returns HTTP 200; DevTools → Console → send any `WorldPulse neon cartography texture` or `WorldPulse cartography` error. Browser rendering has not been live-verified here.
