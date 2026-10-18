"""WorldPulse D.4: explain mapping misses and recover conservative explicit place references.
No network access, dependencies, geocoder APIs, or publisher-location guessing.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit,unquote

AMBIGUOUS={'georgia','jordan','turkey','nice','reading','mobile','orange','victoria','china','may','march','us','uk','usa','india','new','home','world','news','press','general','central','national','international','rio','java','congo','chad','guinea','oman','mali','niger'}
EXCLUDE_TOKENS={'the','de','la','le','les','el','los','las','del','of','in','en','da','do','dos','das','di','du','and','et'}

def fold(value):
    return ''.join(c for c in unicodedata.normalize('NFKD',str(value or '').casefold()) if not unicodedata.combining(c))

def candidates(places):
    by_name=defaultdict(list)
    for place in places:
        name=fold(place.get('name','')).strip()
        if len(name)<4 or name in AMBIGUOUS or not re.search('[a-z]',name):continue
        by_name[name].append(place)
    # Identical names with different coordinates are never guessed.
    return [(name,p[0]) for name,p in sorted(by_name.items(),key=lambda n:-len(n[0])) if len(p)==1]

def context_match(title,description,url,places):
    """Match only explicit geographic context, not ordinary ambiguous terms.

    This supplements (not replaces) the original matcher. It never looks at
    publisher or edition metadata and avoids hallucinating event coordinates.
    """
    names=candidates(places)
    # Before matching, prefer title; descriptions may contain unrelated links.
    for label,field in [('headline-multilingual',title),('description-multilingual',description)]:
        text=fold(re.sub(r'https?://\S+',' ',field or ''))
        for name,place in names:
            if re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',text):
                return place,label
    # Geographic path segments only: /countries/..., /cities/...
    try: bits=[fold(unquote(x).replace('-',' ').replace('_',' ')) for x in urlsplit(url).path.split('/')]
    except (TypeError,ValueError):return None,'unmapped'
    for a,b in zip(bits,bits[1:]):
        if a in ('country','countries','city','cities','location','locations','place','places'):
            for name,place in names:
                if b==name:return place,'url-explicit-place'
    return None,'unmapped'

def classify_unmatched(title,description,url,language='en'):
    t=(title or '').strip();d=(description or '').strip()
    if not t:return 'empty_title'
    if len(t)<18:return 'short_headline_no_location'
    if not d:return 'missing_description'
    if len(d)<40:return 'brief_description_no_location'
    return 'no_confident_geographic_reference'

class CollectorAudit:
    def __init__(self):
        self.records=defaultdict(Counter)
        self.examples=defaultdict(list)
        self.method=Counter()
    def record(self,feed,reason,title='',language='',url='',mapped=False):
        self.records[feed][reason]+=1
        if mapped:self.method[reason]+=1
        if not mapped and len(self.examples[feed])<4:
            self.examples[feed].append({'title':str(title)[:170], 'reason':reason,'language':str(language)[:12], 'url':str(url)[:350]})
    def save(self,path,now):
        rows=[]
        for feed,counts in sorted(self.records.items()):
            rows.append({'source':feed,'funnel':dict(counts),'samples':self.examples.get(feed,[])})
        obj={'schema':1,'generated_at':now.isoformat(),'sources':rows,'mapping_methods':dict(self.method),
             'definitions':{'feed_items':'All items returned by a feed, potentially including old stories',
                            'out_of_window':'Article outside current rolling-24-hour window or has invalid timestamp',
                            'invalid_article':'Missing title or HTTPS article URL',
                            'unmapped':'Eligible article with no defensible geographic subject',
                            'mapped':'Eligible article mapped to a geographic subject, not necessarily incident location'},
             'privacy_note':'Contains public feed headline excerpts and source URLs only.',
             'warning':'Do not interpret a publisher country or feed edition as an article location.'}
        target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
        return obj

def embed_geo_report(data_dir):
    """Embed bounded diagnostic summaries into an existing committed report file.

    GitHub Actions already commits unmatched-review.json, so no workflow edit.
    """
    directory=Path(data_dir)
    details=directory/'geo-intelligence.json'
    target=directory/'unmatched-review.json'
    if not details.exists() or not target.exists():return False
    audit=json.loads(details.read_text(encoding='utf-8'))
    report=json.loads(target.read_text(encoding='utf-8'))
    report['geo_intelligence']={
        'schema':1,'generated_at':audit['generated_at'],
        'mapping_methods':audit['mapping_methods'],
        'source_funnels':[{'source':r['source'],'funnel':r['funnel'],'examples':r['samples'][:2]} for r in audit['sources']],
        'note':'Counts are per feed, before deduplication. Mapped pins are geographic subjects, not verified incident locations.'}
    target.write_text(json.dumps(report,ensure_ascii=False,indent=1),encoding='utf-8')
    print('Geographic intelligence: embedded diagnostics in data/unmatched-review.json',flush=True)
    return True
