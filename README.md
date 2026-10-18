# WorldPulse 2.0D.5 — Collector PATCH (original WorldPulse repository ONLY)

This ZIP contains **only** `scripts/browse_retention.py` and `scripts/apply_d5_patch.py`.

1. In `DVExperiments/WorldPulse` (NOT WorldPulse-2), upload these two files directly into the existing `scripts/` directory, then commit.
2. Open your original WorldPulse Codespace, run `git pull origin main` and `python scripts/apply_d5_patch.py`.
3. If successful, run `python -m py_compile scripts/update.py scripts/browse_retention.py` then `git diff -- scripts/update.py`.
4. Commit only the modified file: `git add scripts/update.py && git commit -m "Add 72-hour browse-only news retention" && git push origin main`.
5. In GitHub Actions, run **Refresh geographic news**. Confirm `data/news.json` includes `unlocated_articles` and `browse_retention` with sensible counts.

The patch **stops without modifying files** if it sees unexpected collector code. Do not replace `update.py` manually, and do not upload this patch to WorldPulse-2.

## Design/limits
- The globe's 24-hour eligibility and map placement logic remain unchanged.
- Valid eligible-but-unmapped articles enter a separate browse-only collection.
- Articles between 24 and 72 hours old also become browse-only entries, clearly marked `archive`.
- Undated, far-future, malformed or over-72-hour articles are excluded.
- Up to 350 title-deduplicated browse entries (across feeds), sorted newest first, stored **inside the existing `data/news.json`**. No workflow changes needed.
- Geographic coordinates are never invented, and archive entries are **not breaking news**.
- Google News may repeat the same story under variant headlines. Count is a sampled browse collection, not the total news worldwide.
- This improves browsing coverage, but does not fix publishers emitting *only* articles older than 72 hours or provide locations for unlocated stories.
