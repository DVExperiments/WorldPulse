"""WorldPulse D.5: bounded, explainable location-evidence and coverage diagnostics.

Audit only. A geographic SUBJECT is not a verified event site. Feed editions are
separate discovery metadata. Never auto-geocode from evidence diagnostics.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import re
import unicodedata

REGIONS = ('Africa','Asia','Europe','North America','South America','Oceania','Antarctica')
# Diagnostic-only signals; these do not authorize adding a globe pin.
COUNTRY_TERMS = {
 'alemania':'Germany','allemagne':'Germany','deutschland':'Germany',
 'schweiz':'Switzerland','suisse':'Switzerland','suiza':'Switzerland',
 'italia':'Italy','italie':'Italy','italien':'Italy',
 'francia':'France','frança':'France','france':'France','frankreich':'France',
 'japon':'Japan','japão':'Japan','japan':'Japan',
 'india':'India','índia':'India','inde':'India',
 'kenia':'Kenya','quênia':'Kenya','kenya':'Kenya',
 'nigeria':'Nigeria','nigéria':'Nigeria',
 'china':'China','chine':'China',
 'ucrania':'Ukraine','ucrânia':'Ukraine','ukraine':'Ukraine',
 'reino unido':'United Kingdom','royaume-uni':'United Kingdom',
 'estados unidos':'United States','etats-unis':'United States',
 'brasil':'Brazil','brazil':'Brazil','méxico':'Mexico',
 'argentina':'Argentina','colombia':'Colombia','colômbia':'Colombia',
 'afrique du sud':'South Africa','áfrica do sul':'South Africa',
 'nueva zelanda':'New Zealand','nouvelle-zélande':'New Zealand'
}
LOCATION_CUES=(' in ',' en ',' em ',' no ',' na ',' au ',' aux ',' dans ',' at ',' near ',' from ',' de ',' do ',' da ',' del ',' von ',' im ',' bei ')

def folded(value):
 value=unicodedata.normalize('NFKD',(value or '').casefold())
 return ''.join(c for c in value if not unicodedata.combining(c))

def evidence_for_match(article):
 """Trace observed literal evidence, not a confidence probability."""
 p=article.get('place') or {}; name=p.get('name',''); title=article.get('title','') or ''; description=article.get('description','') or ''
 literal_name=folded(name)
 def contains(value):
  return bool(literal_name and re.search(r'(?<!\w)'+re.escape(literal_name)+r'(?!\w)',folded(value)))
 fields=[field for field,value in (('headline',title),('description',description)) if contains(value)]
 method=article.get('geo_match','unknown')
 return {'place':name,'place_level':p.get('level','unknown'),'matching_method':method,
         'literal_place_fields':fields,'evidence_class':('literal_name_in_headline' if 'headline' in fields else 'literal_name_in_description' if fields else 'contextual_or_alias_match'),
         'interpretation':'geographic_subject_not_verified_event_location',
         'confidence_label':'direct_literal' if fields else 'contextual_review',
         'note':'Rule-based evidence label, not a calibrated probability or verified event coordinate.'}

def candidates_for_review(title, description, max_candidates=6):
 """Detect explicit multilingual country words; review only, not automatic mapping."""
 mentions=[]
 for field,value in (('headline',title),('description',description)):
  clean=' '+folded(re.sub(r'<[^>]*>',' ',value or ''))+' '
  for alias,country in COUNTRY_TERMS.items():
   term=folded(alias)
   rx=r'(?<!\w)'+re.escape(term)+r'(?!\w)'
   if re.search(rx,clean):
    start=re.search(rx,clean).start()
    left=clean[max(0,start-16):start]
    cue=any(left.endswith(prefix) for prefix in LOCATION_CUES)
    mentions.append({'country':country,'alias':alias,'field':field,'qualified':cue})
 if not mentions:return []
 unique={}
 for m in mentions:
  key=(m['country'],m['field'])
  if key not in unique or (m['qualified'] and not unique[key]['qualified']):unique[key]=m
 return list(unique.values())[:max_candidates]

def coverage_report(raw, points, unmapped, feeds, max_samples=35):
 """Coverage is grouped by *matched place*, not by Google feed edition.

 No continents are inferred from country or centroid (country -> continent
 needs a verified gazetteer). Region is therefore reported as country/place
 names plus geographic latitude hemispheres, with unknown explicit.
 """
 kept=Counter(); by_place=Counter(); by_level=Counter(); by_hemisphere=Counter(); by_method=Counter(); by_evidence=Counter()
 country_lang=defaultdict(Counter); editorial=defaultdict(Counter); strong_examples=[]; weak_examples=[]; cross_source=Counter()
 for a in raw:
  p=a.get('place') or {}; name=p.get('name') or 'unknown'; by_place[name]+=1;by_level[p.get('level','unknown')]+=1
  try:lat=float(p['lat']);lng=float(p['lng']);hem=('N' if lat>=0 else 'S')+('E' if lng>=0 else 'W')
  except (TypeError,ValueError,KeyError):hem='unknown'
  by_hemisphere[hem]+=1
  method=a.get('geo_match','unknown');by_method[method]+=1
  ev=evidence_for_match(a);by_evidence[ev['evidence_class']]+=1
  if len(strong_examples)<max_samples and ev['literal_place_fields']:
   strong_examples.append({'title':a.get('title','')[:170],**ev})
  elif len(weak_examples)<max_samples and not ev['literal_place_fields']:
   weak_examples.append({'title':a.get('title','')[:170],**ev})
  region=a.get('source_region','unknown');editorial[region]['matched_rows']+=1
  if p.get('level')=='country':country_lang[name][a.get('language','unknown')]+=1
  if region and region not in ('international','unknown') and p.get('level')=='country':cross_source[(region,name)]+=1
 for f in feeds:
  editorial[f.get('editorial_region','unknown')]['feed_count']+=1
  editorial[f.get('editorial_region','unknown')]['globe_articles']+=f.get('globe_articles',0)
  editorial[f.get('editorial_region','unknown')]['geography_unmatched']+=f.get('geography_unmatched',0)
 for point in points:kept[point.get('name','unknown')]+=len(point.get('articles',[]))
 review=[]; reasons=Counter(); multi=0
 for item in unmapped:
  title=item.get('title','');desc=item.get('description','')
  candidates=candidates_for_review(title,desc)
  distinct={c['country'] for c in candidates}
  if len(distinct)>1:reason='multiple_country_mentions';multi+=1
  elif len(distinct)==1:reason='explicit_country_candidate_requires_review'
  elif re.search(r'\b(?:globally|global|worldwide|internationally)\b',title,re.I):reason='global_or_nonlocal_topic'
  else:reason='no_diagnostic_country_mention'
  reasons[reason]+=1
  if candidates and len(review)<max_samples:
   review.append({'title':title[:190],'feed':item.get('feed'),'candidates':candidates,'review_class':reason,'url':item.get('url'),'mapping_action':'none_manual_review_only'})
 return {'schema':1,'scope':'one collection run, duplicate feed entries counted before deduplication',
   'location_semantics':'matched geographic subject; verified incident location unavailable',
   'mapped_before_dedupe':len(raw),'globe_serialized_articles':sum(kept.values()),
   'mapped_by_place_top':dict(by_place.most_common(45)),
   'globe_by_place_top':dict(kept.most_common(45)),
   'mapped_by_place_level':dict(by_level),'mapped_by_hemisphere':dict(by_hemisphere),
   'mapped_by_method':dict(by_method),'mapped_by_literal_evidence':dict(by_evidence),
   'mapped_country_languages':{k:dict(v) for k,v in sorted(country_lang.items())},
   'discovery_edition_vs_actual_match':{k:dict(v) for k,v in sorted(editorial.items())},
   'edition_to_country_subject_top':[{'feed_edition':k[0],'subject_country':k[1],'mapped_rows':v} for k,v in cross_source.most_common(40)],
   'unmatched_diagnostic_counts':dict(reasons),
   'unmatched_multi_country_rows':multi,
   'unmatched_language_candidate_examples':review,
   'matched_literal_evidence_examples':strong_examples[:15],
   'matched_contextual_review_examples':weak_examples[:20],
   'limitations':['Not all source editions are region-specific','A feed region is never used to establish story location',
     'Multilingual candidates are diagnostic only and do not create pins','Counts are per feed row and include duplicate entries',
     'No continental classification inferred from coordinates or country strings',
     'Literal place mentions do not guarantee that the event happened there']}
