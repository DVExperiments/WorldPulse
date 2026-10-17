# WorldPulse v1.6C.3 — Measured population brightness

This **incremental patch** builds on v1.6C.2. The neon globe's fixed, regularly spaced cyan land dots are brightness-modulated by a small static texture generated from WorldPop 2020 population-density data. Dot spacing and sizes do not change. Country outlines, category-coloured news signals, the Real/Neon toggle, and all news collection scripts are unchanged.

## Install (GitHub Pages)

1. Replace root `app.js` with the included file.
2. Create `scripts/build_population_texture.py` using the included script.
3. Add `.github/workflows/build-population-texture.yml` as a **new workflow**. GitHub's upload interface can hide dot-folders; use **Add file → Create new file** and enter `.github/workflows/build-population-texture.yml` as the filename, then paste its contents if necessary.
4. Keep existing root `world-borders.geojson` unchanged. Keep your existing `.github/workflows/update.yml` unchanged.
5. After committing, open **Actions → Build WorldPulse population texture → Run workflow**. This runs a *one-time*, independent build and commits `assets/population-density.png` and the source metadata file to `main`.
6. Wait for the Pages build, then hard-refresh WorldPulse. In Console, look for `WorldPulse: measured population brightness raster ready.`

**Important:** This ZIP **does not include a measured population PNG**. The external raster could not be fetched from the artifact-building environment. GitHub Actions must fetch it and generate the static PNG. If that action fails or the PNG does not exist, the site's earlier city-hub approximation remains in use. The workflow fails rather than inventing measured data. The action does not modify `update.yml` or any news data.

## What the generated PNG represents

- Source: WorldPop 1km population density time-series (year 2020), persons/km², delivered by the WorldPop ArcGIS ImageServer.
- Method: the source raster is downsampled into a global equirectangular image (1440×720) and logarithmically scaled to 8-bit brightness. This is an *ambient visualization* of modelled residential density, not exact population counts at each drawn dot and not a real-time reading.
- Areas outside the source raster extent (around south of 59.5°S / north of 83.6°N) are blank in the derived density layer. Country borders remain visible.
- License: CC BY 4.0. Attribution: WorldPop et al., *Global High Resolution Population Denominators Project*, DOI 10.5258/SOTON/WP00674. See `assets/population-density-info.json` after generation.

## Testing

- `node --check app.js`
- `python -m unittest discover -s tests -v`
- Live download and WebGL rendering must be tested after deployment. Check the *population* Action log to ensure that measured raster values were actually obtained.

## Files

`app.js` (replace), `scripts/build_population_texture.py` (add), `.github/workflows/build-population-texture.yml` (add), `tests/test_population_texture.py` (optional). No changes to the main `update.yml`.
