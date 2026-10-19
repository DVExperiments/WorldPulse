"""WorldPulse D.11 global publisher-diversity and subnational evidence audit.

Audit only. Gazetteer mentions are lexical candidates, NOT confirmed event locations.
No changes to news pins, feeds, or ranking.
"""
from collections import Counter, defaultdict
import re
from urllib.parse import urlsplit
from geo_quality_d9 import normalize_url, quality_level, story_classification

MAX_CANDIDATES_PER_ARTICLE = 8
MAX_SAMPLES_PER_PLACE = 3


def _words(s):
 return re.findall(r"[^\W_]+", (s or '').casefold(), re.UNICODE)


def _key(a):
 p=a.get('place') or {}
 return (normalize_url(a.get('url','')), str(p.get('name','')).casefold())


def _pub(a):
 name=(a.get('publisher') or '').strip()
 if not name: name=a.get('source_name') or 'Unknown publisher'
 # Case/whitespace normalization, no publisher mergers by guess.
 return ' '.join(name.split())


def _place(a):
 p=a.get('place') or {}
 return str(p.get('name','')).strip()


def _level(a):
 return str((a.get('place') or {}).get('level') or 'unknown').casefold()


def _build_index(places):
 """Token index for unambiguous, substantial place names; names alone are not geocoding."""
 index=defaultdict(list)
 seen=set()
 for p in places or []:
  name=str(p.get('name','')).strip()
  tokens=_words(name)
  if not tokens or len(name)<5 or len(tokens)>5:continue
  # Single ordinary words make poor standalone locality evidence.
  if len(tokens)==1 and (len(tokens[0])<7 or tokens[0] in {'freedom','liberdade','reading','victoria','parliament','georgia','america','turkey','sudan','jordan','anand','sparks','parana','paraná'}):continue
  k=(name.casefold(),str(p.get('level') or '').casefold())
  if k in seen:continue
  seen.add(k)
  if len(index[tokens[0]])<150:index[tokens[0]].append((name,tuple(tokens),str(p.get('level') or 'unknown')))
 return index


def _mentions(title,index,assigned):
 tokens=_words(title); found={}
 for i,token in enumerate(tokens):
  for name,parts,level in index.get(token,[]):
   if tuple(tokens[i:i+len(parts)])!=parts:continue
   if name.casefold()==assigned.casefold():continue
   # A matched locality is only a candidate; geography hierarchy remains unknown.
   found[name.casefold()]={'name':name,'gazetteer_level':level,'evidence':'literal_headline_name_only'}
   if len(found)>=MAX_CANDIDATES_PER_ARTICLE:return list(found.values())
 return list(found.values())


def _ratio(part,total):return round(100.0*part/total,1) if total else 0.0


def report(articles, gazetteer=None, example_limit=MAX_SAMPLES_PER_PLACE):
 """All-location coverage, with bounded samples and no claims of verified event location."""
 unique={}; repeats=Counter(); source_feeds=defaultdict(set)
 for a in articles:
  k=_key(a);repeats[k]+=1
  if k not in unique:unique[k]=a
  source_feeds[k].add(a.get('audit_feed_key') or a.get('source_name') or 'unknown')
 by_place=defaultdict(list); by_url=defaultdict(set)
 for k,a in unique.items():
  by_place[_place(a)].append((k,a))
  by_url[k[0]].add(k[1])
 global_total=len(unique)
 index=_build_index(gazetteer)
 results=[]; global_pub=Counter();global_levels=Counter();anomalies=[]
 for name in sorted(by_place):
  entries=by_place[name]; n=len(entries)
  publishers=Counter();pub_display={};levels=Counter();match_levels=Counter();editions=Counter();categories=Counter();flags=Counter();precisions=Counter();samples=[];candidate_counts=Counter()
  raw_count=0
  for k,a in entries:
   raw_count+=repeats[k]
   publisher=_pub(a);pid=publisher.casefold();publishers[pid]+=1;pub_display.setdefault(pid,publisher);global_pub[pid]+=1
   evidence=quality_level(a);match_levels[evidence]+=1;global_levels[evidence]+=1
   precisions[_level(a)]+=1
   editions[str(a.get('source_region') or 'unknown')]+=1
   categories[str(a.get('category') or 'unknown')]+=1
   title=a.get('title') or '';desc=a.get('description') or ''
   if evidence=='explicit_description_place':flags['description_only_selected_location']+=1
   if evidence=='contextual_or_alias':flags['contextual_or_alias']+=1
   if len(by_url[k[0]])>1:flags['same_url_multiple_locations']+=1
   classif=story_classification(a).get('classification')
   if classif in ('multi_country_unresolved','cross_border_explicit_locality'):flags['multi_country_headline']+=1
   mentions=_mentions(title,index,name)
   if mentions:flags['other_gazetteer_places_in_headline']+=1
   for candidate in mentions:candidate_counts[candidate['name']]+=1
   reason=[]
   if evidence=='explicit_description_place':reason.append('selected_place_description_only')
   if evidence=='contextual_or_alias':reason.append('contextual_match')
   if len(by_url[k[0]])>1:reason.append('one_url_multiple_selected_locations')
   if mentions:reason.append('other_named_gazetteer_places_in_headline')
   if classif in ('multi_country_unresolved','cross_border_explicit_locality'):reason.append('multi_country_headline')
   if reason:
    score=3*('one_url_multiple_selected_locations' in reason)+2*('contextual_match' in reason)+2*('other_named_gazetteer_places_in_headline' in reason)+('selected_place_description_only' in reason)
    samples.append((score,{'title':title[:220],'description_excerpt':desc[:260],'url':a.get('url',''),'publisher':publisher,'source_feed':a.get('audit_feed_key',''),'selected_place':name,'selected_level':_level(a),'evidence_level':evidence,'reason_codes':reason,'other_gazetteer_name_candidates':mentions[:4]}))
  dominant_pub,dominant_count=publishers.most_common(1)[0]
  shares=[c/n for c in publishers.values()]
  hhi=sum(share*share for share in shares)
  ent={'place':name,'location_level':dict(precisions),'distinct_url_location_pairs':n,'share_of_global_pairs_pct':_ratio(n,global_total),
   'raw_feed_observations':raw_count,'repeated_observations':raw_count-n,
   'publisher_count':len(publishers),'dominant_publisher':pub_display[dominant_pub],
   'dominant_publisher_count':dominant_count,'dominant_publisher_share_pct':_ratio(dominant_count,n),
   'publisher_hhi':round(hhi,4),'effective_publishers_simpson':round(1/hhi,2) if hhi else 0,
   'top_publishers':[{'name':pub_display[p],'count':c} for p,c in publishers.most_common(8)],
   'source_edition_counts':dict(editions),'top_categories':dict(categories.most_common(8)),
   'evidence_levels':dict(match_levels),'review_signals':dict(flags),
   'headline_gazetteer_candidate_names':[{'name':x,'article_count':v} for x,v in candidate_counts.most_common(12)],
   'review_samples':[x for _,x in sorted(samples,key=lambda x:(-x[0],x[1]['title']))[:example_limit]]}
  results.append(ent)
  if n>=8 and (_ratio(dominant_count,n)>=75 or _ratio(n,global_total)>=7):
   anomalies.append({'place':name,'mapped_pairs':n,'dominant_publisher':pub_display[dominant_pub],
    'dominant_share_pct':_ratio(dominant_count,n),'reason':'publisher_concentration_or_high_volume_review_not_inaccuracy'})
 results.sort(key=lambda x:(-x['distinct_url_location_pairs'],x['place']))
 return {'schema':1,'release':'v2.4D.11','policy':'Audit only: does not remap, suppress, add pins, change feeds, or assert candidate place locations.',
  'global_summary':{'distinct_url_location_pairs':global_total,'raw_feed_observations':len(articles),'mapped_locations':len(results),
   'publisher_name_variants':len(global_pub),'overall_evidence_levels':dict(global_levels),
   'locations_with_publisher_dominance_75pct_and_at_least_8_pairs':sum(x['distinct_url_location_pairs']>=8 and x['dominant_publisher_share_pct']>=75 for x in results),
   'locations_with_description_only_evidence':sum(x['review_signals'].get('description_only_selected_location',0)>0 for x in results)},
  'publisher_concentration_review':sorted(anomalies,key=lambda x:-x['mapped_pairs'])[:60],
  'location_coverage':'ALL mapped locations, not limited to top-ranked or one country',
  'locations':results,
  'limitations':['Publisher names are only normalized for whitespace and case; aliases are not resolved.',
   'HHI and effective publisher counts describe the sample, not worldwide media independence.',
   'A gazetteer name found in a headline is not proof of the article event location, nor a verified child location of the selected country.',
   'RSS excerpts do not provide full article geolocation; country/region/municipality hierarchy is not inferred.',
   'URL/location pairs are not necessarily distinct events and separate publisher URLs can syndicate one event.',
   'Editorial feed region is never used as geographic event evidence.']}
