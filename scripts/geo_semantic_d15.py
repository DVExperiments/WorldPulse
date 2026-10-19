"""D15 shadow-only semantic validation of D14 geographic review flags.

Curated, explainable signals; never changes the live matcher or publishes pins.
An alert is not a verified geolocation or a confirmed error.
"""
from collections import Counter, defaultdict
import re
import unicodedata
try:
 from .geo_hierarchy_d14 import mentions
except ImportError:
 from geo_hierarchy_d14 import mentions

# Only explicit, unambiguous parent relationships used to downgrade apparent
# headline conflicts. Don't treat all cities in the world as covered.
PARENT = {
 'paris':'France','kyiv':'Ukraine','kiev':'Ukraine','toluca':'Mexico',
 'santiago':'Chile','santiago de chile':'Chile','california':'United States',
 'mumbai':'India','bombay':'India','apodaca':'Mexico','nuevo león':'Mexico',
 'new york':'United States','new york city':'United States',
 'marseille':'France','lyon':'France','nairobi':'Kenya',
 'accra':'Ghana','con dao':'Vietnam','khanh hoa':'Vietnam',
 'mexico city':'Mexico','ciudad de méxico':'Mexico',
 'rio de janeiro':'Brazil','são paulo':'Brazil','london':'United Kingdom',
 'berlin':'Germany','wellington':'New Zealand','auckland':'New Zealand'
}
# Do not blanket-block these geographic names. A collision warning requires
# explicit contextual hints that the phrase is a common word instead.
COLLISIONS = {
 'lagos': (r'\b(lagos?\s+(?:del|de|en|andinos|chilenos|naturales)|los\s+lagos|lagos\s+de\s+chile)\b', 'Spanish common noun for lakes'),
 'réunion': (r'\b(reuni[oó]n(?:es)?|reuniao|reunião)\b', 'meeting in Spanish or Portuguese'),
 'liberdade': (r'\b(?:liberdade\s+de|pela\s+liberdade|direito\s+[àa]\s+liberdade)\b', 'Portuguese freedom expression'),
 'sparks': (r'\b(?:sparks?\s+(?:debate|outrage|concern|protests?|controversy))\b', 'English verb sparks'),
}

def norm(s):
 return unicodedata.normalize('NFKC',s or '').casefold()

def classify(title, cleaned_description, selected_place, d14):
 title=title or ''; selected=selected_place or ''
 base=d14.get('decision','unknown')
 country_in_title=mentions(title)
 parents={p for name,p in PARENT.items() if norm(name)==norm(selected)}
 for p in list(parents):
  # Parent evidence must be an explicit country alias in headline, not publisher geography.
  if p in country_in_title:
   return {'decision':'hierarchy_consistent','d14_decision':base,'parent_country':p,
           'reason':'selected locality has curated parent matching headline country',
           'evidence_phrase':country_in_title[p]['phrase'],'live_action':'none'}
 collision=COLLISIONS.get(norm(selected))
 if collision and re.search(collision[0],norm(title),flags=re.I):
  return {'decision':'language_collision_review','d14_decision':base,'parent_country':None,
          'reason':collision[1],'evidence_phrase':None,'live_action':'none'}
 if base=='potential_headline_country_contradiction':
  return {'decision':'potential_contradiction_review','d14_decision':base,'parent_country':None,
          'reason':'one other country named; missing verified supporting hierarchy',
          'evidence_phrase':d14.get('contradiction_country'),'live_action':'none'}
 if base=='multicountry_requires_review':
  decision='multicountry_context_review'
 elif base=='supported_by_headline' or base=='supported_by_clean_description':
  decision='retained_independent_evidence'
 else:
  decision='unresolved_geographic_evidence'
 return {'decision':decision,'d14_decision':base,'parent_country':None,
         'reason':'limited curated evidence; no automatic suppression',
         'evidence_phrase':None,'live_action':'none'}

def report(rows, max_samples=120):
 unique={}
 for r in rows:unique.setdefault((r.get('url',''),r.get('selected_place','')),r)
 vals=list(unique.values()); counts=Counter(r['decision'] for r in vals)
 change=Counter((r.get('d14_decision'),r['decision']) for r in vals)
 focus={'hierarchy_consistent','language_collision_review','potential_contradiction_review','multicountry_context_review'}
 by_place=defaultdict(list)
 for r in vals:
  if r['decision'] in focus:by_place[r.get('selected_place','')].append(r)
 for entries in by_place.values():entries.sort(key=lambda x:(x['decision'],x.get('title','')))
 samples=[]
 for i in range(max(map(len,by_place.values()),default=0)):
  for place in sorted(by_place):
   if i<len(by_place[place]):
    r=by_place[place][i]
    samples.append({k:r.get(k) for k in ('title','url','selected_place','publisher','decision','d14_decision','parent_country','reason','evidence_phrase')})
    if len(samples)>=max_samples:break
  if len(samples)>=max_samples:break
 return {'release':'v2.4D.15','mode':'shadow_only_no_live_changes',
  'distinct_url_location_pairs':len(vals),'decision_counts':dict(counts),
  'd14_to_d15': [{'prior':a,'new':b,'count':n} for (a,b),n in sorted(change.items())],
  'review_locations':len(by_place),'balanced_review_samples':samples,
  'sampled_locations':len({s['selected_place'] for s in samples}),
  'known_parent_relationships':len(PARENT),'common_word_collision_patterns':list(COLLISIONS),
  'limits':['A collision alert is not proof that a geographic match is false.',
   'Hierarchy consistency is based on a small curated set; country mention alone does not prove an incident location.',
   'No network geocoding or country-wide verified administrative gazetteer is used.',
   'No automatic removal, relocation or suppression of globe articles.']}
