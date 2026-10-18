"""D.6.1: conservative publisher attribution, never a geographic inference.

Prefer publisher supplied in RSS; for independent direct feeds use configured feed name;
for other direct URLs use a small audited hostname mapping. Google News redirect
URLs cannot identify the real publisher and are intentionally left unknown.
"""
from urllib.parse import urlsplit

HOST_NAMES = {
    'abc.net.au': 'ABC News Australia',
    'rnz.co.nz': 'RNZ',
    'france24.com': 'France24',
    'bbc.com': 'BBC',
    'bbc.co.uk': 'BBC',
    'theguardian.com': 'The Guardian',
    'aljazeera.com': 'Al Jazeera',
    'npr.org': 'NPR',
    'dw.com': 'DW',
    'cbc.ca': 'CBC News',
    'mongabay.com': 'Mongabay',
    'theconversation.com': 'The Conversation',
    'africanews.com': 'Africanews',
    'apnews.com': 'AP News',
    'reuters.com': 'Reuters',
    'un.org': 'UN News',
    'nasa.gov': 'NASA',
}

def clean_name(value):
    return ' '.join(str(value or '').split())[:120]

def publisher_for(item, feed_name='', source_kind=''):
    explicit = clean_name(item.get('publisher'))
    if explicit and explicit.casefold() not in {'unknown','n/a','none','null'}:
        return explicit, 'rss'
    # A named, directly fetched RSS feed provides explicit publisher provenance.
    if source_kind == 'publisher':
        named = clean_name(feed_name)
        if named:
            return named, 'direct_feed'
    try:
        url = urlsplit(item.get('url') or '')
        host = (url.hostname or '').lower().rstrip('.')
    except (ValueError, TypeError):
        return '', 'unresolved'
    if url.scheme not in ('https','http'):
        return '', 'unresolved'
    host = host[4:] if host.startswith('www.') else host
    if host in HOST_NAMES:
        return HOST_NAMES[host], 'recognised_domain'
    return '', 'unresolved'

def annotate(item, feed_name='', source_kind=''):
    # No destructive modification; use the result in both mapped and browse paths.
    name, _ = publisher_for(item, feed_name, source_kind)
    return {**item, 'publisher': name}
