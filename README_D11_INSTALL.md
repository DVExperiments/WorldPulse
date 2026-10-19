# WorldPulse v2.4D.11 — Global Publisher Diversity & Geographic Precision Audit

## Install (GitHub direct upload)
Upload these files with their folders preserved:

- `scripts/update.py` — **replace** the current file (based on D.10)
- `scripts/geo_diversity_d11.py` — **new**
- `tests/test_d11_diversity.py` — **new**

Keep all existing previous modules, JSON files, and `.github/workflows/update.yml`. There are **no workflow changes**.

In GitHub Actions, run **Refresh geographic news**, then open `data/feed-contribution-audit.json` and find `d11_publisher_diversity_geographic_precision`.

## Coverage

Unlike D.10's shortlist, **all places in the mapped RSS sample** are included, across all countries, regions, and localities already supported by the existing collector. Nothing is hard-coded to Vietnam. Each location includes:

- distinct URL/location pairs; repeated observations; sample share
- publisher counts, largest publisher's share, Herfindahl concentration index (HHI), Simpson effective publisher count, and top publisher names
- evidence provenance: headline, description, context/alias
- geographic level supplied by the existing gazetteer: country, region, place, or unknown
- RSS discovery editions and content categories, distinguished from event locations
- textual place-name candidates elsewhere in the headline drawn from the existing PLACES gazetteer
- a bounded set of review samples with description excerpts, URLs, evidence types and reasons
- ranked concentration review covering multiple locations; not just one publisher or country

## Important constraints

**AUDIT ONLY:** does not automatically remap, delete, limit, or create pins. Headline matches to other gazetteer names are *candidates*, not proof that the news event occurred there and not confirmed child locations of the assigned country.

The analysis uses RSS metadata and titles/descriptions, not full article bodies. Counts are tied to the **rolling feed sample**, not all world reporting. Publication names are only normalized for case and whitespace, not merged across publisher aliases. Different URLs may still represent the same syndicated story. A high share from one publisher is not, by itself, an error. Findings should be reviewed before any geocoding or ranking rule changes.

## Offline validation

Five D.11 tests, four D.10 tests, three D.9 tests pass. `update.py` and `geo_diversity_d11.py` compile. A live GitHub Actions execution is required to validate production integration and audit population.
