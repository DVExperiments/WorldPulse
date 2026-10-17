WORLDPULSE V1.2 — RSS DATA COLLECTOR PATCH

1. Open https://github.com/DVExperiments/WorldPulse/blob/main/scripts/update.py
2. Click Edit (pencil), select all, replace with the contents of scripts/update.py from this ZIP.
3. Commit directly to main.
4. Actions > Refresh geographic news > Run workflow.
5. Check log for 'RSS read' and 'Wrote N points ... status=live'.
6. Verify data/news.json shows source 'Google News RSS' and points is nonempty.

Only scripts/update.py MUST be replaced. You do not have to upload the .github folder.
The existing workflow step will still say 'Fetch GDELT geographic coverage' because that
is just its display label; it will actually execute this new RSS collector.

Limitations:
- Uses a sample of English-language Google News RSS search results.
- Markers appear only when a headline contains a known place name.
- Counts are article links observed in a 24-hour sample, not complete geographic news counts.
- RSS URLs sometimes link through Google News rather than directly to publishers.
- A country name's position on the globe is a representative anchor, not the event coordinate.
- News RSS availability can vary; if it fails, the log now reports the specific RSS error.
- This patch cannot be live end-to-end tested from the authoring environment.
