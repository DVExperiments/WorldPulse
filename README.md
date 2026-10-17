# WorldPulse v1.6D.5 — Living Earth Texture Repair

This patch addresses the population-grid shimmer initializing but not displaying.

It binds a canvas-backed WebGL texture directly to the globe material, marks that texture for refresh, and prevents duplicate animation timers. It retains the existing neon country outlines, measured population brightness, news marker appearance, and news collector.

## Install
Replace the repository-root `app.js` only. Leave `index.html`, existing CSS, `world-borders.geojson`, population raster, data files and `.github/workflows/update.yml` unchanged.

## Verify
After a hard refresh, type `WorldPulseShimmerStatus()` in the browser console. `canvasBound` and `displayedTextureIsCanvas` should be true, and `frames`/`uploadsRequested` should rise over time. These diagnose update requests, not independently confirmed GPU upload.

The visual effect still requires testing in the deployed browser.
