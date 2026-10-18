"""E.4 public, conservative explanation of geographic SUBJECT matching (not verified events)."""
from geo_confidence import classify

LABELS={
 'explicit_headline':('Headline evidence','The headline supports the location assignment.'),
 'description_context':('Description evidence','The feed description was used to associate this story with a location.'),
 'conflicting_evidence':('Conflicting place mentions','The location evidence may conflict; interpret this assignment cautiously.'),
 'ambiguous_headline':('Multiple places mentioned','The headline names multiple reviewed places; this map association is not necessarily an incident site.'),
 'url_context':('URL-based context','The match relies on geographic information in a URL, not verified reporting of an incident site.'),
 'other_heuristic':('Heuristic association','The collector matched geographic text but could not assign a clearer evidence category.')}

def public_evidence(article):
    result=classify(article)
    kind=result['evidence_class']
    label,explanation=LABELS.get(kind,LABELS['other_heuristic'])
    return {'evidence_class':kind,'evidence_label':label,'evidence_explanation':explanation,
            'location_role':'geographic_subject','event_location_verified':False,
            'location_precision':str((article.get('place') or {}).get('level') or 'place'),
            'geo_match_method':str(article.get('geo_match') or 'unknown')}
