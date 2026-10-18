# WorldPulse 2.0F.1 — conservative multi-source story clustering

**Target: original `DVExperiments/WorldPulse` collector only.** Requires v2.0E.4 installed. Does NOT change mapping, geography or existing globe signals.

## Install
1. Extract ZIP. Upload `scripts/story_clustering.py`, `scripts/apply_f1_patch.py`, `tests/test_f1.py` to the matching paths in ORIGINAL WorldPulse on GitHub. Commit.
2. Codespace commands:

```bash
git pull origin main
python scripts/apply_f1_patch.py
python -m py_compile scripts/update.py scripts/story_clustering.py
python -m unittest discover -s tests -p 'test_f1.py' -v
git add scripts/update.py
git commit -m "Add F1 multi-source story grouping"
git push origin main
```
3. Run Actions > `update.yml` > **Refresh geographic news**. The next `data/news.json` includes a `story_clusters` array at the root.

## Mechanics and limitations
- Uses only the up-to-20 **published article previews per mapped location/category** in `data/news.json`, not all fetched RSS articles. News feed deduplication occurs first.
- Requires two different publishers, a single matching geographic subject + category, strong headline token overlap (Jaccard >= 0.68, at least 3 shared meaningful tokens), publication dates within 36 hours of each other. Does not use summaries, URL domains, Google edition or publisher headquarters to infer event places.
- Does not cluster unlocated browse-only articles in F.1. Does not cluster across regions or categories. Does not merge loosely related headlines and may miss real multi-source stories with different wording. No external APIs, embeddings or paid services.
- Published group names are existing story headlines; clusters are similarities, not verified common events. Each original article retains its link. Group IDs may change as source articles rotate.
- If few or no groups appear, this is an expected conservative outcome, not necessarily a broken collector.
