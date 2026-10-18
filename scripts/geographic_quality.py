"""WorldPulse D.6: conservative missing-place recovery and diverse browse sampling.
Coordinates are approximate geographic *subject* anchors, never verified incidents.
"""
import re
import unicodedata
from collections import Counter

# Explicit, geographically distinctive labels observed in unmatched-review samples.
# Do not expand this automatically from publisher origin or edition information.
PLACES = (
    ('Gujarat', 23.22, 72.64, 'region', ('gujarat',)),
    ('West Bengal', 22.99, 87.86, 'region', ('west bengal', 'paschim banga')),
    ('Balochistan', 28.49, 65.10, 'region', ('balochistan',)),
    ('Kudat', 6.88, 116.85, 'place', ('kudat',)),
    ('Kisoro', -1.28, 29.68, 'place', ('kisoro',)),
    ('Worcestershire', 52.19, -2.22, 'region', ('worcestershire',)),
    ('Bozeman', 45.68, -111.04, 'place', ('bozeman',)),
    ('Embu County', -0.53, 37.46, 'region', ('embu county',)),
    ('County Down', 54.33, -5.72, 'region', ('county down',)),
    ('Pennsylvania', 40.90, -77.80, 'region', ('pennsylvania',)),
    ('Sabah', 5.98, 116.08, 'region', ('sabah',)),
    ('Whangārei', -35.73, 174.32, 'place', ('whangarei', 'whangārei')),
)

def fold(s):
    s = unicodedata.normalize('NFKD', str(s or '').casefold())
    return ''.join(c for c in s if not unicodedata.combining(c))

def curated_match(title, description=''):
    """Conservative explicit headline match, fallback to distinct description match."""
    for label, text in (('headline-curated', title), ('description-curated', description)):
        clean = fold(re.sub(r'https?://\S+', ' ', text or ''))
        matches = []
        for name, lat, lng, level, aliases in PLACES:
            for alias in aliases:
                if re.search(r'(?<!\w)'+re.escape(fold(alias))+r'(?!\w)', clean):
                    matches.append((len(alias), {'name':name,'lat':lat,'lng':lng,'level':level}))
                    break
        # If two distinct places match, don't assume which is the subject.
        places = {m[1]['name']:m[1] for m in matches}
        if len(places) == 1:
            return next(iter(places.values())), label
        if len(places) > 1:
            return None, 'ambiguous-curated'
    return None, 'unmapped'

def balanced_select(rows, cap=350, publisher_soft_cap=12):
    """Two-pass newest-first, bounded selection with no publisher-home geocoding.

    First pass offers smaller publishers a chance; remaining slots are filled
    newest-first. This improves source variety, not measured geographic variety.
    """
    ordered = sorted(rows, key=lambda r:r['published_at'], reverse=True)
    chosen=[]; seen=set(); pubs=Counter()
    for row in ordered:
        p = (row.get('publisher') or 'Unknown').casefold().strip()
        key = row['url']
        if key in seen or pubs[p] >= publisher_soft_cap: continue
        chosen.append(row); seen.add(key); pubs[p]+=1
        if len(chosen)>=cap:break
    if len(chosen)<cap:
        for row in ordered:
            if row['url'] in seen: continue
            chosen.append(row); seen.add(row['url'])
            if len(chosen)>=cap:break
    chosen.sort(key=lambda r:r['published_at'],reverse=True)
    by_pub=Counter((r.get('publisher') or 'Unknown') for r in chosen)
    stats={'distinct_publishers':len(by_pub),
           'top_publisher_share_pct':round(100*max(by_pub.values(),default=0)/len(chosen),1) if chosen else 0,
           'top_publishers':dict(by_pub.most_common(12)),
           'method':'publisher-balanced two-pass sampling, not geographic inference'}
    return chosen,stats
