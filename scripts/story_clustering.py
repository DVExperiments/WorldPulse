"""WorldPulse F.1 conservative clustering of published article previews.

These are similarity groups, not verified events, story identity or fact checks.
"""
import hashlib
import re
from collections import defaultdict
from datetime import datetime, timezone

STOP={'the','a','an','and','or','on','in','at','to','of','for','with','after','from','as','by','is','are','was','were','will','new','latest','news','says','said','over','about','into','amid','what','how','why','this','that','its','it','more','than','during','today','live','update','updates'}

def tokens(text):
    words=re.findall(r'[^\W_]+',str(text or '').casefold(),flags=re.UNICODE)
    return {w for w in words if len(w)>=3 and w not in STOP and not w.isdigit()}

def similarity(a,b):
    x,y=tokens(a),tokens(b)
    if len(x)<3 or len(y)<3: return 0.0
    common=len(x&y)
    if common<3:return 0.0
    return common/len(x|y)

def parse_time(value):
    try:return datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()
    except (ValueError,TypeError,AttributeError):return None

def build_clusters(points,window_hours=36):
    """Compare previewed articles only; never use publisher to infer geography."""
    buckets=defaultdict(list)
    seen_urls=set()
    for point in points:
        place=str(point.get('name','')).casefold().strip()
        category=str(point.get('category','')).strip()
        if not place or not category:continue
        for a in point.get('articles',[]):
            url=a.get('url','')
            if not isinstance(url,str) or not url.startswith(('https://','http://')) or url in seen_urls:continue
            seen_urls.add(url)
            if len(tokens(a.get('title','')))<3:continue
            buckets[(place,category)].append(a)
    result=[]
    for (place,category),articles in sorted(buckets.items()):
        groups=[]
        for a in sorted(articles,key=lambda v:(v.get('published_at',''),v.get('url','')),reverse=True):
            t=parse_time(a.get('published_at'))
            if t is None:continue
            match=None
            for g in groups:
                # Compare against EVERY existing item, preventing transitive topic drift.
                if all(abs(t-parse_time(other['published_at']))<=window_hours*3600 and similarity(a['title'],other['title'])>=0.68 for other in g):
                    match=g;break
            if match is None:groups.append([a])
            else:match.append(a)
        for g in groups:
            publishers={str(a.get('publisher') or '').casefold().strip() for a in g if str(a.get('publisher') or '').strip()}
            if len(g)<2 or len(publishers)<2:continue
            g.sort(key=lambda a:a.get('published_at',''),reverse=True)
            urls=sorted(a['url'] for a in g)
            cluster_id='f1-'+hashlib.sha256(('\n'.join(urls)).encode()).hexdigest()[:14]
            result.append({'id':cluster_id,'label':g[0]['title'][:260],
                'location':place,'category':category,'article_count':len(g),'publisher_count':len(publishers),
                'latest_at':g[0]['published_at'],
                'articles':[{'title':a.get('title',''),'url':a['url'],'publisher':a.get('publisher',''), 'published_at':a.get('published_at','')} for a in g[:20]]})
    result.sort(key=lambda g:(-g['publisher_count'],-g['article_count'],g['latest_at'],g['id']),reverse=False)
    return result[:100]
