WorldPulse v2.0F.4.5 — Relationship Accuracy Refinement

Upload ONLY:
  scripts/cross_border.py -> DVExperiments/WorldPulse / scripts /
  tests/test_f45.py -> DVExperiments/WorldPulse / tests / (optional)

Do not replace scripts/update.py or modify the workflow.
Commit, then run the existing Refresh geographic news GitHub Action.
This is compatible with F.4 collector import and adds relationship_label and
relationship_explanation to cross_border.links entries without altering country
coordinates, article URLs, or other news feed content.

Example: Sanctions waiver is labelled a waiver; "on hold" is labelled delayed;
ambassador speech is labelled diplomatic statement, not an agreement.
These are headline-derived labels, not fact-checked factual claims.
