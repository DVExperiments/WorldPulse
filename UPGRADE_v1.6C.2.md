# WorldPulse v1.6C.2 — Ambient Brightness Refinement

Visual-only patch, building on v1.6C.1.

## What changes
- Preserves the uniform 5-pixel land-dot grid and the working cyan borders.
- Uses modest brightness variation to suggest settlement concentration: denser areas are brighter, sparse land is darker.
- Adds restrained urban-node glows beneath grid dots.
- Reduces random sparkle variations so regional brightness patterns remain readable.
- Does not alter news markers, news collection, JSON schemas, or GitHub Actions.

**Accuracy note:** The glow is an illustrative settlement proxy based on an approximate curated city-hub list, *not* a measured global population raster. Do not interpret it as exact census density or live activity.

## Install
Replace the repository-root `app.js` with this version. Keep `world-borders.geojson` in the repository root; it is also included in this ZIP for convenience. Keep the site's other files and `.github/workflows/update.yml` unchanged. Commit to `main`, wait for GitHub Pages, and hard refresh.

## Verification
Check Europe, eastern North America, India/East Asia and the Sahara or central Australia in Neon mode. Borders should stay fixed. Dots should remain on the same grid while showing subtle brightness differences. Toggle Real globe to confirm it is unchanged. Confirm that news dots and category filters still work.
