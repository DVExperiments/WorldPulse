# WorldPulse v1.6E — Constellation News Clusters

A frontend-only visual patch based on v1.6D.11. It retains the balanced population-grid flicker, permanent neon borders, news filters, and the working data pipeline.

## What changed
- Collapsed news groups now show a **central clickable signal with up to seven small category-coloured satellite lights** instead of a single giant dot.
- Soft category glow scales logarithmically with mapped article volume.
- Constellation details disappear at close zoom or when clustering is disabled.
- Category-specific grouping and the existing less-aggressive geographic grouping are preserved.
- Decorative mini-lights open the **same original news cluster**. They are **not** additional reports or verified positions.
- Reduced motion users see static constellation visuals, without a new animation effect.

## Installation
Replace only `app.js` in the root of your WorldPulse GitHub Pages repository. Keep the current `index.html`, CSS, `world-borders.geojson`, population raster, collectors, data files, and `.github/workflows/update.yml` unchanged. Commit and hard-refresh after Pages deployment.

## Limitations
The constellation layout is a local decorative arrangement near each aggregated geographic centre. It must not be interpreted as precise locations for its satellite lights. Cluster article counts still refer only to the underlying news records. This patch has been syntax-checked but needs visual testing in the deployed browser.
