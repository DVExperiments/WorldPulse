# WorldPulse v1.6D.4 — Living Earth

A focused frontend patch that animates the **ambient population grid**, not the news markers.

## Installation

Replace `app.js` in your GitHub Pages repository root with the included file. Leave all other files, especially `index.html`, `world-borders.geojson`, `assets/population-density.png`, and `.github/workflows/update.yml`, unchanged.

Deploy via GitHub Pages and hard refresh. Use **Neon globe** with **Subtle signal twinkle** enabled.

## What changed

- Keeps regular grid spacing, fixed pixel positions and measured-population brightness from v1.6C.3.
- Builds an offscreen base texture with the country/coastline outlines and regular population dots.
- Selects a stable subset of the *existing* population grid for gentle, asynchronous luminance shimmer.
- Updates the existing WebGL globe texture in place, instead of reloading the entire image or rebuilding news geometry each frame.
- News signal radius and colour remain stable; only their normal cluster halos remain.
- The existing **Subtle signal twinkle** toggle now controls ambient grid shimmer.
- Real globe view remains unchanged; updates pause while the tab is hidden.

## Console diagnostics

Once the boundaries and population raster load, look for:

`WorldPulse: living population grid initialized: <number> shimmer-capable dots`

The existing `WorldPulse: measured population brightness raster ready.` message should also appear.

## Limitations

The animation is a visual effect and does not imply changes in population or news. Browser GPU/driver support for refreshing the existing texture still needs live verification. If the grid remains static, inspect the browser console and compare with the twinkle checkbox on/off.
