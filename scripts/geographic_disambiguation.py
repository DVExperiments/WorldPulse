"""Conservative final-stage checks for names that commonly are not geographic.

Only applied to selected ambiguous single-word gazetteer labels. The check does
not attempt to verify an incident location, only an explicit geographic subject.
"""
from __future__ import annotations

import re
from typing import Mapping

# Intentionally short, auditable set. Add only after reviewing real false positives.
AMBIGUOUS = frozenset({
    'rubio', 'david', 'forest', 'union', 'sunrise', 'reading',
    'nice', 'mobile', 'victoria', 'jordan', 'georgia', 'turkey',
    'hassan', 'serra', 'split',
})

# Adjacent geography signals, not mere co-occurrence anywhere in the article.
_PREPOSITIONS = r'(?:in|near|around|outside|across|within|throughout)'
_ADMIN = r'(?:city|town|village|municipality|province|county|district|region)'


def accepted_geographic_context(name: str, text: str) -> bool:
    """Require nearby place-indicating wording for especially ambiguous names."""
    if not name or not text:
        return False
    escaped = re.escape(name)
    boundary = rf'(?<!\w){escaped}(?!\w)'
    forms = (
        rf'\b{_PREPOSITIONS}\s+(?:the\s+)?{boundary}\b',
        rf'\b{_ADMIN}\s+of\s+{boundary}\b',
        rf'{boundary}\s+{_ADMIN}\b',
        # Unambiguous known country qualifier, not any arbitrary capitalised word.
        rf'{boundary}\s*,\s*(?:Panama|Venezuela|Belgium|France|Canada|USA|United States|UK|India)\b',
    )
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in forms)


def evaluate(place: Mapping, title: str, description: str = '') -> tuple[bool, str]:
    """Return (accepted, reason); ordinary/non-ambiguous labels pass unchanged."""
    name = str(place.get('name', '')).strip()
    if name.casefold() not in AMBIGUOUS:
        return True, 'not_ambiguous'
    if accepted_geographic_context(name, title):
        return True, 'headline_place_context'
    if accepted_geographic_context(name, description):
        return True, 'description_place_context'
    return False, 'ambiguous_name_without_geographic_context'
