# WorldPulse v2.4D.20 — Verified Geographic Correction Pilot (shadow only)

## Upload
Upload the folder contents at the repository root. Replace `scripts/update.py`; add `scripts/geo_review_d20.py`, `tests/test_d20_review.py`, `data/d20-review-evidence.json` and this README. **Retain all D4–D19.2 modules.**

No changes needed to `.github/workflows/update.yml` for existing audit reporting: `d20_verified_correction_pilot` is embedded in `data/feed-contribution-audit.json`. The separately generated `data/d20-correction-validation.json` is optional and will not appear in GitHub unless explicitly staged by your workflow; the embedded audit is authoritative.

## Safety and validation
No live corrections. The review JSON defaults to an empty list. Three familiar Lagos/Réunion RSS examples are **candidates, not human-reviewed confirmations**. The system never claims to have read full articles, and a review entry must be entered by an actual person after full-article source inspection. A review record includes `url`, `place`, `rule`, `reviewer`, `reviewed_at` (offset-aware ISO 8601), `article_access`, `source_url`, `source_title`, `source_evidence`, `location_evidence`, `independent_geography_check`, and `conclusion`.

Valid rules are `spanish_lagos_lakes` for Lagos and `spanish_reunion_meeting` for Réunion. A `confirmed_false_match` only qualifies for hypothetical withholding when the full article was read, supporting evidence is documented, and an independent geography check is asserted. Unreviewed or ambiguous records are untouched. The review file does not feed into the D18 activation manifest.

D20 runs a nonzero-removal **synthetic** frozen-fixture rehearsal: (1) removes one false location mention and rebuilds local counts and velocity, (2) refuses to mutate a capped signal lacking underlying articles, (3) removes an empty group, (4) checks snapshot immutability and rollback. It separately analyzes real current RSS candidates, with **zero verified removals** until review records are entered.

## Limits
Full review provenance is user-entered, not independently authenticated by this patch. Local group simulation is not a full upstream rebuild of source-feed metrics, cross-border links, clusters or histories. It does not authorize production activation.

Run GitHub Actions workflow **Refresh geographic news** and review `d20_verified_correction_pilot` inside `data/feed-contribution-audit.json`.
