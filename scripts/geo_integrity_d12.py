"""D.12 publisher metadata isolation, shadow-only diagnostics; never writes live locations."""
from collections import Counter, defaultdict
from urllib.parse import urlsplit
import re

DOMAIN = re.compile(r'(?<![\w@])(?:https?://)?(?:www\.)?([a-z0-9][\w-]*(?:\.[a-z0-9][\w-]*)+)(?![\w])',re.I)

def hostname(value):
    if not value: return ''
    s=value.strip()
    try:return (urlsplit(s if '://' in s else 'https://'+s).hostname or '').lower().removeprefix('www.')
    except ValueError:return ''

def isolate(article):
    """Remove publisher domains and explicit trailing publisher credit; never use publisher geography as evidence.

    Constrained to identifiable source domain and suffix credit; avoids stripping a
    genuine country name from prose solely because publisher name contains it.
    """
    original=article.get('description') or ''
    pub=(article.get('publisher') or '').strip()
    host=hostname(article.get('source_url',''))
    domains={x for x in [host] if x}
    pubhost=hostname(pub) if ('.' in pub and ' ' not in pub) else ''
    if pubhost:domains.add(pubhost)
    clean=original; removed=[]
    for m in reversed(list(DOMAIN.finditer(original))):
        d=m.group(1).lower().removeprefix('www.')
        if d in domains or any(d.endswith('.'+allowed) for allowed in domains):
            clean=clean[:m.start()]+ ' ' +clean[m.end():]
            removed.append({'type':'publisher_domain','value':m.group(0)[:120]})
    if pub and len(pub)>=4:
        # Only identifiable attribution at the end of the RSS summary.
        pat=r'(?:\s*[-–—|•]\s*|\s+)(?:'+re.escape(pub)+r')\s*$'
        mm=re.search(pat,clean,re.I)
        if mm:
            removed.append({'type':'trailing_publisher_credit','value':clean[mm.start():][:120].strip()})
            clean=clean[:mm.start()]
    return re.sub(r'\s+',' ',clean).strip(), removed

def shadow_match(article, matcher):
    clean,removed=isolate(article)
    if not removed:return {'status':'unchanged_no_metadata','removed':[],'clean_description':clean}
    result=matcher(article['title'],clean,article.get('url',''))
    return {'status':'compared','removed':removed,'clean_description':clean,'shadow_place':result.get('name') if result else None}

def summarize(rows):
    # Keep deduplicated URL/location records for accurate review counts.
    unique={}
    for row in rows:
        key=(row.get('url',''),row.get('current_place',''))
        if key not in unique:unique[key]=row
    decisions=Counter(r['classification'] for r in unique.values())
    by_place=defaultdict(lambda:Counter())
    for r in unique.values():by_place[r['current_place']][r['classification']]+=1
    affected=[r for r in unique.values() if r['classification'] in ('lost_after_isolation','changed_after_isolation')]
    affected.sort(key=lambda r:(r['current_place']!='Vietnam',r['current_place'],r.get('title','')))
    return {'mode':'shadow_only_no_live_changes','distinct_url_location_pairs_checked':len(unique),'classification_counts':dict(decisions),
     'affected_places_ranked':[{'place':name,'pairs':sum(c.values()),'lost_after_isolation':c['lost_after_isolation'],'changed_after_isolation':c['changed_after_isolation'],'unaffected':c['same_location_after_isolation']} for name,c in sorted(by_place.items(),key=lambda it:(-(it[1]['lost_after_isolation']+it[1]['changed_after_isolation']),-sum(it[1].values()),it[0]))],
     'affected_review_samples':affected[:100],
     'safety_note':'Shadow results are diagnostic. Missing/changed matches are candidates for manual validation, not proof of incorrect current pins. No live location changes.'}
