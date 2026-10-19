"""WorldPulse D.6: independent geographic attribution checks.

This module does not invent coordinates or infer locations from the feed edition.
When a unique, explicitly named headline place conflicts with a description-only
choice, it withholds the article pending review rather than guessing.
"""
from collections import Counter
import re
import unicodedata

AMBIGUOUS_TERMS={'anand','nice','reading','mobile','jordan','georgia','victoria','turkey','orange','java','washington'}

def fold(s):
 return ''.join(c for c in unicodedata.normalize('NFKD',(s or '').casefold()) if not unicodedata.combining(c))

def mentions(text, places):
 value=fold(text)
 found={}
 for p in places:
  name=p.get('name','')
  if len(name)<4 or fold(name) in AMBIGUOUS_TERMS:continue
  if re.search(r'(?<!\w)'+re.escape(fold(name))+r'(?!\w)',value):
   found[name]=p
 return list(found.values())

def audit_decision(article,place,places):
 title=article.get('title','');desc=article.get('description','')
 head=mentions(title,places);body=mentions(desc,places)
 selected=(place or {}).get('name','')
 head_names=sorted({p['name'] for p in head});body_names=sorted({p['name'] for p in body})
 # A country and a city in its country may both be present; this diagnostic
 # cannot establish geographic containment and therefore never chooses one.
 conflict=bool(head_names and selected not in head_names)
 multi=len(head_names)>1
 ambiguous=sorted({name for name in re.findall(r'\b[A-Za-z]{4,}\b',title.casefold()) if name in AMBIGUOUS_TERMS})
 action='review'
 if conflict and len(head_names)==1 and selected in body_names:
  action='withhold_description_conflict'
 elif not conflict and not multi and not ambiguous:
  action='retain'
 return {'action':action,'selected_place':selected,'headline_places':head_names[:12], 'description_places':body_names[:12],
         'headline_description_disagree':conflict,'multiple_headline_places':multi,'ambiguous_tokens':ambiguous[:8],
         'note':'Mentions are not verified event locations. Other existing matchers may recognize additional aliases.'}

def summary(records,withheld,max_samples=45):
 c=Counter(r.get('action','unknown') for r in records)
 disagreements=[r for r in records if r.get('headline_description_disagree')]
 multi=[r for r in records if r.get('multiple_headline_places')]
 return {'policy':'conservative headline-versus-description diagnostic; only single explicit headline / conflicting description choices are withheld',
  'decision_counts':dict(c),'disagreement_count':len(disagreements),'multi_headline_place_count':len(multi),
  'withheld_count':len(withheld), 'withheld_samples':withheld[:max_samples],
  'disagreement_samples':disagreements[:max_samples], 'multi_place_samples':multi[:max_samples],
  'important_limits':['Mentions are not confirmed event locations.','Names can be nested (city and country), so multiple matches are review-only.','No automated mapping from ambiguous person/place tokens.']}
