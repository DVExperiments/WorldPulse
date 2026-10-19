# WorldPulse v2.4D.19 — Correction Integrity & Reviewed-Article Validation

## IMPORTANT: all live corrections are forcibly OFF
This release adds a non-mutating, frozen-snapshot correction simulation. It **forces D18's `enabled=False`** in the collector, so an accidentally set environment switch cannot turn on filtering. D18's ordinary approval manifest remains disabled. The new D19 review manifest is **not** a live approval mechanism.

## Direct GitHub upload
Extract the ZIP and upload its contents (the files, not a surrounding folder) to the repository root:

| Repository path | Action |
|---|---|
| `scripts/update.py` | Replace |
| `scripts/geo_integrity_d19.py` | Add |
| `tests/test_d19_integrity.py` | Add |
| `data/d19-reviewed-articles.json` | Add, empty by default |
| `README_D19_INSTALL.md` | Optional |

Keep all D4–D18 modules and `data/d18-reviewed-approvals.json`. Leave `.github/workflows/update.yml` unchanged. Manually run the **Refresh geographic news** action and inspect `data/feed-contribution-audit.json` → `d19_correction_integrity`.

## Review documentation
Do not enter a false-match conclusion from a title or RSS description alone. To record a confirmed false match, read the full article and document independent geographic evidence. Each row under `reviews` must include:

- `url`: exact `https://` URL from D17's serialized candidate list;
- `place`: `Lagos` or `Réunion` (exact selected place);
- `rule`: `spanish_lagos_lakes` or `spanish_reunion_meeting`;
- `reviewer`: person or review identifier;
- `reviewed_at`: review date;
- `article_access`: `full_article`, `rss_only`, or `unavailable`;
- `source_evidence`: short factual summary or verified excerpt of complete article;
- `location_evidence`: description of country/place evidence, including any contrary signs;
- `conclusion`: `confirmed_false_match`, `valid_match`, or `uncertain`.

Only a `confirmed_false_match` with `article_access: "full_article"` is counted as potentially removable in the **shadow** simulation. This JSON is never consulted to activate a live filter.

## Count and rollback consistency
- D19 takes a frozen copy and computes a SHA-256 fingerprint before simulation.
- It reports visible article counts, hypothetical group disappearance, and before/after group totals.
- A capped group (`count > serialized articles`) cannot be safely recomputed from its truncated article list: D19 treats the correction as *unsafe* and does not hypothetically remove it.
- Even uncapped groups require activity-metric recomputation (relative to snapshot time), so D19 reports those integrity blockers and leaves actual published data intact.
- Rollback is tested by deep-copying the frozen original and checking the same logical snapshot fingerprint. This validates the pure simulation; it is not an end-to-end GitHub rollback test.
- Existing pipeline-level historic/audit counts are unchanged; **do not interpret D19 as production certification for live filtering**.

## Tests and rollback
Run `python -m unittest discover -s tests -p 'test_d19*.py' -v` locally. To revert the patch, restore D18's `scripts/update.py` via GitHub history and remove D19's new files; no output corrections were ever activated by D19.
