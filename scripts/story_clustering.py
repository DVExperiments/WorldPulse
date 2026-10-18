"""WorldPulse F.1.1 conservative news similarity groups; NOT verified events.

Uses only published articles. No remote calls, embeddings or publisher-to-place inference.
"""
import hashlib
import re
import unicodedata
from collections import defaultdict, Counter
from datetime import datetime

STOP={'the','a','an','and','or','on','in','at','to','of','for','with','after','from','as','by','is','are','was','were','will','new','latest','news','says','said','over','about','into','amid','what','how','why','this','that','its','it','more','than','during','today','live','update','updates'}
# Very limited inflection normalisation; avoid broad semantic synonym substitutions.
REPLACE={'protests':'protest','protesters':'protester','demonstrations':'demonstration','clashes':'clash','riots':'riot','teachers':'teacher','schools':'school','officials':'official','arrests':'arrest','arrested':'arrest','fires':'fire','buildings':'building','students':'student','votes':'vote','laws':'law','housing':'housing'}
EVENT={'protest','demonstration','riot','clash','strike','election','vote','earthquake','flood','fire','arrest','airstrike','attack','meeting','committee','bill','law','storm','shooting','explosion','treaty'}

def clean_headline(title,publisher=''):
    text=unicodedata.normalize('NFKC',str(title or '')).strip()
    text=re.sub(r'^\s*(?:breaking|latest|live|watch)\s*[:|\-]\s*','',text,flags=re.I)
    # Remove only a suffix matching the known publisher, never arbitrary text after a dash.
    p=str(publisher or '').strip()
    if p and len(p)>2:
        text=re.sub(r'\s+[-|–—]\s*'+re.escape(p)+r'\s*$', '',text,flags=re.I)
    return text.strip()

def tokens(text):
    words=re.findall(r'[^\W_]+',unicodedata.normalize('NFKC',str(text or '')).casefold(),flags=re.UNICODE)
    return {REPLACE.get(w,w) for w in words if len(w)>=3 and w not in STOP and not w.isdigit()}

def similarity(a,b):
    x,y=tokens(a),tokens(b)
    if len(x)<3 or len(y)<3:return 0.0
    common=len(x&y)
    if common<3:return 0.0
    return common/len(x|y)

def matching_reason(a,b):
    x,y=tokens(a),tokens(b)
    overlap=x&y
    if len(x)<3 or len(y)<3 or len(overlap)<3:return None
    j=len(overlap)/len(x|y)
    if j>=.68:return 'strong_headline_overlap'
    # Guarded additional recall: four shared terms, a shared specific event keyword,
    # at least 60% coverage of shorter title, and relatively high Jaccard.
    if len(overlap)>=4 and overlap&EVENT and j>=.48 and len(overlap)/min(len(x),len(y))>=.60:
        return 'shared_event_terms'
    return None

def parse_time(value):
    try:return datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()
    except (ValueError,TypeError,AttributeError):return None

def cluster_bundle(points,window_hours=36):
    buckets=defaultdict(list)
    seen_urls=set()
    counters=Counter()
    for point in points:
        place=str(point.get('name','')).casefold().strip()
        category=str(point.get('category','')).strip()
        if not place or not category:continue
        for article in point.get('articles',[]):
            url=article.get('url','')
            if not isinstance(url,str) or not url.startswith(('https://','http://')) or url in seen_urls:continue
            seen_urls.add(url)
            a=dict(article)
            a['_clean']=clean_headline(a.get('title',''),a.get('publisher',''))
            a['_time']=parse_time(a.get('published_at'))
            if len(tokens(a['_clean']))<3 or a['_time'] is None:continue
            buckets[(place,category)].append(a)
            counters['candidate_articles']+=1
    result=[]
    for (place,category),articles in sorted(buckets.items()):
        # Preserve latest report per publisher + normalised headline. Other
        # publisher reports of the same headline remain independently visible.
        unique={}
        for a in articles:
            pub=str(a.get('publisher') or '').casefold().strip()
            key=(pub,re.sub(r'\s+',' ',a['_clean'].casefold()))
            prev=unique.get(key)
            if prev is None or (a['_time'],a.get('url',''))>(prev['_time'],prev.get('url','')):
                unique[key]=a
        counters['same_publisher_headlines_collapsed']+=len(articles)-len(unique)
        groups=[]
        for a in sorted(unique.values(),key=lambda v:(v['_time'],v.get('url','')),reverse=True):
            chosen=None
            for g in groups:
                if all(abs(a['_time']-o['_time'])<=window_hours*3600 and matching_reason(a['_clean'],o['_clean']) for o in g):
                    chosen=g;break
            if chosen is None:groups.append([a])
            else:chosen.append(a)
        for g in groups:
            pubs={str(a.get('publisher') or '').casefold().strip() for a in g if str(a.get('publisher') or '').strip()}
            if len(g)<2 or len(pubs)<2:continue
            g.sort(key=lambda a:(a['_time'],a.get('url','')),reverse=True)
            urls=sorted(a['url'] for a in g)
            reasons=Counter(matching_reason(a['_clean'],b['_clean']) for i,a in enumerate(g) for b in g[i+1:])
            reasons.pop(None,None)
            match_rule='shared_event_terms' if reasons.get('shared_event_terms') else 'strong_headline_overlap'
            result.append({'id':'f1-'+hashlib.sha256(('\n'.join(urls)).encode()).hexdigest()[:14],
              'label':g[0]['_clean'][:260], 'location':place,'category':category,
              'article_count':len(g),'publisher_count':len(pubs),'matching_rule':match_rule,
              'latest_at':g[0]['published_at'],
              'articles':[{'title':a.get('title',''),'url':a['url'],'publisher':a.get('publisher',''), 'published_at':a.get('published_at','')} for a in g[:20]]})
    result.sort(key=lambda g:(-g['publisher_count'],-g['article_count'],g['latest_at'],g['id']))
    counters['clusters_produced']=len(result)
    counters['grouped_articles']=sum(g['article_count'] for g in result)
    counters['groups_using_guarded_expansion']=sum(g['matching_rule']=='shared_event_terms' for g in result)
    counters['articles_after_publisher_dedupe']=counters['candidate_articles']-counters['same_publisher_headlines_collapsed']
    return {'story_clusters':result[:100], 'cluster_diagnostics':{'version':'2.0F.1.1','scope':'published_article_previews','note':'Similarity groups are not verified events. Counts refer to sampled published previews.','counts':dict(counters)}}

def build_clusters(points,window_hours=36):return cluster_bundle(points,window_hours)['story_clusters']
