"""D16 non-publishing geographic correction trials and labelled regression benchmark.

Only produces hypothetical actions. Live matching and serialization are untouched.
"""
from collections import Counter,defaultdict
import re
import unicodedata

# Known ambiguous place/common-word collisions. Narrow context required.
PATTERNS={
 'lagos':(r'\b(?:los\s+lagos|lagos\s+(?:de|del|en|chilenos|andinos|naturales))\b','Spanish lakes'),
 'réunion':(r'\b(?:reuni[oó]n(?:es)?|reuni[aã]o)\b','Spanish/Portuguese meeting'),
 'liberdade':(r'\b(?:liberdade\s+de|pela\s+liberdade|direito\s+[àa]\s+liberdade)\b','Portuguese freedom'),
 'sparks':(r'\b(?:sparks?\s+(?:debate|outrage|concern|protests?|controversy))\b','English verb'),
}
def norm(s):return unicodedata.normalize('NFKC',s or '').casefold()

def simulate(title,selected_place,clean_description,isolation_status,d15_decision):
 """Shadow candidate; no actual correction. Explicit evidence protects a case from a drop proposal."""
 name=norm(selected_place); title_n=norm(title)
 pattern=PATTERNS.get(name)
 if pattern and re.search(pattern[0],title_n,re.I):
  return {'trial':'semantic_collision','candidate_action':'withhold_for_review','reason':pattern[1], 'confidence':'review_only'}
 if d15_decision in ('hierarchy_consistent','retained_independent_evidence'):
  return {'trial':'metadata_isolation','candidate_action':'retain','reason':'independent or hierarchy-consistent evidence','confidence':'supported'}
 if isolation_status=='lost_after_isolation':
  return {'trial':'metadata_isolation','candidate_action':'withhold_for_review','reason':'candidate matcher loses selected location after publisher metadata removal','confidence':'review_only'}
 if isolation_status=='changed_after_isolation':
  return {'trial':'metadata_isolation','candidate_action':'relocate_for_review','reason':'candidate matcher selects a different location','confidence':'review_only'}
 return {'trial':'baseline','candidate_action':'retain','reason':'no narrowly actionable signal','confidence':'unverified'}

# Labels are for synthetic/curated headline-place cases, NOT the current feed sample.
BENCHMARK=[
 {'title':'Los lagos de Chile captan el turismo','place':'Lagos','description':'Lagos de Chile','isolation':'no_identifiable_publisher_metadata','d15':'language_collision_review','label':'false'},
 {'title':'Reunión del parlamento en Madrid','place':'Réunion','description':'','isolation':'no_identifiable_publisher_metadata','d15':'language_collision_review','label':'false'},
 {'title':'Pela liberdade de expressão','place':'Liberdade','description':'','isolation':'no_identifiable_publisher_metadata','d15':'language_collision_review','label':'false'},
 {'title':'New policy sparks debate in London','place':'Sparks','description':'','isolation':'no_identifiable_publisher_metadata','d15':'language_collision_review','label':'false'},
 {'title':'Flooding in Lagos disrupts Nigerian transport','place':'Lagos','description':'Flooding in Nigeria','isolation':'no_identifiable_publisher_metadata','d15':'retained_independent_evidence','label':'true'},
 {'title':'A volcanic eruption on Réunion island','place':'Réunion','description':'Réunion island','isolation':'no_identifiable_publisher_metadata','d15':'retained_independent_evidence','label':'true'},
 {'title':'Paris protest draws crowds across France','place':'Paris','description':'France','isolation':'no_identifiable_publisher_metadata','d15':'hierarchy_consistent','label':'true'},
 {'title':'IIT Bombay students protest','place':'Mumbai','description':'India','isolation':'lost_after_isolation','d15':'hierarchy_consistent','label':'true'},
 {'title':'International prices rise amid uncertainty','place':'Vietnam','description':'International prices rise','isolation':'lost_after_isolation','d15':'unresolved_geographic_evidence','label':'ambiguous'},
 {'title':'Ukraine energy grid damaged by attacks','place':'Vietnam','description':'Ukraine','isolation':'lost_after_isolation','d15':'potential_contradiction_review','label':'ambiguous'},
 {'title':'Diplomatic talks between Egypt and Saudi Arabia','place':'Egypt','description':'','isolation':'no_identifiable_publisher_metadata','d15':'multicountry_context_review','label':'ambiguous'},
]
def benchmark():
 outcomes=[];counts=Counter()
 for case in BENCHMARK:
  res=simulate(case['title'],case['place'],case['description'],case['isolation'],case['d15'])
  flag=res['candidate_action']!='retain';label=case['label'];counts[label]+=1
  outcomes.append({'title':case['title'],'place':case['place'],'label':label,'candidate_action':res['candidate_action'],'flagged':flag})
 tp=sum(x['flagged'] for x in outcomes if x['label']=='false')
 fp=sum(x['flagged'] for x in outcomes if x['label']=='true')
 fn=sum(not x['flagged'] for x in outcomes if x['label']=='false')
 tn=sum(not x['flagged'] for x in outcomes if x['label']=='true')
 return {'dataset':'curated_synthetic_regressions_not_representative_live_accuracy','cases':len(outcomes),'labels':dict(counts),
         'verified_false_flagged':tp,'verified_false_missed':fn,'verified_true_flagged':fp,'verified_true_retained':tn,
         'precision_on_binary_labelled_cases_pct':round(100*tp/(tp+fp),1) if tp+fp else None,
         'recall_on_binary_labelled_cases_pct':round(100*tp/(tp+fn),1) if tp+fn else None,
         'ambiguous_cases_excluded_from_binary_metrics':counts['ambiguous'], 'cases_detail':outcomes}

def report(rows,max_samples=100):
 unique={}
 for r in rows:unique.setdefault((r.get('url',''),r.get('selected_place','')),r)
 vals=list(unique.values());actions=Counter(r['candidate_action'] for r in vals);trials=Counter(r['trial'] for r in vals)
 by_place=defaultdict(list)
 for r in vals:
  if r['candidate_action']!='retain':by_place[r.get('selected_place','')].append(r)
 for group in by_place.values():group.sort(key=lambda r:(r.get('candidate_action',''),r.get('title','')))
 samples=[]
 for i in range(max(map(len,by_place.values()),default=0)):
  for place in sorted(by_place):
   if i<len(by_place[place]):
    row=by_place[place][i]
    samples.append({k:row.get(k) for k in ('title','url','selected_place','publisher','trial','candidate_action','reason','d15_decision','isolation_status')})
    if len(samples)>=max_samples:break
  if len(samples)>=max_samples:break
 return {'release':'v2.4D.16','mode':'shadow_only_no_live_changes','population':'pre_deduplication_mapped_URL_location_pairs',
  'distinct_url_location_pairs':len(vals),'trial_counts':dict(trials),'candidate_action_counts':dict(actions),
  'hypothetical_candidate_loss_pairs':actions['withhold_for_review'],
  'hypothetical_candidate_relocation_pairs':actions['relocate_for_review'],
  'affected_location_count':len(by_place),'balanced_review_samples':samples,'benchmark':benchmark(),
  'safety_gates':{'automatic_corrections_enabled':False,'live_pins_changed':False,'ready_to_activate':False},
  'limitations':['Shadow candidate removal is not verified error elimination or actual globe coverage loss.',
  'The dataset includes mapped pre-deduplication URL/place pairs, not serialized globe articles.',
  'No causal before/after accuracy estimate is possible without independently labelled representative articles.',
  'The benchmark consists of curated synthetic cases; it is not a production precision estimate.',
  'International headlines and missing evidence alone must not cause automatic suppression.',
  'All proposed actions are review-only and are not applied to the live collector.']}
