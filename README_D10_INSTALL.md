# WorldPulse v2.4D.10 — Location Accumulation Investigation

## Purpose
Diagnostic-only update. It does not change how news articles are assigned to places, deduplicated, or displayed. It adds a `d10_location_investigation` object to `data/feed-contribution-audit.json` after the collector runs.

## Upload in GitHub web UI
Extract the ZIP and upload these files into the WorldPulse repository, maintaining folders:

- `scripts/update.py` — replace existing
- `scripts/geo_anomaly_d10.py` — add
- `tests/test_d10_anomalies.py` — add

Keep all earlier geographic modules, your existing `tests/d9_geo_benchmark.json`, the GitHub workflow `.github/workflows/update.yml`, and all current site data.

Run Actions → Refresh geographic news (existing `update.yml`). No workflow modification is required.

## What to inspect
Download or open `data/feed-contribution-audit.json` after the run and locate `d10_location_investigation`. Start with `locations` → `Vietnam`:

- `distinct_url_location_pairs` and `duplicate_feed_observations`
- `evidence_levels` and `headline_locality_cues`
- `review_signals`: description-only, contextual matches, cross-border mentions, conflicting selections
- `review_samples`: title, URL, current assignment, evidence level, original feed
- `top_publishers`, `source_editorial_regions`, `similar_title_groups_across_distinct_urls`

These are **review signals**, not verified errors. No existing pinned location is suppressed by D.10. Source feed edition is not used as location evidence. Syndicated coverage can appear under multiple different URLs. The source is limited to RSS snippets, not full article body text.

## Verification
Run `python -m unittest discover -s tests -p 'test_d10_*.py' -v` in a complete checkout. Run the previous regression tests as well. The direct-upload ZIP intentionally does not replace your entire repository.
