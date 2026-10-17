# WorldPulse v1.6E.2 — News markers and population grid separation

This is a corrective patch on top of v1.6E.1.

## Changes
- **News only:** removes large cluster halos and cylinder-like oversized cores; keeps a small central clickable news marker, with satellite news markers sourced from the cluster's **real mapped member coordinates** (capped at 12 for performance). News category colours are preserved. Clicking a satellite opens the same news group.
- **Population only:** slightly raises the static background cyan-dot opacity so population lights remain clearly visible beneath the news layer. The balanced slow, irregular v1.6D.11 shimmer algorithm is unchanged.
- Does not change news data, categories, collection, geocoding, border geometry, cluster cell sizes, or GitHub Actions.

## Install
Replace only the repository-root `app.js` and hard refresh after GitHub Pages redeploys. Keep all data files, population-density raster, styles and `.github/workflows/update.yml` unchanged.

## Notes
The news dots are still globe.gl's point cylinders, but their radii and heights are greatly reduced. This patch prioritizes actual geolocations and distinct points over synthetic decorative rings. The small rendering-only displacement is used solely when a news signal sits essentially on the core, to prevent exact overlap.

Browser/WebGL appearance must be tested on the live site. If it still looks too cylindrical, the next architectural step is to use custom THREE.Sprite objects for **news only**, which would require dedicated click/pointer handling.
