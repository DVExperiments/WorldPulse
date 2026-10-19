"""D.8 conservative geographic subject audit. No coordinate creation or geocoding.

Withholding is restricted to recognizable semantic collisions or narrowly tested
unsupported subnational assignments. Other conflicts are REVIEW only.
"""
import re
from collections import Counter
from geo_semantic_d7 import fold

# Small curated dictionary, not a general location detector. Never use these
# mentions to choose new pins; only to identify contrasts for audit.
COUNTRIES = {
 'russia':('russia','russia','rússia','rusia','russie'),
 'ukraine':('ukraine','ucrânia','ucrania','ucrania','ukraine'),
 'israel':('israel','israel','israël'),
 'tunisia':('tunisia','tunísia','túnez','tunisie'),
 'albania':('albania','albânia','albanie'),
 'canada':('canada','canadá'),
 'mexico':('mexico','méxico'),
 'united states':('united states','estados unidos','états-unis'),
 'brazil':('brazil','brasil','brésil'),
 'france':('france','frança'),
 'vietnam':('vietnam','vietnã','viêt nam'),
}
# True nested city/country mentions are not treated as contradictory by default.
NESTED = {'toluca':'mexico','sao paulo':'brazil','são paulo':'brazil',
          'parana':'brazil','paraná':'brazil','liberdade':'brazil'}
# Known confusing placenames, checked with context, NOT wholesale bans.
COMMON_SUBJECT_COLLISIONS={
 'anand':(r'\b(?:mr|ms|dr|professor|minister|actor|player|candidate)\s+anand\b',r'\banand\s+(?:said|says|told|announced|argued|won)\b'),
 'parana':(r'\b(?:rio|estado|provincia|state|river|em|no|na|from|in|near)\s+parana\b',),
}
LOCATION_PREP = r'(?:in|near|at|from|across|around|within|em|no|na|nos|nas|en|a|au|dans|di|nel|nella)'

def contains(t, phrase):
 return bool(re.search(r'(?<!\w)'+re.escape(fold(phrase))+r'(?!\w)',fold(t)))

def countries_in(title):
 t=fold(title)
 return sorted(k for k, aliases in COUNTRIES.items() if any(contains(t,a) for a in aliases))

def explicit_locality(text,place):
 name=fold(place)
 return bool(name and re.search(r'\b'+LOCATION_PREP+r'\s+(?:(?:the|o|a|la|le)\s+)?'+re.escape(name)+r'\b',fold(text)))

def decision(article,place,d6=None,d7=None):
 title=article.get('title','') or ''; desc=article.get('description','') or ''
 name=(place or {}).get('name','') or ''; n=fold(name)
 headline=countries_in(title)
 result={'action':'retain','reason':'no_d8_intervention','selected_place':name,'title':title[:180],
         'headline_countries':headline,'headline_places':(d6 or {}).get('headline_places',[])[:12],
         'selected_in_title':contains(title,name),'selected_in_description':contains(desc,name),
         'explicit_selected_locality':explicit_locality(title+' '+desc,name),'multi_country':len(headline)>1}
 if (d7 or {}).get('action')=='withhold':
  result.update(action='review',reason='already_handled_by_d7');return result
 # Retain explicit local locality, even if other nations are mentioned.
 if explicit_locality(title,name):
  if len(headline)>1:result.update(action='review',reason='cross_border_local_story')
  return result
 # Person-name collision with no locality: strict contextual phrasing.
 if n=='anand' and any(re.search(p,fold(title)) for p in COMMON_SUBJECT_COLLISIONS['anand']):
  result.update(action='withhold',reason='person_name_collision');return result
 # Specific previously observed false positive: a Brazil state chosen for a
 # sanctions article explicitly about Russia, with no Paraná locality phrase.
 # Check description as well, and never infer replacement coordinates.
 if n in ('parana',) and 'russia' in headline and not explicit_locality(title+' '+desc,name):
  result.update(action='withhold',reason='unsupported_parana_russia_conflict');return result
 # Review, not remove, international stories and unsupported description pins.
 if len(headline)>1:
  result.update(action='review',reason='multiple_country_roles_unresolved')
 elif headline and not contains(title,name):
  # Avoid treating a recognized parent and child as incompatible.
  parent=NESTED.get(n)
  if parent not in headline:
   result.update(action='review',reason='headline_subject_differs_from_selected')
 elif n in ('anand','parana') and not contains(title,name):
  result.update(action='review',reason='ambiguous_place_only_in_description')
 return result

def summary(records,max_samples=70):
 c=Counter(x['action'] for x in records)
 reasons=Counter(x['reason'] for x in records if x['action']!='retain')
 return {'policy':'Narrow contextual suppression plus review-only multi-country role detection; no automatic relocation.',
         'decision_counts':dict(c),'reason_counts':dict(reasons),
         'withheld_samples':[x for x in records if x['action']=='withhold'][:max_samples],
         'review_samples':[x for x in records if x['action']=='review'][:max_samples],
         'limitations':['A headline country can be an actor, target, comparison, or event site.',
                        'Selected geographic names are not independently verified event locations.',
                        'Review and withholding counts are feed observations before deduplication.']}
