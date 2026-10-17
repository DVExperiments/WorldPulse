# WorldPulse v1.6D.8 — Gentle Ambient Flicker

Changes the cyan population-grid animation from a smooth, periodic pulse into irregular gentle flickering.

## Changes
- Fixed dot positions, sizes and grid spacing.
- Smooth, deterministic noise-based brightness variation without synchronized periodic pulsing.
- Existing category-coloured news markers, coastlines and borders unchanged.
- Existing Subtle signal twinkle checkbox enables or disables the grid flicker.

## Installation
Replace only `app.js` in the repository root. Preserve all data files, the population raster, `world-borders.geojson`, CSS, HTML and `.github/workflows/update.yml`.

After deployment, hard refresh the website. `WorldPulseShimmerStatus()` is still available in the console. `WorldPulseShimmerTest(true)` enables a brighter diagnostic preview; use `WorldPulseShimmerTest(false)` to return to the normal visual effect.

The flicker is decorative and does not indicate news velocity or real-time population activity.
