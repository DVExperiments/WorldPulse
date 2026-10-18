# WorldPulse 2.0D.6 — Geographic Recognition & Coverage Quality

**Upload ONLY to the original `DVExperiments/WorldPulse` repository**. Do not upload to WorldPulse-2.

Requires D.5 (`scripts/browse_retention.py`) already installed.

## Features
- 12 curated geographic entries, including Gujarat, West Bengal, Balochistan, Kudat, Kisoro, Worcestershire, and Whangārei. The conservative fallback only runs when the earlier matcher failed. Geographic points represent approximate subjects, NOT verified incident coordinates. Ambiguous multiple curated references remain unlocated.
- Publisher-balanced Browse-only selection: first pass selects up to 12 stories per publisher, then fills unused slots by recency. The existing 350-story cap remains unchanged. This improves publisher diversity, NOT proven country diversity.
- The existing `browse_retention` section in `data/news.json` gains `publisher_balance` with publisher variety, largest-publisher share, and leading publisher counts.
- The globe's 24-hour rule and Discover's 72-hour retention remain unchanged. No GitHub Actions workflow or frontend changes.

## Install
1. Extract the ZIP. Upload `scripts/geographic_quality.py` and `scripts/apply_d6_patch.py` to the original repo's `scripts` directory. Upload `tests/test_d6.py` to `tests` if desired. Commit the upload.
2. Open a Codespace for ORIGINAL WorldPulse and run:

```bash
git pull origin main
python scripts/apply_d6_patch.py
python -m py_compile scripts/update.py scripts/browse_retention.py scripts/geographic_quality.py
python -m unittest discover -s tests -p 'test_d6.py'
git diff -- scripts/update.py scripts/browse_retention.py
```

3. If successful, commit only the two modified files:

```bash
git add scripts/update.py scripts/browse_retention.py
git commit -m "Add D6 geographic quality and balanced story selection"
git push origin main
```

4. Run **Refresh geographic news** in GitHub Actions, then inspect `data/news.json` > `browse_retention` > `publisher_balance` and `data/source-health.json` mapping counts.

## Safety
- Do NOT upload `node_modules`, `dist`, or replace the original workflow.
- Publication timestamps are not modified. Unlocatable stories remain browse-only.
- This patch does not independently verify publisher reports. Do not infer article location from the publisher's country.
- Exact place candidate coordinates are representative region/city anchors, not event sites.
- Measured improvements require a live collection run; unit tests alone do not establish mapping gains.
