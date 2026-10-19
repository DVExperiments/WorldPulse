"""D.10 audit-only location accumulation investigation. Does not change matching or pins."""
from collections import Counter, defaultdict
from urllib.parse import urlsplit
import re
from geo_quality_d9 import normalize_url, quality_level, story_classification

CONTEXT_TERMS = {'in','at','near','across','from','within','outside','throughout','en','em','no','na','nos','nas','à','au','dans','di','a','de','del'}
STOPWORDS = {'the','for','and','with','from','that','this','over','after','about','says','news','will','amid','more','into','have','than','were','been'}

def word_present(text, term):
 return bool(term and re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',text or '',re.I))

def headline_evidence(title, place):
 """Diagnostic only: syntactic locality cue, not proof of event location."""
 if not place or not word_present(title,place):return 'not_named_in_headline'
 p=re.search(r'(?<!\w)'+re.escape(place)+r'(?!\w)',title,re.I)
 before=title[max(0,p.start()-36):p.start()].casefold()
 tokens=re.findall(r'\w+',before)
 if tokens and tokens[-1] in CONTEXT_TERMS:return 'preposition_locality_cue'
 if re.search(r'\b(?:city of|state of|province of|region of|capital of)\s*$',before):return 'qualified_locality_cue'
 return 'name_in_headline_no_locality_cue'

def key_for(a):
 place=(a.get('place') or {}).get('name','').strip()
 return (normalize_url(a.get('url')),place.casefold())

def topic_fingerprint(title):
 words=[w for w in re.findall(r'[a-zA-ZÀ-ÿ]{4,}',(title or '').lower()) if w not in STOPWORDS]
 return tuple(sorted(set(words)))

def report(articles,points=None,focus_locations=('Vietnam',),sample_limit=18,top_n=12):
 """Counts URL/location pairs, conservatively flags possible contextual contamination.

 No claim of actual event-location verification or exact syndication detection.
 """
 unique={}; feed_occurrences=Counter(); url_places=defaultdict(set)
 for a in articles:
  k=key_for(a); feed_occurrences[k]+=1
  unique.setdefault(k,a)
  url_places[k[0]].add(k[1])
 by_place=defaultdict(list)
 for a in unique.values():by_place[(a.get('place') or {}).get('name','')].append(a)
 targets=set(focus_locations)|{name for name,_ in sorted(((n,len(v)) for n,v in by_place.items() if n),key=lambda item:-item[1])[:top_n]}
 results=[]
 for name in sorted(targets,key=lambda x:(-len(by_place.get(x,[])),x)):
  group=by_place.get(name,[]); levels=Counter(); headline_cues=Counter(); reasons=Counter(); multi_count=0
  suspects=[]; recurring=defaultdict(list); sources=Counter(); feed_editions=Counter()
  for a in group:
   title=a.get('title','');desc=a.get('description','');k=key_for(a)
   lvl=quality_level(a);cue=headline_evidence(title,name)
   levels[lvl]+=1;headline_cues[cue]+=1
   multi=story_classification(a)['classification'] in ('multi_country_unresolved','cross_border_explicit_locality')
   multi_count+=int(multi)
   sources[a.get('publisher') or a.get('source_name') or 'unknown']+=1
   feed_editions[a.get('source_region') or 'unknown']+=1
   if lvl=='explicit_description_place' and not word_present(title,name):reasons['description_only_selected_place']+=1
   if lvl=='contextual_or_alias':reasons['contextual_or_alias_assignment']+=1
   if multi:reasons['multi_country_headline']+=1
   if len(url_places[k[0]])>1:reasons['same_url_multiple_selected_places']+=1
   if feed_occurrences[k]>1:reasons['repeated_feed_observations']+=1
   fp=topic_fingerprint(title)
   if len(fp)>2:recurring[fp].append(a)
   priority=(3 if lvl=='explicit_description_place' else 4 if lvl=='contextual_or_alias' else 0)+(2 if multi else 0)+(2 if len(url_places[k[0]])>1 else 0)
   if priority:
    suspects.append((priority,{'title':title[:220],'url':a.get('url',''),'selected_place':name,
      'evidence_level':lvl,'headline_cue':cue,'source_feed':a.get('audit_feed_key',''),
      'feed_edition':a.get('source_region',''),'publisher':a.get('publisher',''),
      'other_places_for_same_url':sorted(url_places[k[0]]-{name.casefold()}),
      'headline_country_classification':story_classification(a)['classification'],
      'reason':'Prioritized for human inspection, not established as incorrect'}))
  repeat_title_groups=sum(1 for v in recurring.values() if len({normalize_url(x.get('url')) for x in v})>1)
  results.append({'place':name,'distinct_url_location_pairs':len(group),'raw_feed_observations':sum(feed_occurrences[key_for(a)] for a in group),
    'duplicate_feed_observations':sum(feed_occurrences[key_for(a)]-1 for a in group),
    'evidence_levels':dict(levels),'headline_locality_cues':dict(headline_cues),
    'multi_country_headlines':multi_count,'review_signals':dict(reasons),
    'similar_title_groups_across_distinct_urls':repeat_title_groups,
    'top_publishers':[{'name':x,'count':v} for x,v in sources.most_common(8)],
    'source_editorial_regions':dict(feed_editions),
    'review_samples':[a for _,a in sorted(suspects,key=lambda x:(-x[0],x[1]['title']))[:sample_limit]]})
 return {'schema':1,'policy':'Audit-only. No new or removed pins, remaps, feed changes, or automated correctness judgements.',
  'raw_mapped_observations':len(articles),'distinct_url_location_pairs':len(unique),
  'focus_locations':list(focus_locations),'locations':results,
  'limitations':['URL/location pairs are not unique news events; syndicated articles can have different URLs.',
   'Preposition and literal place-name evidence are weak textual heuristics, not verified event locations.',
   'Description-only assignments and multi-country stories are review candidates, not proven errors.',
   'Published source edition is never used as location proof.',
   'The source files are not full article bodies, only RSS titles and descriptions.']}
