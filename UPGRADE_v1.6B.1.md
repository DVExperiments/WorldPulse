# WorldPulse v1.6B.1 — Neon Cartography Fix

## Installation
Copy **app.js**, **neon.css**, and **world-borders.geojson** into the ROOT of the existing WorldPulse GitHub Pages repository, replacing the first two. Do not alter index.html, data files, Python scripts, or `.github/workflows/update.yml`. Wait for Pages to deploy, then hard-refresh.

## Changes
- Bundles a 173-country/territory GeoJSON file (countryinfo dataset) with WorldPulse so boundaries load without a CDN.
- Renders permanent country and coast outlines as globe-anchored 3D geographic paths; they do not depend on news, filters, or coverage shading.
- Keeps a dim dotted land texture and grid as secondary styling.
- Removes floating HTML glow sprites that caused the purple top-left artifact.
- Preserves the satellite toggle, existing news markers, cluster filtering, data health and other controls.

## Known limits
- The bundled dataset includes **173 features** and is not a complete or authoritative representation of every sovereign territory or disputed boundary. It is a coarse global visual reference, not a political-border authority.
- Source geometry is from the Python `countryinfo` package dataset; check licensing and attribution for redistribution prior to public/large-scale use.
- Rendering passes JavaScript syntax checks; performance and visual output must be verified on GitHub Pages in a WebGL browser.
- If the outlines do not appear, confirm `world-borders.geojson` was uploaded beside `app.js` in repository root and check the browser console for a loading error.
