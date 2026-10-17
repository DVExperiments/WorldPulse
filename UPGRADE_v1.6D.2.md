# WorldPulse v1.6D.2 — Living Shimmer Repair

This frontend patch fixes the barely visible twinkle in v1.6D.1.

- News markers softly and continuously brighten and return to their category colour.
- Marker radius changes by no more than 7%, avoiding distracting pulses.
- Each marker has a distinct animation phase; nothing flashes in unison.
- Glowing halos, cartography, population raster, and data collection stay untouched.
- Shimmer is decorative, not an indication of breaking news or severity.
- The `Subtle signal twinkle` checkbox disables the animated treatment.
- Animation updates pause when the browser tab is hidden.

## Installation

Replace only `app.js` at the root of the GitHub repository. Keep all other files and the `update.yml` workflow unchanged.

After GitHub Pages redeploys, hard-refresh. In Neon mode with Subtle signal twinkle enabled, watch several dots for 5–10 seconds. For a comparison, turn the checkbox off.

The patch passed JavaScript syntax checks but has not been visually validated in your browser.
