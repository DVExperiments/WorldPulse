# WorldPulse 2.0D.6.1 — Publisher Metadata Correction

**Target:** original `DVExperiments/WorldPulse` collector repository, **not** `WorldPulse-2`.

## Purpose
- Recover missing RSS publisher names from the configured direct-feed name or a short, audited list of article hostnames.
- Preserve existing trustworthy article publisher fields.
- Do **not** infer publishers from Google News redirect URLs, unknown domains, article subject matter, or the geographic location of news events.
- Resolve publisher **before** retention/balancing, so publisher variety measurements become more meaningful.
- No changes to globe, article freshness window, map coordinates, feed requirements or Github Actions workflow.

## Install
1. Extract ZIP. Upload `scripts/publisher_metadata.py` and `scripts/apply_d61_patch.py` to existing `scripts/` directory in original WorldPulse repo. Upload `tests/test_d61.py` to existing `tests/` (create tests folder if necessary). Commit the uploaded files in GitHub.
2. In original WorldPulse Codespace terminal:

```bash
git pull origin main
python scripts/apply_d61_patch.py
python -m py_compile scripts/update.py scripts/publisher_metadata.py
python -m unittest discover -s tests -p 'test_d61.py' -v
git diff -- scripts/update.py
```

3. If those pass, commit the collector's updated import and ingestion line:

```bash
git add scripts/update.py
git commit -m "Correct browse article publisher attribution"
git push origin main
```

4. In Actions run **Refresh geographic news**. Then inspect `data/news.json` > `browse_retention` > `publisher_balance` and `unlocated_articles` > `publisher`.

**Success checks:** fewer `Unknown` browse-only entries, a sensible set of identified publishers, no unexpected increase in news map points purely from metadata, and standard 132/136-ish feed health (feed availability varies).

## Expected effect, not guaranteed live count
An offline pass on the 2.0D.6 `news.json` snapshot recovered **115 of 129** empty publisher names among its 350 browse-only articles. There were 14 remaining after domain matching. The live output can differ because selection is performed again after repair, and articles change between runs.

## Safety notes
The installer refuses to proceed if D.6 `balanced_select` integration or known update.py insertion points are absent. Running it twice does not duplicate the patch. No tracked data files are overwritten during installation. The Python code is standard-library only.
