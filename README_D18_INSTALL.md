# WorldPulse v2.4D.18 — Controlled Activation & Geographic Precision Safeguards

## Default behavior: SHADOW ONLY
Upload the ZIP file contents to the **repository root** (not the folder itself):
- `scripts/update.py` REPLACE
- `scripts/geo_activation_d18.py` ADD
- `tests/test_d18_activation.py` ADD
- `data/d18-reviewed-approvals.json` ADD (defaults disabled, empty approvals)
- `README_D18_INSTALL.md` ADD (optional)

Keep D4–D17 modules; do not change `.github/workflows/update.yml`.
Run GitHub Actions > **Refresh geographic news**. Inspect `data/feed-contribution-audit.json` > `d18_controlled_activation`.

## Important limitations
- No correction is active on installation. The default approval manifest has `enable_live_corrections: false` and empty approvals; the environment variable is absent.
- Live correction is intentionally double-gated. **Do not enable** without manually reviewing original full article text and independent location evidence, and obtaining explicit authorization.
- `d18_controlled_activation.projected_review_samples` reports candidate serialized entries. Numbers do not imply verified false matches.
- D18 does **not** conduct full-article validation, automatically relocate anything, or enable global publisher metadata isolation.
- If manually enabled in a future authorization, D18 filters selected serialized article entries only, not the upstream deduped dataset. Aggregate pipeline counts, diagnostic numbers and some signal metrics are pre-correction. Do not enable on article groups capped at 20 without further full-pipeline consistency testing. This is not yet production certified.

## Future optional activation procedure (not authorised by this release)
1. Read full articles and evidence. Record only confirmed false geographic assignments in `data/d18-reviewed-approvals.json` (max 20). Each must contain exact `url`, `place`, `manual_article_review:true`, and `rule` (`spanish_lagos_lakes` or `spanish_reunion_meeting`). Also set `enable_live_corrections:true`.
2. Separately configure `WORLDPULSE_D18_ENABLE_APPROVED_CORRECTIONS=1` in the collector environment. This is deliberately **not** set by the shipped GitHub Action and is not exposed as a ready click-to-enable workflow input.
3. Re-run and review `d18_controlled_activation.actual_removed_entries`, then separately validate UI, signal metrics and coverage.

## Rollback
Unset the environment variable (or set it to `0`) OR set `enable_live_corrections:false` in the manifest, and rerun the workflow. Removing the D18 import/invocation and restoring D17 `scripts/update.py` also reverts the collector. GitHub commit history provides a version rollback.

## Local checks
`python -m pytest -q tests/test_d18_activation.py tests/test_d17_pilot.py`
