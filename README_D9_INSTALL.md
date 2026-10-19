# WorldPulse v2.4D.9 — Geographic Quality Assurance & Multi-Location Event Intelligence

## Direct upload
Upload these files into the *same paths* in your existing WorldPulse repository:

- `scripts/update.py` — **replace**.
- `scripts/geo_quality_d9.py` — **add**.
- `tests/d9_geo_benchmark.json` — **add**.
- `tests/test_d9_quality.py` — **add**.

Keep all v2.4D.4–D.8 scripts, and keep `.github/workflows/update.yml` unchanged. This is an **incremental patch**, not a whole-repository ZIP.

Use Actions → Refresh geographic news → Run workflow. Then inspect `data/feed-contribution-audit.json` → `d9_quality_assurance`.

## What D.9 changes

- Adds a permanent nine-case geographic *regression* benchmark based on known and synthetic examples. Pass rate is **not** an independent real-world geocoding precision metric.
- Separates headline, description, contextual and unsupported evidence categories for *already accepted* matches.
- Classifies international multi-country headlines for **audit only**, including select Italian/Belgian/Portuguese country words absent from the previous curated set.
- Audits location concentration from URL+selected-location deduplicated observations, including Vietnam counts. Does not automatically declare popular places erroneous.
- Reports sample international headlines and competing places **without creating extra globe pins**.

## Safety and limitations

No new automatic geography is accepted, no coordinates are inferred, and no articles are withheld by D.9. Existing v2.4D.4–D.8 guards remain authoritative. Raw feed observations include repeats; unique URL-location pairs can still be duplicates across syndication URLs. Full live Actions verification is required after upload.

## Offline test

From the repository root: `python -m unittest discover -s tests -p 'test_d9_quality.py'`
