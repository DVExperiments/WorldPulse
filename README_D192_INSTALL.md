# WorldPulse v2.4D.19.2 — Feed Health Monitoring & Recovery Validation

## Installation
Upload repository-relative contents of this ZIP to the repository root. Replace `scripts/update.py`; add `scripts/feed_health_d192.py`, retain/replace unchanged `scripts/feed_resilience_d191.py`, add tests. Keep existing geographic modules D4–D19. Do not change `.github/workflows/update.yml`. All D18 correction activation remains locked off.

## New files generated on each successful or failed-feed collection
- `data/feed-health-validation.json` — transport errors vs HTTP-success/zero-parsed outcomes by aggregator/publisher, plus frozen simulated outage scenario results.
- `data/feed-contribution-audit.json` adds `d192_feed_health_validation` when a normal publication occurs.
- `data/feed-resilience-health.json` continues reporting real D19.1 publication decisions.

Even if catastrophic outage preservation skips ordinary publication, `feed-health-validation.json` is written before returning. The regular contribution audit is intentionally left unchanged when publication is blocked.

## What is and is not tested
`frozen_outage_drills.scenarios` exercises healthy prior snapshot + catastrophic Google failure, partial Google failure, successful-but-empty Google feeds, healthy feeds, and expired prior snapshot. The test helper checks that the in-memory frozen baseline is unchanged and the existing D19.1 decision matches expectations. It does NOT replay HTTP requests, execute GitHub Actions, or assert that a real future outage was protected. A successfully fetched but empty feed is reported separately from 503/timeout transport failures and does not trigger automatic publication blocking.

## Test locally
`python -m unittest discover -s tests -p 'test_d19*_*.py'` or `python -m unittest discover -s tests -p 'test_d192_health.py'`.

## Safeguards
The correction activation gate remains `enabled=False`, with no modified geographic matching. Google News and publisher RSS sources remain unchanged. Review `data/feed-health-validation.json` after the next workflow run. A healthy dataset is not retroactively restored from the outage run.
