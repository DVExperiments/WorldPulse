"""WorldPulse optional worldwide GeoNames city resolver.

GeoNames cities15000 data: https://download.geonames.org/export/dump/
GeoNames data is licensed CC BY 4.0. City matches are *geographic subjects*,
not verified incidents. Failure to fetch never stops news collection.
"""
from __future__ import annotations
import csv
import io
import json
import re
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

URL='https://download.geonames.org/export/dump/cities15000.zip'
CACHE=Path(__file__).resolve().parents[1]/'data/geonames-cities15000.zip'
META={'available':False,'reason':'not initialized','cities_loaded':0,'candidate_names':0,'ambiguous_names':0,'downloaded':False}
STOP={'nice','mobile','reading','orange','victoria','georgia','jordan','paris','london','springfield','newcastle','san jose','san pedro','santa cruz','santiago','kingston','richmond','salem','rochester','manchester','hamilton','columbus','cambridge','portland','birmingham','lebanon','turkey','gaza','china','java','delhi','kiev','odessa','washington'}

class GlobalResolver:
 def __init__(self, legacy):
  self.legacy=legacy
  self.by_name={}
  self.pattern=None
  self.meta=dict(META)

 def load(self):
  try:
   if CACHE.exists() and CACHE.stat().st_size>500_000:
    blob=CACHE.read_bytes()
   else:
    req=urllib.request.Request(URL,headers={'User-Agent':'WorldPulse/1.5.4A (educational geographic news viewer)'})
    with urllib.request.urlopen(req,timeout=11) as response:blob=response.read(12_000_000)
    if len(blob)<500_000:raise ValueError('GeoNames download unexpectedly small')
    self.meta['downloaded']=True
   z=zipfile.ZipFile(io.BytesIO(blob))
   with z.open('cities15000.txt') as file:
    items=defaultdict(list)
    for raw in io.TextIOWrapper(file,encoding='utf8'):
     cols=raw.rstrip('\n').split('\t')
     if len(cols)<15:continue
     try: population=int(cols[14]); lat=float(cols[4]);lng=float(cols[5])
     except ValueError:continue
     name=cols[1]; country=cols[8]
     if not 4<=len(name)<=55 or population<15000:continue
     place={'name':name,'lat':lat,'lng':lng,'level':'place','country_code':country,'population':population,'geonames_id':cols[0],'region_code':cols[10]}
     variants=[name,cols[2]]
     for variant in variants:
      key=variant.casefold().strip()
      if len(key)<5 or key in STOP or not re.fullmatch(r"[\w\s'’.-]+",key,re.UNICODE):continue
      items[key].append(place)
   # Retain only globally unique names; even common unique city names need sufficient length.
   # Collisions within same settlement can appear as name and ASCII alias.
   unique={};ambiguous=0
   for name, rows in items.items():
    dedup={p['geonames_id']:p for p in rows}; options=list(dedup.values())
    if len(options)!=1:ambiguous+=1;continue
    place=options[0]
    if place['population']<50000:continue
    unique[name]=place
   self.by_name=unique
   self.meta.update(available=True,reason='GeoNames cities15000 loaded',cities_loaded=sum(1 for x in items.values()),candidate_names=len(unique),ambiguous_names=ambiguous)
   # Token n-gram matching avoids evaluating tens of thousands of regexes per article.
   return self
  except Exception as exc:
   self.meta['reason']=str(exc)[:180]
   return self

 def match(self,text):
  if not self.by_name:return None
  tokens=re.findall(r"[\w]+(?:['’.-][\w]+)*",text,flags=re.UNICODE)
  choices=[]
  for length in (4,3,2,1):
   for i in range(len(tokens)-length+1):
    segment=tokens[i:i+length]; name=' '.join(segment).casefold()
    p=self.by_name.get(name)
    if p:
     # Names are explicit and unique in cities15000; keep low-ish geographic certainty.
     choices.append((length,p['population'],p))
  if not choices:return None
  choices.sort(key=lambda p:(p[0],p[1]),reverse=True)
  return choices[0][2]

def get_resolver(legacy):
 return GlobalResolver(legacy).load()
