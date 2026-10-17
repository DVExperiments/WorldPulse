# WorldPulse v1.6D.1 — Visible Signal Twinkle

The prior v1.6D twinkle changed only a tiny fraction of marker colours, so it was difficult to see. This patch makes an occasional individual news signal visibly sparkle toward white for about one second, then return to its category colour. Sparkles are anchored only to existing mapped news signals and do not represent new events or real-time news updates.

**Installation:** replace the root `app.js` from v1.6D. Keep `index.html`, population texture, globe border data, collectors, and `.github/workflows/update.yml` unchanged. No news refresh required.

**Test:** enable Neon globe and Subtle signal twinkle, leave the globe stationary for 20–30 seconds, then uncheck twinkle and compare. The effect is more noticeable when the globe is zoomed in. If you see no movement, hard-refresh (Ctrl+Shift+R) and inspect the browser console. Browser visual rendering has not been validated here.
