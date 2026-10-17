# WorldPulse v1.6D.10 — Calm Flicker & Reduced Motion

This targeted frontend update reduces the frequency and intensity of the cyan population-grid flicker. It preserves the less-aggressive news clustering introduced in v1.6D.9.

## Changes
- Removes short stochastic sparkle spikes that could resemble flashes.
- Slows per-dot brightness transitions and reduces their amplitude.
- Caps animated texture refreshes at about five per second (190 ms interval).
- Respects `prefers-reduced-motion`: ambient animation starts disabled when that preference is enabled, and pauses if the user enables reduced motion while visiting.
- Preserves the existing checkbox for manually enabling/disabling twinkle (unless the browser requests reduced motion).
- No changes to article locations, counts, news-dot clustering, cartography or population data.

The change reduces unnecessary rapid variations but is **not** a formal photosensitivity safety certification. Users who are sensitive to motion can switch off *Subtle signal twinkle* or enable reduced motion in their operating system.

## Install
Replace **only `app.js`** in your repository root; keep all CSS, HTML, geographic data, population texture, news collector and `.github/workflows/update.yml` unchanged. Commit and hard-refresh after GitHub Pages deploys.
