# WORLD PULSE — Interactive Global News Globe

A GitHub Pages–ready 3D news geography visualization: spin the globe, choose coverage themes, select locations and open linked articles. Built with HTML/CSS/JS, [Globe.GL](https://globe.gl/) and a scheduled Python data pipeline pulling article results from [GDELT DOC 2.0](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/).

## Deploy (no server, no API keys)

1. Create a **public** GitHub repository (e.g. `WorldPulse`).
2. Upload **all contents** of this package into the **repository root**, preserving `.github/workflows/update.yml`, `scripts/`, and `data/`. Do not upload only the enclosing folder.
3. Open **Settings → Pages → Build and deployment → Deploy from a branch** and choose `main` / `(root)`, then save.
4. Open **Actions → Refresh geographic news → Run workflow**. It fetches geographic coverage and commits `data/news.json`. If GitHub asks to enable Actions, enable them.
5. Reload `https://YOUR-USERNAME.github.io/WorldPulse/`. The scheduled job attempts a refresh at `:17` and `:47` each hour, subject to GitHub Actions queue/delay, GDELT uptime and GitHub repository settings.
6. In **Settings → Actions → General → Workflow permissions**, ensure **Read and write permissions** is selected if workflow push fails with HTTP 403. Some repos block pushes to protected branches; adjust permissions or commit using a PR process.

A new repository starts with **no sample or fabricated news**. The site needs the first successful Actions run to populate signals. The globe JavaScript and Earth texture need internet/CDN access. You can run `python scripts/update.py` locally (Python 3.10+ standard library only) if desired.

## What the numbers mean (v1.1 collector)

**This release uses GDELT DOC 2.0, not GEO 2.0.** The old GEO endpoint returned HTTP 404 and was replaced. The scheduled script requests the newest **up to 250 articles for each of six category searches** from the preceding 24 hours. It matches explicit named places in article *headlines* against a bundled 165-entry geographic name table, placing a dot at the reference coordinate for that named place. It does **not** infer a reporter's location from an outlet's domain, or a news event location from the whole article. Some headlines have no recognized place; those are omitted. Ambiguous locations can still occur. Country markers represent a reference point, not a country's news centroid.

**Marker count = unique article URLs in this limited query sample whose title matched the chosen place and category**, not the number of all new articles over 24 hours, not internet traffic, not unique news events, and not a complete representation of reporting for a country. One article can contribute to multiple category searches; global totals can overlap. For a matched article, the collector assigns its single longest explicitly named place and saves up to eight source links per marker. An empty category can be legitimate, but check Actions logs for API errors.

The six categories are independent keyword queries, not objective classifications of the event. Source titles may arrive in languages other than English; location matching uses Roman-script named places and is incomplete for other languages. Article titles appear as retrieved, with experimental on-device translation on supported browsers only. Older snapshots are kept if a category fails. A mixture of new and older category samples means totals are not synchronized across categories.

## Translation

The site reads `navigator.language`. If the user's browser supports the emerging on-device `Translator` API and can translate from English to that browser language, the interface attempts automatic translation of article link titles. If unavailable, titles remain as originally provided by GDELT. There is **no guaranteed cross-browser translation service** in this release. Opening the original link always goes to the publisher, in their own language. Later production versions can pre-translate from a licensed provider in the GitHub Actions pipeline (observe quotas and rights) and cache translated titles as static files.

## Social layer

The social tab is functional but **empty by default**. It will render `data/social.json` posts **only** if they include `verified_location: true`, numeric `lat`/`lng`, and article-like post links; don't equate hashtag/location mentions, profile bios, IP guesses or topics with a user's physical posting location. Build a legally/ethically sourced and consent-aware feed before enabling globally. Example schema (not real data):

```json
{"updated_at":"2026-10-17T06:00:00Z","source":"consented geotagged content","posts":[{"lat":40.7,"lng":-74,"name":"Example","verified_location":true,"articles":[{"title":"Example post","url":"https://example.org/post/123"}]}]}
```

No social platform APIs or tokens are currently configured. Avoid publishing precise personal whereabouts without permission. Social activity drawn from one platform is not equivalent to the world's internet traffic.

## Files

- `index.html` / `style.css` / `app.js`: frontend and 3D interactions.
- `scripts/update.py`: GDELT DOC article-list retrieval and headline-based location matching; retains old category data if a query fails and reports stale status.
- `.github/workflows/update.yml`: public repository scheduled automation / manual run.
- `data/news.json`: machine-generated snapshot (empty at first).
- `data/social.json`: optional verified-social-location dataset.

## Next improvements

- Add event-level deduplication, a larger reviewed gazetteer, and reliable event-location geocoding rather than headline place-name matching.
- Add automatic multilingual translation via a service-side translation provider with language caches and correct attribution.
- Add a vetted platform-specific public social feed with consented coarse locations, geographic confidence and sampling disclosures.
- Add date sliders, time-series archives, entity search, source diversity/credibility context and automated tests on live feed schemas.
- Add accessible non-WebGL 2D map / list fallback and mobile optimizations.

## Libraries & providers

[Globe.GL](https://github.com/vasturiano/globe.gl) (MIT) and GDELT DOC 2.0 (data source, terms governed by provider). Earth texture via the Three Globe example assets. No news article full text is stored in this app, just source links and title snippets. Browser requests also contact image/CDN providers. Check licensing and rate limits before public commercial deployment.
