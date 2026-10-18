"""WorldPulse E.3 evidence classes; advisory only, NOT event-location verification."""
from collections import Counter
from pathlib import Path
import json
from geo_accuracy_audit import mentioned_places, reviewed_catalogue

CATALOGUE = reviewed_catalogue()

def classify(article):
    method=str(article.get('geo_match') or 'unknown')
    place=(article.get('place') or {}).get('name') or 'Unknown'
    title=mentioned_places(article.get('title',''),CATALOGUE)
    desc=mentioned_places(article.get('description',''),CATALOGUE)
    # "no catalogue match" is an audit-coverage limitation, NOT a quality warning.
    if len(title)>1:
        kind='ambiguous_headline'; note='multiple_reviewed_headline_subjects'
    elif method=='headline-reviewed-correction':
        kind='explicit_headline'; note='corrected_from_description_to_headline'
    elif method.startswith('headline') or method in ('normalized-headline','headline-normalized','headline-expanded'):
        kind='explicit_headline'; note='headline_matching_method'
    elif method.startswith('description'):
        if len(title)==1 and title[0]!=place:
            kind='conflicting_evidence'; note='distinct_reviewed_headline_place'
        else:
            kind='description_context'; note='description_matching_method'
    elif method=='url-explicit-place' or method.startswith('url'):
        kind='url_context';note='url_based_match_not_article_body'
    elif len(title)==1 and title[0]==place:
        kind='explicit_headline';note='reviewed_headline_agrees'
    elif len(desc)==1 and desc[0]==place:
        kind='description_context';note='reviewed_description_agrees'
    else:
        kind='other_heuristic';note='matcher_evidence_not_independently_resolved'
    return {'evidence_class':kind,'evidence_reason':note,'assigned_place':place,
            'match_method':method,'reviewed_headline_places':title[:8],
            'reviewed_description_places':desc[:8],
            'event_location_verified':False}

def build(rows,now):
    classes=Counter();methods=Counter();examples=[];limited=0
    for article in rows:
        record=classify(article)
        classes[record['evidence_class']]+=1
        methods[record['match_method']]+=1
        if not record['reviewed_headline_places'] and not record['reviewed_description_places']:
            limited+=1
        if record['evidence_class'] in ('ambiguous_headline','conflicting_evidence','url_context') and len(examples)<45:
            examples.append({'title':str(article.get('title',''))[:180], 'publisher':str(article.get('publisher',''))[:90],
                             'url':str(article.get('url',''))[:300],**record})
    return {'schema':1,'version':'2.0E.3','generated_at':now.isoformat(),
      'scope':'mapped eligible feed occurrences before deduplication',
      'mapped_occurrences_audited':len(rows),'evidence_classes':dict(classes),
      'matching_methods':dict(methods),'not_found_in_limited_review_catalogue':limited,
      'review_examples':examples,
      'notes':['Evidence classes are descriptive, not calibrated confidence scores.',
               'No catalogue match is not a warning and is never counted as an error.',
               'Geographic subject is not a verified event or incident coordinate.',
               'Source URL, publisher, and feed edition are not accepted as incident-location verification.'],
      'policy':'Diagnostic only. No placements or existing matching decisions changed.'}

def publish_confidence(rows,now,folder):
    path=Path(folder)/'unmatched-review.json'
    if not path.is_file():raise RuntimeError('Missing unmatched-review.json; E.3 cannot embed evidence report')
    report=build(rows,now)
    data=json.loads(path.read_text(encoding='utf8'))
    data['geo_confidence_evidence']=report
    path.write_text(json.dumps(data,ensure_ascii=False,indent=1),encoding='utf8')
    print('WorldPulse E.3 geographic evidence report published',flush=True)
    return report
