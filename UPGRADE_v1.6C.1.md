# WorldPulse v1.6C.1 — Population Brightness Refinement

This patch refines the neon globe's ambient land grid so it keeps the same regular dotted grid while showing population density through clearer brightness variation.

## What changed

- Preserves the existing neon country and coastline outlines.
- Preserves the regular land grid pattern.
- Dense population regions now render with brighter cyan dots.
- Sparse regions remain dimmer.
- Keeps subtle metropolitan glow under the grid.
- Does not change the news collection workflow or category markers.

## Install

Replace `app.js` in the repository root with the version from this patch.

Keep `world-borders.geojson` in the repository root.

Then let GitHub Pages redeploy and hard refresh the site.

## Notes

The background grid is an ambient visual layer and is not a live population feed. It is intended to make the globe feel more alive and closer to the digital concept aesthetic.
