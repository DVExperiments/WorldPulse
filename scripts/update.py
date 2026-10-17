#!/usr/bin/env python3
"""WorldPulse v1.3: multi-region Google News RSS sampling and conservative geocoding.
No paid APIs, no publisher-location inference. Counts are deduplicated RSS samples.
"""
from __future__ import annotations
import datetime as dt
import email.utils
import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/news.json'
PLACES = json.loads((ROOT/'data/places.json').read_text(encoding='utf8'))
# Three regionally distributed searches per theme reduce single-market bias.
REGIONS = [('US','en-US','US:en'),('GB','en-GB','GB:en'),('IN','en-IN','IN:en'),('AU','en-AU','AU:en')]
QUERIES = {
 'politics':['election parliament government','diplomacy summit referendum'],
 'environment':['climate conservation wildlife','pollution deforestation drought'],
 'hazards':['earthquake floods wildfire','storm hurricane landslide'],
 'society':['protest education housing','healthcare rights community'],
 'economy':['inflation trade employment','business investment economy'],
 'science':['science research discovery','technology spacecraft medicine'],
 'conflict':['war military fighting ceasefire','airstrike armed conflict attack'],
}
# Country match is indicative country anchor, not event location. Avoid partial names.
MATCHERS = [(p,re.compile(r'(?<!\w)'+re.escape(p['name'])+r'(?!\w)',re.I)) for p in PLACES if len(p['name'])>=4]
PUBLISHERS = {'reuters.com','apnews.com','bbc.com','bbc.co.uk','aljazeera.com','theguardian.com','dw.com','france24.com'}

def norm_title(title):
 title = html.unescape(title)
 title = re.sub(r'\s+[—–-]\s+[^—–-]{2,65}$','',title) # Google News publisher suffix
 return re.sub(r'\s+',' ',title).strip()

def signature(title):
 clean=norm_title(title).lower()
 clean=re.sub(r'[^\w\s]',' ',clean)
 clean=re.sub(r'\b(the|a|an|and|of|to|in|on|for|with|from|at|after|as|by)\b',' ',clean)
 return frozenset(w for w in clean.split() if len(w)>2)

def timeparse(s):
 try:
  v=email.utils.parsedate_to_datetime(s)
  return v if v.tzinfo else v.replace(tzinfo=dt.timezone.utc)
 except (TypeError,ValueError,IndexError):return None

def fetch(query,locale):
 gl,hl,ceid=locale
 url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':f'({query}) when:1d','hl':hl,'gl':gl,'ceid':ceid,'num':'100'})
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (WorldPulse/1.3 global-news-map)','Accept':'application/rss+xml,application/xml,text/xml'})
 with urllib.request.urlopen(req,timeout=30) as response:
  raw=response.read(2_500_000)
 root=ET.fromstring(raw)
 if root.tag!='rss':raise ValueError('Feed returned non-RSS data')
 for item in root.findall('./channel/item'):
  source=item.find('source')
  yield {'title':norm_title(item.findtext('title') or ''),'url':(item.findtext('link') or '').strip(),
   'published':item.findtext('pubDate') or '', 'publisher': source.text if source is not None else '',
   'source_url':source.attrib.get('url','') if source is not None else ''}

def locate(title):
 matches=[p for p,rx in MATCHERS if rx.search(title)]
 if not matches:return None
 # Prefer matched named cities/areas to countries; preserve representative accuracy level.
 matches.sort(key=lambda p:(p.get('level')!='country',len(p['name'])),reverse=True)
 return matches[0]

def collect(now):
 cutoff=now-dt.timedelta(hours=24)
 results=[]; failures={}; scanned=Counter(); seen_queries=0
 for cat,queries in QUERIES.items():
  for j,locale in enumerate(REGIONS):
   # Rotate query variants across locales; more variety with limited requests.
   q=queries[j%len(queries)]; key=f'{cat}/{locale[0]}'
   try:
    rows=list(fetch(q,locale));seen_queries+=1;scanned[cat]+=len(rows)
    for a in rows:
     when=timeparse(a['published'])
     if not when or not cutoff<=when<=now+dt.timedelta(minutes=20):continue
     if not a['title'] or not a['url'].startswith('https://'):continue
     place=locate(a['title'])
     if not place:continue
     results.append({**a,'category':cat,'place':place,'at':when.astimezone(dt.timezone.utc).isoformat()})
    print(f'{key}: received {len(rows)} RSS items',flush=True)
   except Exception as exc:
    failures[key]=str(exc);print(f'{key}: FAILED {exc}',flush=True)
   time.sleep(.35)
 return results,failures,dict(scanned),seen_queries

def produce(raw,now):
 # Cross-region / cross-category canonical de-duplication. Similar titles across different
 # publishers remain distinct unless almost identical, preventing inflated reprints.
 exact=set();kept=[];sig_index=defaultdict(list);duplicates=0
 for a in sorted(raw,key=lambda x:x['at'],reverse=True):
  canonical=a['url'].split('?')[0].rstrip('/')
  key=(canonical, a['category'])
  if key in exact:duplicates+=1;continue
  exact.add(key)
  sig=signature(a['title'])
  nearby=sig_index[(a['category'],a['place']['name'].lower())]
  if len(sig)>=5 and any(len(sig&s)/len(sig|s)>.89 for s in nearby if s):
   duplicates+=1;continue
  nearby.append(sig)
  kept.append(a)
 grouped=defaultdict(list)
 for a in kept:grouped[(a['place']['name'].lower(),a['category'])].append(a)
 points=[]
 for (_,category),articles in grouped.items():
  p=articles[0]['place']; recent=sum(1 for a in articles if (now-dt.datetime.fromisoformat(a['at'])).total_seconds()<3*3600)
  previous=sum(1 for a in articles if 3*3600<=(now-dt.datetime.fromisoformat(a['at'])).total_seconds()<6*3600)
  # +1 smoothing prevents undefined ratios; present as directional sampled comparison.
  delta=round((recent-previous)/(previous+1)*100)
  velocity='rising' if recent>=3 and recent>=previous+2 else ('cooling' if previous>=3 and previous>=recent+2 else 'steady')
  points.append({'lat':p['lat'],'lng':p['lng'],'name':p['name'],'accuracy':p.get('level','place'),
   'count':len(articles),'category':category,'recent_3h':recent,'previous_3h':previous,
   'velocity':velocity,'velocity_change_pct_sample':delta,
   'articles':[{'title':a['title'][:260],'url':a['url'],'published_at':a['at'],'publisher':a['publisher'],
                'source_url':a['source_url']} for a in articles[:20]]})
 return sorted(points,key=lambda p:p['count'],reverse=True),duplicates,len(kept)

def main():
 now=dt.datetime.now(dt.timezone.utc)
 old={}
 if OUT.exists():
  try:old=json.loads(OUT.read_text(encoding='utf8'))
  except (OSError,ValueError):pass
 raw,failures,scanned,success=collect(now)
 if not success:
  old['status']='stale';old['last_attempt_at']=now.isoformat();old['errors']=failures
  OUT.write_text(json.dumps(old,ensure_ascii=False,indent=1),encoding='utf8')
  raise SystemExit('Every regional RSS search failed; retained last-known snapshot')
 points,duplicates,unique=produce(raw,now)
 record={'schema':2,'version':'1.3','source':'Google News RSS regional samples','updated_at':now.isoformat(timespec='seconds'),
  'last_attempt_at':now.isoformat(timespec='seconds'),'window':'rolling 24 hours',
  'status':'live' if not failures else 'partial','query_successes':success,'query_attempts':len(REGIONS)*len(QUERIES),
  'articles_scanned':scanned,'distinct_mapped_articles':unique,'duplicates_removed':duplicates,
  'metric':'Deduplicated mapped articles in sampled RSS queries, not all news worldwide',
  'accuracy_note':'Places are inferred from explicit headline names. Country markers are representative anchors, not exact incident locations.',
  'velocity_note':'Recent 3-hour vs previous 3-hour counts within sampled articles; directional, not a verified activity surge.',
  'errors':failures,'points':points}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(record,ensure_ascii=False,indent=1),encoding='utf8')
 print(f'WorldPulse v1.3: {success}/{record["query_attempts"]} regional queries; {unique} distinct mapped articles; {duplicates} duplicates removed; {len(points)} location-category signals; status={record["status"]}',flush=True)
 if not points:print('WARNING: feeds succeeded but no headline-place matches; inspect gazetteer/query coverage',flush=True)
if __name__=='__main__':main()
