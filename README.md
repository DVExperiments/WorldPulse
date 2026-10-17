# WorldPulse v1.6D.9 — Living Grid + More Local Signals

This is a **frontend-only** patch built on top of v1.6D.8.

## Changes

1. **More perceptible, irregular cyan grid flicker.** Independent settlement-grid dots occasionally catch the light, mixed with softer random brightness drift. No synchronized pulse, no moving dots, and no blinking borders.
2. **One less news clustering level.** Removed the coarsest 19-degree map grouping. The default globe now uses the previous second tier (9-degree cells), so more existing news signals stay separate without zooming.
3. **Zoom-aware clustering still works.** At intermediate zoom the cell size is 4.5 degrees; close up it displays unaggregated signals. Cluster counts and click-through article members stay intact.

## Install

Replace only the root `app.js` in the existing WorldPulse repository. Keep all CSS, HTML, population raster, `world-borders.geojson`, JSON data, collectors, and `.github/workflows/update.yml` unchanged. Commit, wait for GitHub Pages, and hard refresh.

## Important accuracy note

Smaller clusters **do not increase underlying news coverage**, counts, or location accuracy. More markers at a given zoom represent the same sampled articles at finer spatial groupings. Country-level markers remain approximate subjects.

## Verify

- With **Subtle signal twinkle** enabled, look for small, irregular cyan brightness flickers. Disable to compare.
- At the initial globe view, more coloured news markers should remain independent than before, particularly in Europe and eastern North America.
- Zoom in and out; nearby markers should still group/un-group, and clicking them should continue to open real articles.
- `WorldPulseShimmerStatus()` remains available in the browser console.
