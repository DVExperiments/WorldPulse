# WorldPulse v1.6D.6 — Visible Population Grid Shimmer

## Fix
The previous texture implementation selected ~1,900 tiny squares worldwide. Those tiny changes are almost invisible once projected onto the globe. This build increases the proportion of **existing** ambient population grid dots that shimmer and raises their small brightness variation, without moving the grid or changing news dots and country borders.

## Install
Replace `app.js` in your repository root. Do not change any news collection files, GeoJSON, or population raster. Commit and hard-refresh after GitHub Pages deploys.

## How to test
1. With neon mode and Subtle signal twinkle enabled, keep the globe still and observe land dots.
2. If unclear, type `WorldPulseShimmerTest(true)` in the developer console yourself. This enables an intentionally exaggerated **temporary** brightness test, not the intended final appearance.
3. Watch for clear asynchronous dot changes, then type `WorldPulseShimmerTest(false)` to restore the gentler mode.
4. You can check `WorldPulseShimmerStatus()` for frames, texture binding, and test-mode state.

Note: The previous city/settlement grid remains an ambient interpretation, not a news source. This update only alters the animation. No new geographic facts are implied.

If test mode shows no changes, the issue is still with texture updates or browser rendering, not ordinary shimmer contrast.
