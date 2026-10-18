"""Conservative supplementary geography matcher for WorldPulse.

No publisher-home inference. No country guessing from language. Returns only
explicit place names in article title, summary or supported URL path patterns.
"""
from __future__ import annotations
import re
import unicodedata
from urllib.parse import urlsplit, unquote

BLOCK = {'nice', 'reading', 'mobile', 'turkey', 'georgia', 'jordan', 'victoria',
         'orange', 'china', 'us', 'usa', 'uk', 'eu', 'may', 'march', 'new', 'home',
         'news', 'world', 'international', 'state', 'press', 'washington'}

def folded(text):
    # Preserve punctuation word boundaries, but treat accented and plain spellings alike.
    return ''.join(c for c in unicodedata.normalize('NFKD', text.casefold())
                   if not unicodedata.combining(c))

def safe_candidates(places):
    names = {}
    for place in places:
        name = str(place.get('name', '')).strip()
        plain = folded(name)
        if len(plain) < 5 or plain in BLOCK or not re.search(r'[a-z]', plain):
            continue
        names.setdefault(plain, []).append(place)
    # Duplicate place names can refer to different regions. Avoid choosing arbitrarily.
    return sorted(((name, options[0]) for name, options in names.items() if len(options) == 1),
                  key=lambda x: len(x[0]), reverse=True)

def find_explicit(title, description, url, places):
    candidates = safe_candidates(places)
    for source, text in [('title-normalized', title), ('description-normalized', description)]:
        clean = folded(text or '')
        for name, place in candidates:
            if re.search(r'(?<!\w)' + re.escape(name) + r'(?!\w)', clean):
                return place, source
    # URL fallbacks are intentionally restricted to clearly geographical path segments.
    # Do not treat a news publisher's domain, language or editorial edition as location.
    try:
        path = unquote(urlsplit(url).path).strip('/').lower().split('/')
    except (ValueError, TypeError):
        return None, 'unmapped'
    tokens = []
    for index, segment in enumerate(path):
        if index > 0 and path[index-1] in ('place', 'places', 'location', 'locations', 'city', 'cities', 'country', 'countries'):
            tokens.append(segment)
    for token in tokens:
        normal = folded(re.sub(r'[-_]+', ' ', token))
        for name, place in candidates:
            if normal == name:
                return place, 'url-explicit-geography'
    return None, 'unmapped'
