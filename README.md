# WorldPulse v1.6C — Settlement Density Globe

This patch refines the neon globe surface so the ambient land texture feels more alive and closer to the concept direction.

## Changes

- Keeps the working neon country and coastline outlines from v1.6B.4.
- Adds a population / settlement-inspired ambient dot field across land.
- Major urban regions receive brighter cyan dot density and faint local glow.
- Sparse regions remain quieter and dimmer.
- Live news dots remain the coloured foreground layer.
- No changes to the news collection pipeline or workflow.

## Install

Replace `app.js` in the repository root.

Keep `world-borders.geojson` in the repository root. A copy is included for convenience.

Hard refresh the site after GitHub Pages deploys.

## Notes

The background settlement texture is an ambient visual layer derived from a built-in worldwide city hub set. It is not a live population dataset and should not be interpreted as live news activity.
