# WorldPulse v2.4D.19.1 — Feed Resilience & Coverage Protection

Direct-upload patch for the existing D.19 repository. Preserve all previous modules.

## Upload
- `scripts/update.py` (replace)
- `scripts/feed_resilience_d191.py` (new)
- `tests/test_d191_resilience.py` (new)
- `README_D191_INSTALL.md` (optional)

No changes to `.github/workflows/update.yml`. D.18 live corrections remain locked OFF by D.19 code.

## Behaviour
- Google RSS requests: maximum 3 attempts total on transient 429/5xx or network timeouts, bounded exponential backoff and jitter. Permanent 4xx other than 429 fail immediately.
- Google request spacing: 0.35s between requests. Direct publisher feeds use the existing logic.
- When at least 80% of 20+ Google feeds fail (and very few succeed), preserve `data/news.json` **only if** it already has >=350 serialized article entries and its timestamp is <=30h old. An empty/stale first deployment will publish available direct feeds instead of permanently freezing the site.
- When preservation occurs, `data/news.json` is left byte-for-byte unchanged. `data/source-health.json` and `data/feed-resilience-health.json` are updated to report the failed attempt. D.19 audit and other historical files are not overwritten with the degraded snapshot.
- When regular publishing resumes, audit `release` will report `v2.4D.19.1` and include `d191_feed_resilience`.

**Limitations:** This is snapshot-level protection, not automatic merging of live direct publisher articles with previous Google results. It does not make Google News availability predictable. The safeguard depends on the previous snapshot being present in the repository checkout. Check that your GitHub Actions workflow's checkout includes committed `data/news.json` before running. The 350 article / 30 hour safety threshold is intentionally conservative; tune only after observing multiple real runs.

## Validation
Run `python -m unittest discover -s tests -p 'test_d191_resilience.py' -v` and existing D.19 tests. Restart the GitHub Action. Inspect `data/feed-resilience-health.json`, `data/source-health.json`, and latest `data/news.json` timestamp when Google returns 503.
