# WorldPulse v2.0E — Geographic Intelligence Expansion

**Collector-only patch for the ORIGINAL `DVExperiments/WorldPulse` GitHub repository.** Do **not** upload these files to `WorldPulse-2`.

## Included
- `scripts/geo_expansion.py` — reviewed geographic fallback containing **158 place/region entries**, with distinctive multilingual variants and boundaries. Names are geographic *subjects*, not verified incident locations. No third-party runtime dependency, API key, or geocoding request.
- `scripts/apply_e_patch.py` — fail-closed, repeat-safe installer for the D.6.1 collector.
- `scripts/audit_e_samples.py` — optional offline unmatched-headline sample audit.
- `tests/test_e.py` — ten regression tests.

## Installation
1. Upload the three `scripts/*.py` files to the original repo's `scripts/` folder; upload `tests/test_e.py` to `tests/`. Commit uploads on GitHub.
2. Open **original WorldPulse** Codespace, and run:
   ```bash
   git pull origin main
   python scripts/apply_e_patch.py
   python -m py_compile scripts/update.py scripts/geo_expansion.py
   python -m unittest discover -s tests -p 'test_e.py' -v
   git diff -- scripts/update.py
   ```
3. If installation and tests succeed, commit only modified collector file:
   ```bash
   git add scripts/update.py
   git commit -m "Add v2.0E geographic recognition expansion"
   git push origin main
   ```
4. Go to original `WorldPulse` Actions and run **Refresh geographic news**. Inspect `data/unmatched-review.json` > `geo_intelligence` > `mapping_methods`: watch for **`method/headline-expanded`** and **`method/description-expanded`**. The counts are per-feed, before deduplication. These methods may appear even when distinct mapped article counts are unchanged.

## Optional offline audit
```bash
python scripts/audit_e_samples.py data/unmatched-review.json
```
Shows how many *sampled* headlines the v2.0E fallback could recognise. This is not a prediction of distinct live article recoveries. On the supplied 120-example D.4 file, 12 had names recognised by the expanded table, but **several were already covered by D.6**; they are not all new recoveries.

## Deliberate limits
- This patch **does not replace or refactor** existing `locate`, global geography, multilingual, or D.6 matching layers. It runs **only if all earlier matchers fail**. Therefore it cannot correct inaccurate older matches; this requires a separate audit/refactor.
- It does not change the 24-hour globe window, 72-hour Discover window, 350-story limit, publisher attribution, JSON structure, GitHub Actions, or WorldPulse-2 website.
- No location is invented from the publisher's country, article feed edition, or a generic place word.
- When the expanded matcher sees **more than one distinct place** in the same headline/description, it declines to choose one. Existing older matchers may behave differently.
- Coordinates represent cities or approximate region anchors, **not verified incident coordinates**.
- This is a reviewed 158-entry expansion, **not** a complete global gazetteer or NLP entity recogniser.

## Verification
Ten tests passed; installation was checked for safe repeat execution and collector Python syntax on a local reconstructed D.6.1 copy. Live feed and browser testing have **not** been run from this patch package.
