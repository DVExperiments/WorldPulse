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
import os
import socket
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from urllib.parse import urlsplit
from pathlib import Path
from global_geography import get_resolver
from publisher_network import merge_feeds
from geo_mapping_enhancements import find_explicit
from geo_intelligence import CollectorAudit, context_match, classify_unmatched, embed_geo_report

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/news.json'
PLACES = json.loads((ROOT/'data/places.json').read_text(encoding='utf8')) + json.loads((ROOT/'data/places-extra.json').read_text(encoding='utf8'))
# Three regionally distributed searches per theme reduce single-market bias.
REGIONS = [('US','en-US','US:en'),('GB','en-GB','GB:en'),('IN','en-IN','IN:en'),('AU','en-AU','AU:en'),('ZA','en-ZA','ZA:en'),('NG','en-NG','NG:en'),('PH','en-PH','PH:en'),('CA','en-CA','CA:en')]
QUERIES = {
 'politics':['election parliament government','diplomacy summit referendum'],
 'environment':['climate conservation wildlife','pollution deforestation drought'],
 'hazards':['earthquake floods wildfire','storm hurricane landslide'],
 'society':['protest education housing','healthcare rights community'],
 'health':['public health hospitals disease','healthcare medical services'],
 'education':['schools universities students','education teachers learning'],
 'rights':['human rights civil liberties equality','protest discrimination justice'],
 'community':['housing migration communities','local services culture housing'],
 'economy':['inflation trade employment','business investment economy'],
 'science':['science research discovery','technology spacecraft medicine'],
 'conflict':['war military fighting ceasefire','airstrike armed conflict attack'],
}
# Country match is indicative country anchor, not event location. Avoid partial names.
# Alternate spellings are curated only when they have an unambiguous target.
ALIASES = {'Kyiv':'Kiev','Odesa':'Odessa','Zaporizhzhia':'Zaporozhye','Kharkiv':'Kharkov',
 'Türkiye':'Turkey','Côte d’Ivoire':'Ivory Coast','United States':'USA',
 'United Kingdom':'UK','Democratic Republic of the Congo':'DR Congo',
 'Myanmar':'Burma','Czechia':'Czech Republic','South Korea':'Republic of Korea',
 'North Korea':'DPRK','United Arab Emirates':'UAE',
 'São Paulo':'Sao Paulo','Belém':'Belem','Bogotá':'Bogota',
 'Medellín':'Medellin','Mérida Mexico':'Merida Mexico','Cancún':'Cancun',
 'Kraków':'Krakow','Gdańsk':'Gdansk','Wrocław':'Wroclaw',
 'Chișinău':'Chisinau','Chişinău':'Chisinau','Düsseldorf':'Dusseldorf',
 'Malmö':'Malmo','Tromsø':'Tromso','Durrës':'Durres','Whangārei':'Whangarei'}
# Words such as "Nice", "Gaza" and "Jordan" can be ambiguous. A small blocked
# list prevents common false positives unless corroborated by other context.
AMBIGUOUS = {'nice','turkey','georgia','jordan','victoria','reading','mobile','brest','sudan khartoum','tripoli lebanon','odessa texas'}
# v1.5.2: Curated contextual location hints. These are approximate geographic
# SUBJECTS, not verified incident locations. Do not use publisher domicile.
GEO_HINTS = [
 # (display name, latitude, longitude, level, matching phrases, context restriction)
 ('Strait of Hormuz',26.56,56.25,'region',['strait of hormuz'],None),
 ('Iraqi Kurdistan',36.19,44.01,'region',['iraqi kurdistan','kurdistan region of iraq'],None),
 ('Macquarie Island',-54.62,158.86,'place',['macquarie island'],None),
 ('Ho Chi Minh City',10.82,106.63,'place',['hcm city','ho chi minh city','saigon'],None),
 ('Kalispell',48.19,-114.31,'place',['kalispell'],None),
 ('Bacolod',10.68,122.95,'place',['bacolod'],None),
 ('Malaga Province',36.72,-4.42,'region',['malaga province','málaga province'],None),
 ('Jaintia Hills',25.42,92.35,'region',['jaintia hills'],None),
 ('Khyber Pakhtunkhwa',34.0,71.5,'region',['khyber pakhtunkhwa','k-p province','k-p government','k-p assembly'],None),
 ('Somalia',5.15,46.2,'country',['somali opposition','somali president','somali parliament','somali election'],None),
 ('Iraq',33.2,44.4,'country',['iraqi parliament','iraqi cabinet','iraqi government'],None),
 ('United States',39.8,-98.6,'country',['in the us','across the us','us house','in the u.s.'],None),
 ('United Kingdom',54.0,-2.0,'country',['in the uk','across the uk','in the u.k.'],None),
 ('Bangsamoro',7.2,124.2,'region',['barmm','bangsamoro'],None),
 ('Scotland',56.5,-4.2,'region',['westminster parliament','indyref2','snp leader'],None),
 ('Tamil Nadu',11.1,78.7,'region',['dmk mps','mk stalin','dmk demands'],None),
]
# Explicit false-positive safeguards; a mention alone establishes geographic subject,
# not local event site, and some stand-alone words must not resolve to a location.
GEO_MATCHERS=[]
for label,lat,lng,level,terms,_ in GEO_HINTS:
 for term in terms:
  GEO_MATCHERS.append(({'name':label,'lat':lat,'lng':lng,'level':level}, re.compile(r'(?<!\w)'+re.escape(term)+r'(?!\w)',re.I),term))
MATCHERS=[]
for p in PLACES:
 names=[p['name']]
 if p['name'] in ALIASES:names.append(ALIASES[p['name']])
 for name in names:
  if len(name)<4 or name.casefold() in AMBIGUOUS:continue
  MATCHERS.append((p,re.compile(r'(?<!\w)'+re.escape(name)+r'(?!\w)',re.I),name))

# Representative administrative anchors: state/province-level SUBJECTS, not event coordinates.
NA_REGIONS = json.loads((ROOT/'data/north-america-regions.json').read_text(encoding='utf8'))
NA_MATCHERS=[]
for item in NA_REGIONS:
 for phrase in item['terms']:
  NA_MATCHERS.append((item,re.compile(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)',re.I),phrase))

GEO_RESOLVER = None

def bootstrap_global_geography():
 global GEO_RESOLVER
 GEO_RESOLVER=get_resolver(PLACES)
 print('Global geography:',GEO_RESOLVER.meta,flush=True)

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
   'source_url':source.attrib.get('url','') if source is not None else '', 'description':html.unescape(re.sub(r'<[^>]+>',' ',item.findtext('description') or ''))[:650]}

def locate(title, description=''):
 """Use explicit phrases before contextual aliases; never infer from publisher origin.

 The second return value remains headline/description for legacy metrics. The
 actual interpretation is *geographic subject*, NOT a confirmed event site.
 """
 for field, quality in ((title,'headline'),(re.sub(r'https?://\S+',' ',description),'description')):
  contextual=[(p,phrase) for p,rx,phrase in GEO_MATCHERS if rx.search(field)]
  matches=[(p,name) for p,rx,name in MATCHERS if rx.search(field)]
  # Specific explicit or contextual locality outranks a generic country reference.
  regional=[(p,phrase) for p,rx,phrase in NA_MATCHERS if rx.search(field)]
  choices=contextual+matches+regional
  if not choices and GEO_RESOLVER is not None:
   candidate=GEO_RESOLVER.match(field)
   if candidate: choices=[(candidate,candidate['name'])]
  if not choices: continue
  priority={'place':3,'region':2,'country':1}
  choices.sort(key=lambda item:(4 if item[0] in NA_REGIONS and ('state' in item[1].lower() or 'province' in item[1].lower()) else priority.get(item[0].get('level'),0),len(item[1])),reverse=True)
  return choices[0][0],quality
 return None,'unmapped'

# Independent editorial feeds complement Google News; feeds can independently fail.
# Feed metadata is configuration, not a guarantee of availability or geographic representation.
DIRECT_FEEDS = [
 ('BBC World','https://feeds.bbci.co.uk/news/world/rss.xml','international','en'),
 ('BBC Science','https://feeds.bbci.co.uk/news/science_and_environment/rss.xml','international','en'),
 ('BBC Business','https://feeds.bbci.co.uk/news/business/rss.xml','international','en'),
 ('Al Jazeera','https://www.aljazeera.com/xml/rss/all.xml','international','en'),
 ('The Guardian World','https://www.theguardian.com/world/rss','international','en'),
 ('The Guardian Environment','https://www.theguardian.com/environment/rss','international','en'),
 ('DW World','https://rss.dw.com/rdf/rss-en-world','international','en'),
 ('France24','https://www.france24.com/en/rss','international','en'),
 ('NPR World','https://feeds.npr.org/1004/rss.xml','international','en'),
 ('NPR Science','https://feeds.npr.org/1007/rss.xml','international','en'),
 ('ABC Australia','https://www.abc.net.au/news/feed/51120/rss.xml','regional','en'),
 ('RNZ World','https://www.rnz.co.nz/rss/world.xml','regional','en'),
 ('RNZ National','https://www.rnz.co.nz/rss/national.xml','regional','en'),
 ('The Conversation','https://theconversation.com/global/articles.atom','international','en'),
 ('CBC World','https://www.cbc.ca/cmlink/rss-world','regional','en'),
 ('AfricaNews','https://www.africanews.com/feed/','regional','en'),
 ('ReliefWeb Updates','https://reliefweb.int/updates/rss.xml','specialist','en'),
 ('UN News','https://news.un.org/feed/subscribe/en/news/all/rss.xml','specialist','en'),
 ('NASA News','https://www.nasa.gov/feed/','specialist','en'),
 ('France24 FR','https://www.france24.com/fr/rss','regional','fr'),
 ('France24 ES','https://www.france24.com/es/rss','regional','es'),
 ('DW Español','https://rss.dw.com/rdf/rss-es-all','regional','es'),
 ('BBC Brasil','https://www.bbc.com/portuguese/index.xml','regional','pt'),
 # Independent regional publishers (best effort; checked individually and never required).
 ('BBC Africa','https://feeds.bbci.co.uk/news/world/africa/rss.xml','regional','en'),
 ('BBC Asia','https://feeds.bbci.co.uk/news/world/asia/rss.xml','regional','en'),
 ('BBC Latin America','https://feeds.bbci.co.uk/news/world/latin_america/rss.xml','regional','en'),
 ('BBC Middle East','https://feeds.bbci.co.uk/news/world/middle_east/rss.xml','regional','en'),
 ('BBC Europe','https://feeds.bbci.co.uk/news/world/europe/rss.xml','regional','en'),
 ('RNZ Pacific','https://www.rnz.co.nz/rss/pacific.xml','regional','en'),
 ('Guardian Africa','https://www.theguardian.com/world/africa/rss','regional','en'),
 ('Guardian Asia','https://www.theguardian.com/world/asia/rss','regional','en'),
]
DIRECT_FEEDS = merge_feeds(DIRECT_FEEDS)
CATEGORY_TERMS = {
 'conflict':('war','military','troop','missile','airstrike','ceasefire','invasion','conflict','army','bomb','guerra','guerre','ataque'),
 'hazards':('earthquake','flood','wildfire','hurricane','typhoon','volcano','cyclone','storm','disaster','terremoto','inundación'),
 'environment':('climate','conservation','wildlife','emissions','pollution','deforestation','environment','clima','environnement'),
 'politics':('election','parliament','president','minister','government','vote','diplomacy','elección','gobierno','élection'),
 'economy':('inflation','market','trade','jobs','unemployment','bank','economy','economía','économie'),
 'science':('research','study','spacecraft','scientist','technology','discovery','science','ciencia','recherche'),
 'health':('hospital','disease','healthcare','public health','vaccination','medicine','santé','salud','saúde'),
 'education':('school','student','teacher','university','education','école','educación','educação'),
 'rights':('human rights','civil rights','discrimination','equality','protest','derechos humanos','droits humains'),
 'community':('housing','community','migration','local services','culture','homeless','vivienda','moradia'),
 'society':('society','social affairs'),
}

def classify(title):
 t=title.casefold();scores={k:sum(bool(re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',t)) for term in words) for k,words in CATEGORY_TERMS.items()}
 top=max(scores,key=scores.get)
 return top if scores[top] else 'community'

def direct_fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'WorldPulse-NewsMonitor/1.4 (+https://github.com/DVExperiments/WorldPulse)', 'Accept':'application/rss+xml,application/atom+xml,application/xml,text/xml'})
 with urllib.request.urlopen(req,timeout=14) as response: raw=response.read(2_000_000)
 root=ET.fromstring(raw)
 rows=[]
 for item in root.findall('./channel/item'):
  rows.append({'title':norm_title(item.findtext('title') or ''),'url':(item.findtext('link') or '').strip(), 'published':item.findtext('pubDate') or item.findtext('date') or '', 'publisher':'','source_url':'','description':html.unescape(re.sub(r'<[^>]+>',' ',item.findtext('description') or ''))[:650]})
 ns={'a':'http://www.w3.org/2005/Atom'}
 for item in root.findall('a:entry',ns):
  link=next((x.attrib.get('href','') for x in item.findall('a:link',ns) if x.attrib.get('rel','alternate')=='alternate'), '')
  if not link:
   node=item.find('a:link',ns);link=node.attrib.get('href','') if node is not None else ''
  rows.append({'title':norm_title(item.findtext('a:title',default='',namespaces=ns)), 'url':link,'published':item.findtext('a:published',default='',namespaces=ns) or item.findtext('a:updated',default='',namespaces=ns),'publisher':'','source_url':'','description':html.unescape(re.sub(r'<[^>]+>',' ',item.findtext('a:summary',default='',namespaces=ns) or ''))[:650]})
 if not rows:raise ValueError('Feed contained no recognizable RSS/Atom items')
 return rows

def parsed_timestamp(value):
 parsed=timeparse(value)
 if parsed:return parsed.astimezone(dt.timezone.utc)
 try:return dt.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(dt.timezone.utc)
 except (ValueError,AttributeError):return None

def collect(now):
 cutoff=now-dt.timedelta(hours=24)
 results=[];failures={}; scanned=Counter();health=[];seen_queries=0;unmapped=[]; geo_audit=CollectorAudit()
 def ingest(rows,category,source,kind,region,language):
  mapped=0
  for a in rows:
   geo_audit.record(source,'feed_items',mapped=True)
   when=parsed_timestamp(a['published'])
   if not when or not cutoff<=when<=now+dt.timedelta(minutes=20):
    geo_audit.record(source,'out_of_window',a.get('title',''),language,a.get('url',''))
    continue
   if not a['title'] or not a['url'].startswith('https://'):
    geo_audit.record(source,'invalid_article',a.get('title',''),language,a.get('url',''))
    continue
   geo_audit.record(source,'eligible',mapped=True)
   place,match_origin=locate(a['title'],a.get('description',''))
   if not place:
    place,match_origin=find_explicit(a['title'],a.get('description',''),a['url'],PLACES)
   if not place:
    place,match_origin=context_match(a['title'],a.get('description',''),a['url'],PLACES)
   if not place:
    geo_audit.record(source,'unmapped',a['title'],language,a['url'])
    geo_audit.record(source,classify_unmatched(a['title'],a.get('description',''),a['url'],language),mapped=True)
    unmapped.append({'title':a['title'][:180],'description':a.get('description','')[:260], 'publisher':a.get('publisher') or source,'feed':source,'published_at':when.isoformat(),'url':a['url']})
    continue
   mapped+=1
   geo_audit.record(source,'mapped',mapped=True)
   geo_audit.record(source,'method/'+match_origin,mapped=True)
   results.append({**a,'category':category or classify(a['title']),'place':place,'geo_match':match_origin,'at':when.isoformat(), 'publisher':a.get('publisher') or source,'source_kind':kind,'source_name':source,'source_region':region,'language':language})
  return mapped
 for cat in QUERIES:
  for j,locale in enumerate(REGIONS):
   q=QUERIES[cat][j%len(QUERIES[cat])];key=f'google/{cat}/{locale[0]}'
   try:
    rows=list(fetch(q,locale));seen_queries+=1;scanned[cat]+=len(rows)
    mapped=ingest(rows,cat,'Google News '+locale[0],'aggregator',locale[0],'en')
    health.append({'source':key,'status':'ok','items':len(rows),'mapped':mapped,'kind':'aggregator','editorial_region':locale[0],'language':'en'})
   except Exception as exc:
    failures[key]=str(exc);health.append({'source':key,'status':'failed','items':0,'mapped':0,'kind':'aggregator','editorial_region':locale[0],'language':'en'})
   time.sleep(.12)
 for name,url,region,language in DIRECT_FEEDS:
  key='direct/'+name
  try:
   rows=direct_fetch(url);seen_queries+=1;scanned['direct']+=len(rows)
   mapped=ingest(rows,None,name,'publisher',region,language)
   health.append({'source':key,'status':'ok','items':len(rows),'mapped':mapped,'kind':'publisher','editorial_region':region,'language':language})
  except Exception as exc:
   failures[key]=str(exc);health.append({'source':key,'status':'failed','items':0,'mapped':0,'kind':'publisher','editorial_region':region,'language':language})
  time.sleep(.12)
 geo_audit.save(ROOT/'data/geo-intelligence.json',now)
 return results,failures,dict(scanned),seen_queries,health,unmapped

def produce(raw,now):
 # Cross-region / cross-category canonical de-duplication. Similar titles across different
 # publishers remain distinct unless almost identical, preventing inflated reprints.
 exact=set();kept=[];sig_index=defaultdict(list);duplicates=0
 for a in sorted(raw,key=lambda x:x['at'],reverse=True):
  canonical=a['url'].split('?')[0].rstrip('/')
  key=canonical
  if key in exact:duplicates+=1;continue
  exact.add(key)
  sig=signature(a['title'])
  nearby=sig_index[a['place']['name'].lower()]
  if len(sig)>=5 and any(len(sig&s)/len(sig|s)>.82 for s in nearby if s):
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
  points.append({'lat':p['lat'],'lng':p['lng'],'name':p['name'],'accuracy':p.get('level','place'),'location_basis':'description' if all(a.get('geo_match')=='description' for a in articles) else 'headline','location_role':'geographic_subject','event_location_verified':False,
   'count':len(articles),'publisher_count':len({a['publisher'].casefold() for a in articles}),'category':category,'recent_3h':recent,'previous_3h':previous,
   'velocity':velocity,'velocity_change_pct_sample':delta,
   'articles':[{'title':a['title'][:260],'url':a['url'],'published_at':a['at'],'publisher':a['publisher'],
                'source_url':a['source_url'],'source_kind':a.get('source_kind'),'language':a.get('language','en'),'geo_match':a.get('geo_match','headline')} for a in articles[:20]]})
 return sorted(points,key=lambda p:p['count'],reverse=True),duplicates,len(kept)

HISTORY=ROOT/'data/history.json'
HEALTH=ROOT/'data/source-health.json'

def update_history(now,points):
 """Per-day sampled category totals. Does not claim full daily coverage."""
 try:hist=json.loads(HISTORY.read_text(encoding='utf8'))
 except (OSError,ValueError):hist={'schema':1,'days':{}}
 day=now.date().isoformat()
 daydata=hist.setdefault('days',{}).setdefault(day,{'samples':0,'max_mapped_articles':0,'categories':{},'last_updated':''})
 counts=Counter()
 for p in points:counts[p['category']]+=p['count']
 daydata['samples']+=1
 daydata['max_mapped_articles']=max(daydata['max_mapped_articles'],sum(counts.values()))
 daydata['categories']={k:max(v,daydata.get('categories',{}).get(k,0)) for k,v in counts.items()}
 daydata['last_updated']=now.isoformat(timespec='seconds')
 hist['days']={k:v for k,v in sorted(hist['days'].items()) if k>=(now.date()-dt.timedelta(days=30)).isoformat()}
 hist['updated_at']=now.isoformat(timespec='seconds')
 HISTORY.write_text(json.dumps(hist,indent=1),encoding='utf8')


ARTICLE_HISTORY=ROOT/'data/article-history.json'
DIAGNOSTICS=ROOT/'data/data-health.json'

def update_article_history(now,points):
 """Bounded article-level history. Records are sampled mentions, NOT canonical events."""
 try: old=json.loads(ARTICLE_HISTORY.read_text(encoding='utf8'))
 except (OSError,ValueError):old={'schema':1,'articles':{}}
 records=old.get('articles',{})
 if not isinstance(records,dict):records={}
 for p in points:
  for a in p.get('articles',[]):
   url=a.get('url','');
   if not url:continue
   key=hashlib.sha256((url.split('?')[0]).encode()).hexdigest()[:24]
   row=records.get(key,{})
   records[key]={**row,'title':a['title'],'url':url,'publisher':a['publisher'],'category':p['category'],'place':p['name'],'geo_accuracy':p.get('accuracy'),'geo_match':a.get('geo_match'),'published_at':a.get('published_at'),'first_seen':row.get('first_seen',now.isoformat()),'last_seen':now.isoformat()}
 cutoff=(now-dt.timedelta(days=30)).isoformat()
 records={k:v for k,v in records.items() if v.get('last_seen','')>=cutoff}
 # Bounded for repository size; latest first
 records=dict(sorted(records.items(),key=lambda kv:kv[1].get('last_seen',''),reverse=True)[:6000])
 ARTICLE_HISTORY.write_text(json.dumps({'schema':1,'updated_at':now.isoformat(),'retention_days':30,'note':'Sampled tracked article URLs, not verified event clusters','articles':records},ensure_ascii=False,indent=1),encoding='utf8')

def update_diagnostics(now,feeds,unmapped,points,duplicates):
 cat=Counter();geo=Counter();regions=Counter();hemispheres=Counter()
 for p in points:
  cat[p['category']]+=p['count'];geo[p.get('accuracy','unknown')]+=p['count'];regions[p.get('location_basis','unknown')]+=p['count'];hemispheres[('N' if p['lat']>=0 else 'S')+('E' if p['lng']>=0 else 'W')]+=p['count']
 # Distinct unmatched stories are grouped independently of feed repetition.
 unmatched_unique={}
 for row in unmapped:
  title_key=re.sub(r'\W+',' ',row['title'].casefold()).strip()
  if not title_key:continue
  if title_key not in unmatched_unique:unmatched_unique[title_key]={**row,'feed_occurrences':0,'feeds':set()}
  unmatched_unique[title_key]['feed_occurrences']+=1
  unmatched_unique[title_key]['feeds'].add(row['feed'])
 ranked=sorted(unmatched_unique.values(),key=lambda r:(len(r['feeds']),r['feed_occurrences']),reverse=True)
 unmatched_review=[{'title':r['title'],'url':r['url'],'publisher':r['publisher'],'feed_occurrences':r['feed_occurrences'],'feed_count':len(r['feeds']),'description_excerpt':r.get('description','')[:160]} for r in ranked[:120]]
 # Approximate post-dedup publisher contribution by normalized article URL/title.
 # Entries from multiple feeds are assigned to a source only if unique to that
 # source. For cross-source overlap report separately rather than pretending
 # one source alone discovered the article.
 def article_key(a):
  raw_url=a['url'].split('?')[0].rstrip('/').lower()
  if 'news.google.com/rss/articles/' in raw_url:
   return 'google:'+raw_url
  return 'url:'+raw_url
 origin_index=defaultdict(set)
 pub_index=defaultdict(set)
 for a in getattr(update_diagnostics,'raw_for_report',[]):
  k=article_key(a)
  origin_index[k].add('google' if a.get('source_kind')=='aggregator' else 'direct')
  pub_index[k].add(a.get('source_name','unknown'))
 direct_only={k for k,v in origin_index.items() if v=={'direct'}}
 google_only={k for k,v in origin_index.items() if v=={'google'}}
 overlap={k for k,v in origin_index.items() if len(v)>1}
 unique_by_direct_source=Counter()
 for k in direct_only:
  for source in pub_index[k]:unique_by_direct_source[source]+=1
 source_network={'unique_direct_urls_not_in_google_sample':len(direct_only),
  'unique_google_urls_not_in_direct_sample':len(google_only),
  'urls_found_in_both_channels':len(overlap),
  'warning':'URL comparisons underestimate syndication and Google News links often differ from publisher URLs; counts are not verified distinct real-world events',
  'direct_feed_unique_url_contributions':dict(unique_by_direct_source.most_common(30))}
 country_names=Counter()
 unique_places=set()
 for p in points:
  unique_places.add((round(p['lat'],3),round(p['lng'],3),p['name']))
  if p.get('accuracy')=='country':country_names[p['name']]+=p['count']
 # This is a country-labelled article distribution, not a complete continent
 # distribution. Full continent counts need country ISO codes from geocoder.
 coverage_overview={'country_labelled_articles':sum(country_names.values()),
  'country_labels_count':len(country_names),'top_country_subjects':dict(country_names.most_common(30)),
  'distinct_geographic_signal_centers':len(unique_places),
  'warning':'Articles matched to cities/regions are not included in country-labelled counts; lack of mapped articles does not mean no news occurred'}
 region_rollup={}
 for code,_,_ in REGIONS:
  fs=[f for f in feeds if f['source'].startswith('google/') and f['source'].endswith('/'+code)]
  region_rollup[code]={'requests':len(fs),'successful':sum(f['status']=='ok' for f in fs),'mapped_pre_dedupe':sum(f['mapped'] for f in fs)}
 direct_rollup={'configured':sum(f['kind']=='publisher' for f in feeds),'successful':sum(f['kind']=='publisher' and f['status']=='ok' for f in feeds),'mapped_pre_dedupe':sum(f['mapped'] for f in feeds if f['kind']=='publisher')}
 obj={'schema':1,'updated_at':now.isoformat(),'feeds_total':len(feeds),'feeds_ok':sum(f['status']=='ok' for f in feeds),'feeds_failed':[f['source'] for f in feeds if f['status']!='ok'], 'google_feeds_by_region':{code:{'total':sum(f['source'].endswith('/'+code) for f in feeds if f['source'].startswith('google/')),'ok':sum(f['status']=='ok' and f['source'].endswith('/'+code) for f in feeds if f['source'].startswith('google/')),'mapped_pre_dedupe':sum(f['mapped'] for f in feeds if f['source'].startswith('google/') and f['source'].endswith('/'+code))} for code,_,_ in REGIONS}, 'mapped_articles_by_category':dict(cat),'mapped_articles_by_location_precision':dict(geo),'location_evidence_counts':dict(regions),'geographic_quadrants':dict(hemispheres),'geo_signal_count':len(points),'mapped_total':sum(p['count'] for p in points),'geo_match_rate_note':'Do not divide mapped records by total fetched: repeat entries, missing timestamps and expired items distort the rate.','unmapped_sample_count':len(unmapped),'unmapped_distinct_titles':len(set(re.sub(r'\W+',' ',a['title'].casefold()) for a in unmapped)),'unmapped_by_feed':dict(Counter(a['feed'] for a in unmapped).most_common(18)),'unmapped_examples':unmatched_review[:35], 'unmapped_review_file':'data/unmatched-review.json', 'direct_source_breakdown':direct_rollup, 'publisher_network_contributions':source_network, 'coverage_overview':coverage_overview, 'source_editions':region_rollup, 'duplicates_removed':duplicates,'gazetteer_entries':len(PLACES)+len(GEO_HINTS)+len(NA_REGIONS),'contextual_alias_groups':len(GEO_HINTS),'global_gazetteer':GEO_RESOLVER.meta if GEO_RESOLVER else {'available':False,'reason':'not initialized'},'warning':'Unmapped count includes repeated feed entries. RSS geo-matching reflects place mentions, not necessarily where events occurred.'}
 DIAGNOSTICS.write_text(json.dumps(obj,ensure_ascii=False,indent=1),encoding='utf8')
 (ROOT/'data/unmatched-review.json').write_text(json.dumps({'schema':1,'updated_at':now.isoformat(),'distinct_unmatched':len(unmatched_unique),'note':'Headlines lack a confidently matched place. Not every headline is geographically attributable. Samples may repeat over time.','examples':unmatched_review},ensure_ascii=False,indent=1),encoding='utf8')

def main():
 bootstrap_global_geography()
 now=dt.datetime.now(dt.timezone.utc)
 old={}
 if OUT.exists():
  try:old=json.loads(OUT.read_text(encoding='utf8'))
  except (OSError,ValueError):pass
 raw,failures,scanned,success,health,unmapped=collect(now)
 HEALTH.write_text(json.dumps({'updated_at':now.isoformat(timespec='seconds'),'ok':success,'attempts':len(health),'sources':health,'failures':failures},indent=1),encoding='utf8')
 if not success:
  old['status']='stale';old['last_attempt_at']=now.isoformat();old['errors']=failures
  OUT.write_text(json.dumps(old,ensure_ascii=False,indent=1),encoding='utf8')
  raise SystemExit('Every RSS feed failed; retained last-known snapshot')
 points,duplicates,unique=produce(raw,now)
 publishers=set(a['publisher'].casefold() for a in raw if a.get('publisher'))
 record={'schema':2,'version':'1.5.4B','source':'Google News RSS and independent publisher RSS samples','updated_at':now.isoformat(timespec='seconds'),
  'last_attempt_at':now.isoformat(timespec='seconds'),'window':'rolling 24 hours',
  'status':'live' if not failures else 'partial','query_successes':success,'query_attempts':len(health),
  'articles_scanned':scanned,'distinct_mapped_articles':unique,'duplicates_removed':duplicates,
  'source_count':len(publishers),'direct_sources_ok':sum(h['status']=='ok' for h in health if h['kind']=='publisher'),
  'unmapped_articles_sample':len(unmapped),'geographic_confidence':{'headline':sum(a.get('geo_match')=='headline' for a in raw),'description':sum(a.get('geo_match')=='description' for a in raw)},
  'source_health_file':'data/source-health.json','history_file':'data/history.json',
  'metric':'Deduplicated mapped articles in sampled RSS feeds, not all news worldwide',
  'accuracy_note':'Locations are geographic SUBJECTS, never automatically verified incident sites. Locations are place mentions from headlines or descriptions, not verified event coordinates. Description matches are contextual; country pins use representative anchors.',
  'velocity_note':'Recent 3-hour vs previous 3-hour counts within sampled articles; directional, not a verified activity surge.',
  'errors':failures,'points':points}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(record,ensure_ascii=False,indent=1),encoding='utf8')
 update_history(now,points)
 update_article_history(now,points)
 update_diagnostics.raw_for_report=raw
 update_diagnostics(now,health,unmapped,points,duplicates)
 embed_geo_report(ROOT/'data')
 print(f'WorldPulse v1.5.4B: {success}/{len(health)} feeds; {unique} mapped articles; {duplicates} duplicates removed; {len(points)} signals; {len(publishers)} publisher names; status={record["status"]}',flush=True)
 if not points:print('WARNING: feeds succeeded but no headline-place matches',flush=True)
if __name__=='__main__':main()
