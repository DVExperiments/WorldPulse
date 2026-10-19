"""D.7: narrow, inspectable false-positive guard; never assigns new coordinates.

Only blocks validated lexical false-positive patterns or independently contradictory
explicit country mentions. All other uncertainty is review-only.
"""
from collections import Counter
import re
import unicodedata

# Contextual rules, not a general ban on city names. A legitimate city mention
# outside these exact ordinary-language phrases stays eligible for prior matchers.
COMMON_WORD_RULES = {
 'liberdade': (r'\b(?:mais|pela|por|da|de|à|a)\s+liberdade\b',
               r'\bliberdade\s+(?:de|para|e|ou|religiosa|individual|de expressão)\b'),
 'sparks': (r'\b(?:sparks|sparked)\s+(?:debate|outrage|controversy|protests?|fears?|concern|anger)\b',
            r'\b(?:dispute|decision|announcement|policy|report)\s+sparks\b'),
 'reading': (r'\breading\s+(?:books?|skills?|scores?|levels?|list|material)\b',),
 'nice': (r'\b(?:a|very|quite|really)\s+nice\s+(?:day|gesture|place|surprise|thing)\b',),
 'mobile': (r'\bmobile\s+(?:phones?|devices?|apps?|networks?|technology|data)\b',),
 'orange': (r'\borange\s+(?:juice|fruit|peel|trees?|colour|color)\b',),
}

def fold(s):
 return ''.join(c for c in unicodedata.normalize('NFKD',str(s or '').casefold()) if not unicodedata.combining(c))

def words(text, phrase):
 return bool(re.search(r'(?<!\w)'+re.escape(fold(phrase))+r'(?!\w)',fold(text)))

def decision(article, place, d6=None):
 title=article.get('title','') or ''
 desc=article.get('description','') or ''
 name=(place or {}).get('name','')
 normalized=fold(name)
 t=fold(title); b=fold(desc)
 result={'action':'retain','reason':'no_narrow_semantic_block','selected_place':name,
         'title':title[:180],'headline_places':(d6 or {}).get('headline_places',[])[:12],
         'matched_rule':None}
 rules=COMMON_WORD_RULES.get(normalized,())
 if rules:
  hits=[pattern for pattern in rules if re.search(pattern,t)]
  # Don't suppress a city merely for occurring in a stock phrase when the
  # headline also uses explicit physical-locality syntax (e.g. "in Sparks").
  locality=bool(re.search(r'\b(?:in|near|at|from|across|around|em|na|no|de|en)\s+'+re.escape(normalized)+r'\b',t))
  if hits and not locality:
   result.update(action='withhold',reason='common_word_place_collision',matched_rule=hits[0]);return result
 # Missing headline evidence is a review hint rather than a block: a location
 # can legitimately appear only in the description or supported metadata.
 heads=(d6 or {}).get('headline_places') or []
 if heads and name not in heads and not words(title,name):
  result.update(action='review',reason='headline_place_differs_from_selected')
 elif (d6 or {}).get('multiple_headline_places'):
  result.update(action='review',reason='multiple_headline_places')
 elif normalized in COMMON_WORD_RULES and not words(title,name):
  result.update(action='review',reason='ambiguous_name_without_headline_support')
 return result

def summary(records, max_samples=50):
 count=Counter(r['action'] for r in records)
 reasons=Counter(r['reason'] for r in records if r['action']!='retain')
 return {'policy':'Targeted semantic false-positive rules; never relocates an article. All non-blocking uncertainty remains review-only.',
         'decision_counts':dict(count),'reason_counts':dict(reasons),
         'withheld_samples':[r for r in records if r['action']=='withhold'][:max_samples],
         'review_samples':[r for r in records if r['action']=='review'][:max_samples],
         'limitations':['Descriptions or missing city-country containment metadata cannot establish event locations.',
                        'Lexical patterns are narrow and cannot catch all false positives.',
                        'Counts are feed-entry observations before deduplication.']}
