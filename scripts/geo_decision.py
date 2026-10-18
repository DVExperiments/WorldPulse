"""WorldPulse 2.0E.2: conservative headline-over-description geography correction.

Only override a description-based selection when one unique vetted E catalogue
subject is stated in the headline. No URL, publisher, feed-region or AI inference.
A named geographic subject is not a verified incident coordinate.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
from geo_accuracy_audit import mentioned_places, reviewed_catalogue
from geo_expansion import ROWS

CATALOGUE=reviewed_catalogue()
PLACES={name:{'name':name,'level':level,'lat':lat,'lng':lng} for name,level,lat,lng,_ in ROWS}

class DecisionAudit:
 def __init__(self):
  self.counts=Counter();self.examples=[]
 def decide(self, article, place, method):
  self.counts['reviewed_mapped_candidates']+=1
  if not str(method).startswith('description'):
   self.counts['unchanged_not_description_based']+=1
   return place,method
  names=mentioned_places(article.get('title',''),CATALOGUE)
  if not names:
   self.counts['unchanged_no_reviewed_headline_place']+=1
   return place,method
  if len(names)!=1:
   self.counts['withheld_multiple_headline_places']+=1
   return place,method
  name=names[0]
  if name==place.get('name'):
   self.counts['unchanged_already_agrees']+=1
   return place,method
  if name not in PLACES:
   self.counts['withheld_missing_catalogue_record']+=1
   return place,method
  # Preserve the exact reviewed region/city anchor. Mark as subject only.
  replacement=PLACES[name].copy()
  self.counts['corrected_to_explicit_headline_place']+=1
  if len(self.examples)<40:
   self.examples.append({'title':str(article.get('title',''))[:180],
      'publisher':str(article.get('publisher',''))[:90],
      'previous_place':place.get('name'),'corrected_place':name,
      'previous_method':str(method), 'new_method':'headline-reviewed-correction',
      'reason':'unique_reviewed_headline_subject_over_description',
      'url':str(article.get('url',''))[:300]})
  return replacement,'headline-reviewed-correction'
 def publish(self,folder,now):
  target=Path(folder)/'unmatched-review.json'
  if not target.exists():raise RuntimeError('Missing unmatched-review.json: cannot publish correction audit')
  doc=json.loads(target.read_text(encoding='utf8'))
  doc['geo_decision_corrections']={
   'schema':1,'version':'2.0E.2','generated_at':now.isoformat(),
   'scope':'eligible mapped feed occurrences, before deduplication',
   'counts':dict(self.counts),'examples':self.examples,
   'policy':'Only unique E-catalogue explicit headline subjects override different description-based selections; all other choices unchanged.',
   'limitations':'Catalogue is incomplete. A subject is not a verified event location. Some explicit mentions may be incidental; inspect correction examples.'}
  target.write_text(json.dumps(doc,ensure_ascii=False,indent=1),encoding='utf8')
  print('WorldPulse v2.0E.2: decision-correction report published',flush=True)
