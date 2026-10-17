# WorldPulse v1.6D.7 — Smoother Living Earth

Increases the population-grid shimmer refresh rate from approximately **4 FPS** to **11 FPS** by reducing the render interval from 240 ms to 90 ms and the frame throttle from 220 ms to 85 ms.

The grid, country borders, measured population brightness, category colours and news sources remain unchanged. Animation pauses in hidden tabs.

## Installation
Replace **app.js** in the repository root; keep all other files unchanged, including `update.yml`. Wait for GitHub Pages deployment and hard-refresh.

## Performance note
Each update still redraws a 2048×1024 texture; this update requests more GPU uploads and may cost more performance on older devices. If globe rotation becomes sluggish, revert to v1.6D.6, or request an adaptive animation-quality setting.

## Verify
Use `WorldPulseShimmerStatus()` in the console. `frames` should increase more quickly than before. This patch has undergone a JavaScript syntax check, not a live WebGL benchmark.
