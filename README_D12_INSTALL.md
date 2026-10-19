# WorldPulse v2.4D.12 — Publisher Metadata Isolation & Geographic Evidence Integrity

## Direct-upload patch for existing WorldPulse v2.4D.11 installation

Upload files preserving these exact paths:
- `scripts/update.py` — replace existing
- `scripts/geo_integrity_d12.py` — NEW
- `tests/test_d12_integrity.py` — NEW

Keep all D4–D11 modules (including `scripts/geo_diversity_d11.py`) and all other repository files. Do not overwrite `.github/workflows/update.yml`.

Then run **Actions → Refresh geographic news → Run workflow**. Open `data/feed-contribution-audit.json`, find `release: v2.4D.12` and `d12_publisher_metadata_integrity`.

## How the shadow audit works
- Applied to already accepted, mapped feed entries after D4–D8 safety rules, prior to deduplication.
- Identifies publisher source hostnames and publisher-like trailing credits in RSS `description` fields.
- Reruns only the candidate geographic matching chain using the cleaned description.
- Reports same-location, lost-location, and changed-location *candidate* results; **does not alter the live selected location**.
- Deduplicates diagnostic output by URL and original location, and reports all places plus up to 100 review examples.
- Domain cleanup is limited to identifiable publisher domains from `source_url` / publisher metadata. Some feed-specific boilerplate will not be detected, by design.
- The shadow calculation does not replay the stateful prior correction pipeline (`decision_audit.decide`) or final D6–D8 guards. Therefore results are a **triage signal, not a guaranteed final output diff**.
- No publisher-country inference is added. No live globe pins, URLs, thresholds, workflows or UI changes.

## Local verification
`python -m pytest -q tests/test_d12_integrity.py`

## Follow-up
Review affected examples before proposing live activation. Genuine national references in prose must remain admissible even if the publisher's name or domain also includes that country.
