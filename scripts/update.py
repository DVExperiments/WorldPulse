#!/usr/bin/env python3
"""Fetch geographic news mentions from GDELT GEO 2.0; never manufacture data."""
import datetime as dt
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'news.json'
CATEGORIES = {
 'politics': '(election OR parliament OR government OR diplomacy)',
 'environment': '(climate OR wildlife OR pollution OR conservation)',
 'hazards': '(earthquake OR flood OR wildfire OR hurricane)',
 'society': '(protest OR education OR healthcare OR housing)',
 'economy': '(inflation OR trade OR economy OR employment)',
 'science': '(research OR technology OR discovery OR science)',
}
class Links(HTMLParser):
 def __init__(self):
  super().__init__(); self.items=[]; self.href=None; self.words=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a': self.href=dict(attrs).get('href'); self.words=[]
 def handle_data(self,data):
  if self.href: self.words.append(data)
 def handle_endtag(self,tag):
  if tag=='a' and self.href:
   title=html.unescape(' '.join(' '.join(self.words).split())).strip()
   url=html.unescape(self.href)
   if title and url.startswith(('http://','https://')):
    self.items.append({'title':title[:240], 'url':url})
   self.href=None;self.words=[]
def read_urls(raw):
 p=Links();p.feed(raw or ''); out=[];seen=set()
 for v in p.items:
  if v['url'] not in seen:
   seen.add(v['url']);out.append(v)
 return out[:5]
def fetch_category(category, query):
 params=urlencode({'query':query,'mode':'pointdata','format':'geojson', 'timespan':'1d', 'maxpoints':'350','sort':'date'})
 req=Request('https://api.gdeltproject.org/api/v2/geo/geo?'+params, headers={'User-Agent':'WorldPulse/1.0 (public research visualization)'})
 with urlopen(req, timeout=40) as r:
  payload=json.load(r)
 if payload.get('type') != 'FeatureCollection':
  raise ValueError('Expected GEO GeoJSON FeatureCollection')
 result=[]
 for f in payload.get('features',[]):
  props=f.get('properties') or {}; coords=(f.get('geometry') or {}).get('coordinates') or []
  if len(coords)<2:continue
  lng,lat=coords[:2]
  if not (-180<=lng<=180 and -90<=lat<=90):continue
  count=props.get('count',0)
  try:count=max(0,int(count))
  except (TypeError,ValueError):count=0
  links=read_urls(props.get('html',''))
  result.append({'lat':lat,'lng':lng,'name':str(props.get('name') or 'Unlabelled location')[:150],
                 'count':count,'category':category,'articles':links})
 return result

def main():
 now=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
 points=[];errors={}; successes=[]
 for cat,query in CATEGORIES.items():
  try:
   got=fetch_category(cat,query);points.extend(got);successes.append(cat)
   print(f'{cat}: {len(got)} locations')
  except Exception as exc:
   errors[cat]=str(exc);print(f'{cat}: FAILED: {exc}')
  time.sleep(2)
 # Merge with last known fresh data per category if partial failure; preserve acquisition timestamps.
 prev={}
 if OUT.exists():
  try:
   saved=json.loads(OUT.read_text(encoding='utf-8'))
   prev=saved if isinstance(saved,dict) else {}
  except (ValueError,OSError):pass
 old=prev.get('points',[])
 if successes:
  pts=points+[p for p in old if p.get('category') in errors]
  updated=now
 else:
  pts=old;updated=prev.get('updated_at')
 status='live' if len(successes)==len(CATEGORIES) else ('partial' if successes else 'stale')
 record={'schema':1,'updated_at':updated,'last_attempt_at':now,'status':status,
         'source':'GDELT GEO 2.0','window':'rolling 24 hours',
         'metric':'GDELT location mentions near category keywords (not unique new articles)',
         'categories_updated':successes,'errors':errors,'points':pts}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(record,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print(f'Wrote {len(pts)} points to {OUT}, status={status}')
 if not successes:raise SystemExit('All feeds failed; retained last-known data')
if __name__=='__main__':main()
