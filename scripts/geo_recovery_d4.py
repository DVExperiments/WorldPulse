"""WorldPulse D.4: high-precision geographic recovery and non-destructive feed audit.

No external geocoding, no location guesses based on publisher or news edition.
Only qualified literal country references (not adjectives) are considered.
"""
from __future__ import annotations
import re
import unicodedata
from collections import Counter

# All targets must exist unambiguously in the repository's existing place index.
# Country-code substrings or ambiguous names are intentionally NOT supported.
EXPLICIT_COUNTRIES = {
    'méxico': ('Mexico', 'México'),
    'brasil': ('Brazil', 'Brasil'),
    'españa': ('Spain', 'España'),
    'portugal': ('Portugal',),
    'argentina': ('Argentina',),
    'colombia': ('Colombia',),
    'chile': ('Chile',),
    'perú': ('Peru', 'Perú'),
    'peru': ('Peru', 'Perú'),
    'nueva zelanda': ('New Zealand',),
    'áfrica do sul': ('South Africa',),
    'africa do sul': ('South Africa',),
    'afrique du sud': ('South Africa',),
    'états-unis': ('United States', 'USA'),
    'estados unidos': ('United States', 'USA'),
}
# Explicit containment or topic phrases; no unrestricted name matching.
PREFIXES = ('en', 'em', 'no', 'na', 'nos', 'nas', 'au', 'aux', 'dans', 'de', 'do', 'da', 'del', 'desde', 'in', 'across', 'throughout')
PREFIX_RX = '(?:' + '|'.join(PREFIXES) + ')'

def _fold(value):
    value=unicodedata.normalize('NFKD',value.casefold())
    return ''.join(ch for ch in value if not unicodedata.combining(ch))

# Preserve explicit phrase boundaries; matching a country adjective alone is unsafe.
def recover_explicit_geography(title, description, places):
    indexes={}
    for p in places:
        if p.get('level')!='country':
            continue
        indexes.setdefault(_fold(p.get('name','')),[]).append(p)
    for field_name, field in (('headline',title),('description',description)):
        folded=_fold(re.sub(r'<[^>]*>', ' ', field or ''))
        found=[]
        for alias, names in EXPLICIT_COUNTRIES.items():
            term=_fold(alias)
            rx=r'(?<!\w)'+PREFIX_RX+r'\s+(?:the\s+|el\s+|la\s+|los\s+|las\s+|o\s+|a\s+)?'+re.escape(term)+r'(?!\w)'
            if re.search(rx,folded):
                matches=[]
                for name in names:matches.extend(indexes.get(_fold(name),[]))
                unique={(_fold(p.get('name','')),p.get('lat'),p.get('lng')):p for p in matches}
                if len(unique)==1: found.append((next(iter(unique.values())),alias))
        distinct={(_fold(p.get('name','')),p.get('lat'),p.get('lng')):(p,alias) for p,alias in found}
        # Conflicting countries in same field are ambiguous; don't choose one.
        if len(distinct)==1:
            p,alias=next(iter(distinct.values()))
            return p,{'field':field_name,'explicit_phrase':alias,'method':'qualified_country_phrase'}
        if len(distinct)>1:return None
    return None

def diagnose_unmatched(title,description):
    if not (title or '').strip():return 'empty_headline'
    if re.search(r'\b(?:globally|worldwide|internationally|global)\b',(title or '').casefold()):return 'global_or_nonlocal_topic'
    if len((description or '').strip())<25:return 'limited_description_evidence'
    return 'insufficient_unambiguous_location_evidence'

def summarize_efficiency(feeds):
    totals=Counter()
    for f in feeds:totals[f.get('usefulness','unknown')]+=1
    overlap=[]
    for f in feeds:
        duplicates=f.get('duplicate_canonical',0)+f.get('duplicate_near_title',0)
        mapped=f.get('geography_matched',0)
        if duplicates or mapped:
            overlap.append({'feed':f['feed'],'mapped':mapped,'survived':f.get('deduplication_survived',0),'duplicate_canonical':f.get('duplicate_canonical',0),'duplicate_near_title':f.get('duplicate_near_title',0),'loss_attribution':sorted(f.get('lost_to_feeds',{}).items(),key=lambda x:-x[1])[:5],'duplicate_share_pct':round(100*duplicates/mapped,1) if mapped else None})
    return {'usefulness_classes':dict(totals),'overlap_by_feed':overlap,'policy':'Observation only: no automatic feed removal or priority changes; duplicates are order-dependent and may provide fallback resilience.'}
