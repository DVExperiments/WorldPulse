# WorldPulse v1.6B.2 — Independent Neon Map & Data Startup Repair

This corrective patch replaces **only** `app.js`. Keep existing `world-borders.geojson` (from v1.6B.1) alongside it at the repository root.

## Fixes
- Draws detailed country and coastline outlines into the *neon globe material* from the bundled GeoJSON, independently of news data, category filters, D3, and optional 3D paths methods.
- Adds faint land dots, with borders in two luminous passes. This is geographic decoration, not extra news.
- Starts fetching `data/news.json` and `data/events.json` even when globe initialization throws, so one rendering error cannot prevent data status updates.
- Isolates neon texture generation errors and logs them to the browser console.
- Prevents duplicate simultaneous boundary loads.

## Installation
1. Replace root `app.js` with the one in this ZIP.
2. Confirm `world-borders.geojson` already exists in the repository root from v1.6B.1. It is included again here for convenience; if missing, upload it to the root.
3. Commit to `main`, wait for GitHub Pages deployment, then hard-reload.
4. Check for coastlines/country lines **before** the feed loads. Check live article and event numbers afterward.

No changes to `scripts/`, `.github/workflows/update.yml`, or `data/` are required.

If either problem remains, open DevTools (F12) > Console and copy the first red error, and check Network for `world-borders.geojson` and `data/news.json` (both should return HTTP 200).

## Caveat
Automated tests verify JS syntax, valid bundled GeoJSON and patch packaging. Full WebGL rendering on GitHub Pages needs browser validation.
