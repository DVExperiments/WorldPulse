# WorldPulse v1.5.4C — Geographic Coverage Visualization

## Installation
Replace the repository root `app.js` and `index.html`; add the new root `coverage.css` file. Do not replace `style.css`, collector scripts, GeoNames modules, data snapshots, or `.github/workflows/update.yml`.

Wait for GitHub Pages deployment, then hard-refresh the site. No news collector rerun is needed.

## Features
- Opt-in **Shade countries by sampled reporting** toggle in the Display area.
- Country/territory shapes from `world-atlas@2/countries-110m.json` (Natural Earth simplified shapes) downloaded in the browser. Supporting `topojson-client` and `d3-geo` scripts load from a CDN.
- Approximate country-level color based on the number of deduplicated news articles associated with geographic marker positions inside each shape. This is **not** source-country, audience, or confirmed event-site coverage.
- Counts follow existing category and geographic precision filters. Clicking a shaded country opens links for its matched points.
- Data Health overview cards and topic/precision bar charts, with existing detailed diagnostics preserved.
- No automatic return of country pulse rings, changes to news collection, or extra permissions.

## Caveats
- A country with zero mapped records may still have many actual events and uncollected news stories.
- City, region and country matches refer to geographic *subjects*, not confirmed incident coordinates. Polygons are generalized and may have border inaccuracies.
- The fallback is the existing globe if country-boundary loading fails.
- A static page that uses external CDNs requires network access; to operate completely offline, vendor the globe, topojson, d3 and GeoJSON/TopoJSON datasets within the repository.
- Colors use a logarithmic scale to avoid a few high-count countries overwhelming the display. They should not be interpreted as absolute cross-national coverage rates.

## Smoke test
1. Confirm the globe loads, dots remain visible, and news links work.
2. Enable 'Shade countries by sampled reporting' in Display. Verify country polygons appear, no animated rings.
3. Toggle one category; country shading should update.
4. Select a shaded country and verify linked sampled stories in the drawer.
5. Switch to Recorded events: country shading should hide.
6. Open Data Health and verify KPI tiles, topic charts and the original diagnostics.
7. In browser DevTools, check whether third-party boundary source was blocked if the toggle reports an error.
