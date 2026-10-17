# WorldPulse v1.4A — Global Coverage Expansion

GitHub Pages compatible. This release adds independent editorial RSS alongside Google News regional RSS queries, feed health reporting, headline deduplication across categories, sampled source diversity, and a compact 30-day archive of daily collection statistics. Existing 3D globe, v1.3 format, categorization, clustering and velocity are maintained.

## Install

Upload the contents of this folder into the **root** of the existing GitHub repository, replacing files where prompted. Keep only **one** workflow in `.github/workflows/` (replace your existing workflow content rather than adding another). Then Actions → Refresh geographic news → Run workflow.

## Files

- `scripts/update.py`: multi-source RSS collector (standard Python library only).
- `data/places.json`: existing gazetteer.
- `data/news.json`: generated 24-hour view (preserved until next successful run).
- `data/source-health.json`: feed status, counts and errors.
- `data/history.json`: compact daily maxima of **sampled** mapped articles (NOT complete daily story totals).

## What the numbers mean

RSS responses are ranked, limited samples. Article timestamps may be absent or inaccurate, and a place mentioned in a headline may not be the event's true location. Exact URL duplicates and very similar same-place titles are collapsed; syndicated stories and semantic duplicates can remain. Counts and velocity are **not global census metrics**. A daily historical maximum is not the total unique stories that day. Source counts use returned publisher labels and can count alternate names separately. A feed failure produces partial status rather than erasing successful results. The Globe panel presents a location's stories with source links. The social activity layer remains intentionally unconnected.

## Source coverage

Configuration includes 28 region-specific Google News searches plus 23 direct feeds (including some French, Spanish and Portuguese), whose availability varies. A working feed doesn't guarantee any geographically matched articles. Failed feeds are listed in `data/source-health.json`. News source content and original links belong to their publishers. No article bodies are copied.

## Limitations and next steps

This is a discovery interface, not a fact verification engine. Geographic matches are conservative but not geolocation proof; multilingual headlines may need additional alias dictionaries. To make a meaningful overlooked-stories analysis, the next phase should maintain event identities, source market baselines, and normalized coverage shares; don't infer intentional suppression from a coverage decline.
