# WorldPulse v1.6D.3 — Actual WebGL Signal Shimmer

## What was broken
The previous v1.6D patches updated Globe.gl point colour/radius accessor callbacks, but this alone did not force the already-built WebGL point meshes to change. As a result, the timer fired without visible animation.

## What's different
The 280 ms animation update now regenerates point display records with staggered shimmer amplitudes and gives those records to `globe.pointsData(...)`. Each news dot can brighten smoothly and enlarge by up to 15% while maintaining the underlying news coordinates, category colours, map texture and coverage controls. This runs only for visible tabs in Neon mode with twinkling enabled.

## Installation
Replace only `app.js` in the GitHub Pages repository root. Keep everything else, including `update.yml` and the population raster, unchanged.

If animation impacts performance on slower devices, turn off **Subtle signal twinkle**.

## Testing
Toggle **Subtle signal twinkle** off then on. Watch several dots for 5–10 seconds. WebGL point updates should now be visible. This build passed a JavaScript syntax check but has not been validated in the user's browser.
