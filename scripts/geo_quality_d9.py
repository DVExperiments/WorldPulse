"""D.9 audit-only QA for WorldPulse. Never generates geographic assignments."""
from __future__ import annotations
from collections import Counter, defaultdict
import json, re
from urllib.parse import urlsplit, urlunsplit
from geo_subject_d8 import countries_in, contains, explicit_locality

QUALITY_LEVELS = ('explicit_headline_place','explicit_description_place','contextual_or_alias','unsupported_or_unverified')

def normalize_url(url):
 try:
  u=urlsplit(url or '')
  return urlunsplit((u.scheme.lower(),u.netloc.lower(),u.path.rstrip('/'),'','')) if u.scheme and u.netloc else (url or '')
 except ValueError:return url or ''

def quality_level(article):
 name=(article.get('place') or {}).get('name','')
 title=article.get('title','') or ''
 desc=article.get('description','') or ''
 if name and contains(title,name):return QUALITY_LEVELS[0]
 if name and contains(desc,name):return QUALITY_LEVELS[1]
 if article.get('geo_match'):return QUALITY_LEVELS[2]
 return QUALITY_LEVELS[3]

def story_classification(article):
 title=article.get('title','') or ''
 name=(article.get('place') or {}).get('name','')
 countries=countries_in(title)
 for code,aliases in {'italy':('italy','italia','italie'),'belgium':('belgium','belgique','belgica','bélgica'),'portugal':('portugal',)}.items():
  if any(contains(title,alias) for alias in aliases) and code not in countries:countries.append(code)
 countries.sort()
 if len(countries)>1:
  kind='cross_border_explicit_locality' if name and explicit_locality(title,name) else 'multi_country_unresolved'
 elif len(countries)==1:
  kind='single_country_reference'
 else:kind='no_curated_country_reference'
 return {'classification':kind,'headline_countries':countries,'existing_selected_place':name,
         'location_verified':False,'automatic_additional_pins':0}

def report(articles, points, benchmark_results=None, max_samples=40):
 # Deduplicate per canonical URL and selected location. Do not equate repeat RSS rows with unique news.
 unique={}
 for a in articles:
  key=(normalize_url(a.get('url')), (a.get('place') or {}).get('name','').casefold())
  unique.setdefault(key,a)
 rows=list(unique.values())
 levels=Counter(quality_level(a) for a in rows)
 classes=Counter(story_classification(a)['classification'] for a in rows)
 place_counts=Counter((a.get('place') or {}).get('name','') for a in rows)
 duplicates=len(articles)-len(rows)
 samples=[]
 for a in rows:
  c=story_classification(a)
  if c['classification'] in ('multi_country_unresolved','cross_border_explicit_locality') and len(samples)<max_samples:
   samples.append({'title':a.get('title','')[:190], 'url':a.get('url',''),**c,'quality_level':quality_level(a)})
 # Concentration is a monitoring trigger, not a declaration that locations are wrong.
 top=[{'place':name,'unique_articles':num,'share_of_unique_articles_pct':round(100*num/len(rows),1) if rows else 0,
       'review_recommended':num>=30 and num/max(len(rows),1)>=0.08} for name,num in place_counts.most_common(20) if name]
 return {'schema':1,'policy':'Audit only. No added pins, inferred locations, automatic remapping or newly blocked articles.',
   'unique_mapped_url_location_pairs':len(rows),'pre_deduplication_mapped_entries':len(articles),
   'duplicate_url_location_observations_removed':duplicates,'evidence_levels':dict(levels),
   'multilocation_classifications':dict(classes),'international_review_samples':samples,
   'top_location_concentrations':top,
   'vietnam_unique_article_count':place_counts.get('Vietnam',0),
   'benchmark':benchmark_results or {},
   'limitations':['Place mention does not prove incident coordinates or event location.',
    'Curated countries dictionary does not detect every country, language or subnational place.',
    'URL/location deduplication can count syndicated duplicates under separate URLs.',
    'Concentration anomalies are only review triggers.']}

def run_benchmark(fixtures, d7_fn, d8_fn):
 checks=[]
 for f in fixtures:
  a={'title':f['title'],'description':f.get('description','')}
  p={'name':f['selected_place']}
  d7=d7_fn(a,p,{})
  d8=d8_fn(a,p,{},d7)
  action='withhold' if d7.get('action')=='withhold' or d8.get('action')=='withhold' else 'retain'
  c=story_classification({'title':a['title'],'place':p})
  ok=action==f['expect_action'] and (not f.get('expect_classification') or c['classification']==f['expect_classification'])
  checks.append({'id':f['id'],'passed':ok,'expected_action':f['expect_action'],'observed_action':action,
   'expected_classification':f.get('expect_classification'),'observed_classification':c['classification']})
 return {'total':len(checks),'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),
  'passing_pct':round(100*sum(c['passed'] for c in checks)/len(checks),1) if checks else None,
  'failed_cases':[c for c in checks if not c['passed']],
  'note':'Regression expectations curated from prior observed errors and synthetic safety cases; not a representative measured real-world precision score.'}
