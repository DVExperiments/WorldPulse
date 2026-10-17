# WorldPulse v1.6B — Neon Globe Refinement

## Install on your existing GitHub Pages repository

Replace the existing **root** `app.js` and `neon.css` with the two files in this ZIP. Do not modify `update.yml`, `style.css`, `coverage.css`, `index.html`, or any JSON data. Wait for GitHub Pages deployment, then hard refresh (Ctrl+Shift+R).

## What changes

- Dense neon land dots sampled inside country polygons, and three-pass cyan coastline glow, generated locally in the browser from the world-atlas boundary dataset already used by the coverage layer.
- Softer latitude/longitude grid with continent outlines dominating the visual hierarchy.
- Small, category-colored, gently shimmering halos at **real news signal coordinates**; aggregated markers become larger glows. No invented news sites or pulsing coverage rings.
- Subtle starfield ambience using CSS; respects reduced-motion preferences.
- Existing satellite view, filters, zoom, click interactions, country shading, source links, and data remain untouched.

## Dependencies and caveats

- The dotted continents require the existing country-boundary request (`world-atlas@2/countries-110m.json`) to succeed. If it fails, the globe retains its basic grid and news markers.
- Browser WebGL and Globe.gl are required. Dense cartographic texture rendering may be slower on low-powered devices. The texture is built once when boundaries load and when switching back to Neon mode, not on every animation frame.
- This patch was syntax checked but not visually validated in the user's deployed browser. If visual changes seem absent, hard refresh the page.
- Markers represent sampled headline **coverage**; geographic matches aren't verified event sites. Dotted continents and stars are decorative cartography, not additional news.
