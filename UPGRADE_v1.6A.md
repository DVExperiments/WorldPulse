# WorldPulse v1.6A — Neon Globe Visual Redesign

## Installation on existing GitHub Pages repository

Replace `app.js` and `index.html` at the root, and add `neon.css` at the root. Keep `style.css`, `coverage.css`, all `data/` files, `scripts/` and `.github/workflows/update.yml` unchanged. Commit to main and wait for GitHub Pages, then perform a hard refresh.

## Changes

- Default mode is a dark cyan longitude/latitude wireframe, with country outlines and fine dot texture after the existing `world-atlas` topology loads.
- Realistic Earth remains an alternate display mode. Mode selection is saved locally in the browser.
- Category markers remain linked to actual mapped articles/events and cluster as before; the subtle twinkle affects marker brightness, not positions or news-velocity values.
- No large pulse rings or synthetic news locations have been added.
- The coverage shading and recorded event layers remain present.

## Limitations and verification

The base wireframe works without the country-boundary network request, but coastline outlines and land dots need the existing world-atlas and d3-geo CDN resources. This release is not a pixel-perfect reproduction of the visual concept and does not create additional news density. The browser WebGL result and performance should be tested on the published site, especially on lower-powered hardware. Country polygons can visually obscure neon texture when coverage shading is enabled; turn off coverage shading for the pure neon map view. The source of the continent lines is the same world-atlas dataset already used by v1.5.4C.

Sanity checks: switch Neon → Real → Neon, rotate, zoom, click news signals, try category filtering and Recorded events, open Data Health and return. Confirm the collector stays untouched.
