# WorldPulse v1.3 — Global News Signals

An interactive 3D globe for geographically referenced headlines. Static GitHub Pages frontend and scheduled GitHub Actions Python collector. **No API keys, Python dependencies, hosting fees, or server required.**

## What's new in 1.3

- Seven categories including **War & conflict**, visually differentiated with a pink-red marker.
- 28 RSS searches: seven themes × four regional Google News editions (US, UK, India, Australia) for broader coverage than one global query.
- Bundled gazetteer of ~380 named places, countries and key cities / conflict-reporting areas. Unmatched headlines aren't assigned locations. The named place is a reference, not an independently verified incident site; country markers are approximate.
- Deduplicates article URLs across overlapping regional searches, with conservative normalized-title matching to merge nearly identical syndicated headline copies in the same category and location.
- Per-marker news **velocity**: latest 3 hours compared with previous 3 hours in the current RSS sample (`rising`, `steady`, `cooling`). Shown as rising in tooltip and panel, not asserted as event severity.
- Source names and publication ages in the story drawer; up to 20 article links per marker-category.
- Collector errors, successful query counts and removed duplicate counts visible in metadata and logs.

## Publishing / upgrading

To deploy, upload all files and folders to the **root** of the `WorldPulse` GitHub repository; use the GitHub web editor to create/update the hidden workflow file at `.github/workflows/update.yml` if the upload dialog hides the `.github` folder.

For an existing working v1.2 site, replace these files:

1. `scripts/update.py`
2. `data/places.json` (NEW and essential)
3. `app.js`
4. `index.html`
5. `.github/workflows/update.yml` (recommended: new step name and longer timeout)
6. `README.md` (optional)

**Keep the existing working `data/news.json` file.** The next workflow run will replace it with a new v1.3 snapshot. Do not overwrite it with the empty starter snapshot in this ZIP when upgrading an existing repository.

Go to **Actions → Refresh geographic news → Run workflow**. After a successful run, inspect `data/news.json`: `schema: 2`, `status: live` or `partial`, and `points` should be populated. Refresh the Pages site with Ctrl+Shift+R.

## Limitations and honest metrics

- **This is a sampled monitoring view, not a census of 24-hour global articles.** Google News RSS returns ranked, capped feed results; searches are performed in English and overrepresent locations prominently featured in headlines. Counts cannot be compared as unbiased estimates of all reporting.
- One article is assigned to the most specific explicitly named recognized place in its headline, not necessarily the real event location. A story mentioning multiple cities gets only one pin. Some names are ambiguous and a finite gazetteer misses many small towns.
- The category means *query theme that found the article*. War coverage includes reports, official claims and opinions: it is not a verified record of battlefield incidents or casualties. Article links lead to the Google News item (which may redirect); the collector also stores source labels.
- URL deduplication and near-identical-title matching remove repeats, but different headlines and sources about the same event remain as separate article records. Thus counts are articles rather than unique real-world events.
- **News velocity** compares sampled publication-time counts in the most recent three hours to the previous three; sample variation or missing feeds can create false signals. It is not a dependable incident-alert system. Never treat it as an emergency warning.
- Social posts layer remains disabled without verified, permission-appropriate geolocation sources. Browser translation only works where supported, otherwise original-language titles display.
- Google News RSS availability, rate limits and output format can change. The workflow retains older news on total failure and marks it stale.

## Architecture

`GitHub Actions` -> Python stdlib RSS collector (`scripts/update.py` + bundled `data/places.json`) -> `data/news.json` -> `globe.gl` static viewer (`index.html`, `app.js`, `style.css`). Scheduled twice per hour. No client-side access to paid APIs, secrets or scraping of article bodies.

## Test the collector locally

Run `python scripts/update.py` from the repository root (uses network access). Check console results and `data/news.json`. JS syntax can be tested with `node --check app.js` if Node.js is installed.
