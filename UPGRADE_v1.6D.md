# WorldPulse v1.6D — Living News Signals

A frontend-only patch built on the working v1.6C.3 measured population texture.

## Changes
- Adds subtle category-coloured light halos beneath real sampled news markers (only for clusters with 2+ articles).
- Cluster core size and halo intensity scale logarithmically with sampled article volume; no fabricated positions.
- Adds restrained optional twinkle through the existing **Subtle signal twinkle** checkbox.
- Works at existing globe zoom/cluster tiers, with no giant pulsing rings.
- Keeps news click-through, location precision filters, satellite mode, GeoJSON cartography and population density texture.

## Install
Replace only `app.js` in the repository root. Keep all CSS, `index.html`, `world-borders.geojson`, population texture, collectors and `.github/workflows/update.yml` unchanged. Commit to main; wait for Pages deployment and hard-refresh.

## Verify
1. Neon globe: article-dense markers have a soft glow and clearer scale variation.
2. Zoom in: clusters split; smaller single-story points stay modest.
3. Uncheck 'Subtle signal twinkle': animated highlights stop; colors remain stable.
4. Real globe: markers retain their previous styling.
5. Click a core or glow marker and confirm the same source-linked news drawer opens.
6. Category and precision filters still remove the right markers.

## Accuracy and limits
Halos are *visual representations of sampled news article counts* and are not incident severity, sentiment, verified event counts, or real-time internet traffic. Brightness is bounded to avoid visual overload. This patch was checked for JavaScript syntax and static invariants, not yet verified in a live WebGL browser.
