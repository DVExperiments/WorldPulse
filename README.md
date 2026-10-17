# WorldPulse v1.6D.11 — Balanced Ambient Flicker

A visibility adjustment for the cyan population grid after v1.6D.10 became imperceptible.

- Interpolated irregular brightness changes now occur at a middle-ground rate between v1.6D.9 and v1.6D.10.
- Wider dot brightness range while maintaining fixed size and positions.
- About 7 texture updates/second (hardware-dependent), rather than a rapid flash.
- Preserves `prefers-reduced-motion` behavior, and the manual twinkle checkbox.
- Preserves v1.6D.9 reduced clustering, news data, and the neon geography.

## Install
Replace only root `app.js`; hard-refresh after GitHub Pages deploys.

## Diagnostics
Run `WorldPulseShimmerStatus()` to check `enabled`, `reducedMotion`, `frames`, and `canvasBound`. Reduced motion must be false for the flicker to play. This is a visual-tuning patch, not a medically verified photosensitivity-safe setting.
