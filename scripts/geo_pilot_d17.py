"""D17 opt-in-ready *shadow-only* semantic pilot; does not change live pins.

The flag is audit metadata, not an enabled suppression path. Strict eligibility
requires language evidence, absence of independently supported selected-place
mentions and no competing positive evidence in cleaned descriptions.
"""
from collections import Counter, defaultdict
import re
import unicodedata

PILOT_ENABLED = False  # intentional safety lock; changing this alone does not alter collector

def normal(text):
    return unicodedata.normalize('NFKC', text or '').casefold()

# Contextual, narrowly scoped lexical collisions, rather than global blocklists.
COLLISIONS = {
    'lagos': ('es', r'\b(?:los\s+lagos|lagos\s+(?:de|del|en|chilenos|andinos|naturales))\b', 'Spanish lakes'),
    'réunion': ('es', r'\breuni[oó]n(?:es)?\b', 'Spanish meeting'),
}
# Explicit positive evidence: do not suggest withholding if the selected place is
# plausibly used geographically anywhere in the cleaned article snippet.
POSITIVE = {
    'lagos': r'\b(?:lagos\s*,?\s*nigeria|lagos\s+(?:state|city|metropolis)|in\s+lagos|en\s+lagos\s*,?\s*nigeria)\b',
    'réunion': r'\b(?:r[eé]union\s+(?:island|territory)|[iî]le\s+de\s+la\s+r[eé]union|island\s+of\s+r[eé]union|en\s+la\s+r[eé]union)\b',
}

def trial(title, place, clean_description, language, d16_action, d15_decision):
    key = normal(place); source = normal(title); clean = normal(clean_description)
    baseline = {'candidate_action':'retain_unchanged','eligible_for_future_pilot':False,
                'reason':'no strict semantic-collision evidence','safety':'shadow_only'}
    if key not in COLLISIONS: return baseline
    lang, pattern, meaning = COLLISIONS[key]
    if not (language or '').casefold().startswith(lang):
        return {**baseline,'reason':'feed language does not confirm required collision language'}
    if not re.search(pattern, source, re.I):return baseline
    if re.search(POSITIVE[key], source+' '+clean, re.I):
        return {**baseline,'reason':'independent selected-place geographic context protects assignment'}
    if d15_decision in ('hierarchy_consistent','retained_independent_evidence'):
        return {**baseline,'reason':'existing independent evidence protects assignment'}
    if d16_action not in ('withhold_for_review','relocate_for_review'):
        return {**baseline,'reason':'D16 did not identify a review-only correction'}
    return {'candidate_action':'eligible_shadow_withhold','eligible_for_future_pilot':True,
            'reason':meaning+' in headline; no positive place context in available RSS excerpt',
            'safety':'shadow_only_unverified_article_body'}

def benchmark():
    cases = [
      ('Los lagos del sur de Chile','Lagos','', 'es','withhold_for_review','language_collision_review',True),
      ('Reunión del parlamento en Madrid','Réunion','', 'es','withhold_for_review','language_collision_review',True),
      ('Los lagos del sur de Chile','Lagos','Flooding in Lagos, Nigeria','es','withhold_for_review','language_collision_review',False),
      ('Flooding in Lagos, Nigeria','Lagos','','en','retain','retained_independent_evidence',False),
      ('Reunión del parlamento en Madrid','Réunion','On Réunion island','es','withhold_for_review','language_collision_review',False),
      ('Reunión del parlamento en Madrid','Réunion','','en','withhold_for_review','language_collision_review',False),
      ('Reunión del parlamento en Madrid','Réunion','','es','retain','language_collision_review',False),
      ('Reunión del parlamento en Madrid','Réunion','','es','withhold_for_review','hierarchy_consistent',False),
      ('Los lagos del sur de Chile','Lagos','','es','withhold_for_review','language_collision_review',True),
    ]
    results=[trial(*row[:6])['eligible_for_future_pilot']==row[6] for row in cases]
    return {'kind':'curated_synthetic_regression_not_independent_validation','total':len(cases),'passed':sum(results),'failed':len(cases)-sum(results)}

def report(rows, points, max_samples=60):
    unique={}
    for row in rows:unique.setdefault((row.get('url'),row.get('selected_place')),row)
    vals=list(unique.values()); eligible=[r for r in vals if r.get('eligible_for_future_pilot')]
    url_places={(r['url'],normal(r['selected_place'])) for r in eligible}
    visible=[]
    for point in points:
        for a in point.get('articles',[]):
            if (a.get('url'),normal(point.get('name'))) in url_places:
                visible.append({'url':a['url'],'place':point['name'],'category':point.get('category'),'title':a.get('title','')[:180]})
    grouped=defaultdict(list)
    for r in eligible:grouped[r.get('selected_place','')].append(r)
    balanced=[]
    for i in range(max((len(g) for g in grouped.values()), default=0)):
        for p in sorted(grouped):
            if i<len(grouped[p]):
                r=grouped[p][i];balanced.append({k:r.get(k) for k in ('url','title','selected_place','publisher','language','reason','clean_description_excerpt')})
            if len(balanced)>=max_samples:break
        if len(balanced)>=max_samples:break
    return {'release':'v2.4D.17','mode':'shadow_only','flag_enabled':PILOT_ENABLED,'automatic_correction_enabled':False,
      'unique_url_location_pairs':len(vals), 'strict_eligible_pairs':len(eligible),
      'strict_eligible_visible_article_entries':len(visible),
      'visible_signal_groups_affected':len({(r['place'],r['category']) for r in visible}),
      'visible_samples':visible[:25], 'balanced_review_samples':balanced,
      'by_selected_place':dict(Counter(r['selected_place'] for r in eligible)),
      'benchmark':benchmark(),
      'rollback':'No live edit was made. Remove D17 imports/audit calls or set the audit flag false to stop reporting.',
      'activation_gates':{'live_correction_enabled':False,'requires_independent_manual_article_review':True,
           'requires_false_positive_coverage_audit':True,'requires_explicit_user_authorization':True},
      'limitations':['An RSS excerpt is not a complete article, so eligible does not mean confirmed erroneous.',
         'Feature flag is a non-operational safety lock; no automatic suppression code is connected.',
         'Visible entry counts are exact URL/location matches against the serialized 20-article-per-signal list, not whole globe pins.',
         'Synthetic regression examples are not a measured real-world precision estimate.']}
