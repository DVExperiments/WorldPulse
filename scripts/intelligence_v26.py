"""v2.6 narrowly verified lexical suppressions and deduplication quality diagnostics.
No automated relocation, no publisher-region location evidence.
"""
from __future__ import annotations
import re
from collections import Counter
from urllib.parse import urlsplit,parse_qsl,urlencode,urlunsplit

def lexical_collision(place,title,description):
    name=str((place or {}).get('name','')).casefold()
    t=' '.join((title or '').split()).casefold()
    d=' '.join((description or '').split()).casefold()
    # Spanish reunión (ordinary noun for a meeting) vs the island Réunion.
    if name in {'réunion','reunion','réunion island'}:
        meeting=bool(re.search(r'\breuni[oó]n(?:es)?\b',t))
        parliamentary=bool(re.search(r'\b(interparlamentari[ao]s?|parlamentari[ao]s?|legislador(?:es|as)?|congreso|senado|diputad[oa]s?)\b',t+' '+d))
        explicit_island=bool(re.search(r'\b(isla de la reuni[oó]n|isla reuni[oó]n|reunion island|r[eé]union island|la r[eé]union,? francia)\b',t+' '+d))
        if meeting and parliamentary and not explicit_island:return 'spanish_parliamentary_meeting_not_reunion_island'
    # Spanish plural lagos in an article explicitly about Chilean lakes.
    if name in {'lagos','lagos, nigeria'}:
        lakes=bool(re.search(r'\blagos\b',t))
        chilean=bool(re.search(r'\b(chile|chilen[oa]s?|sur de chile|regi[oó]n de los lagos)\b',t+' '+d))
        environmental=bool(re.search(r'\b(lagos|lagunas|normas ambientales|contaminaci[oó]n|calidad del agua|recursos h[ií]dricos)\b',t))
        nigeria=bool(re.search(r'\b(nigeria|nigerian[oa]s?|estado de lagos|lagos state)\b',t+' '+d))
        if lakes and chilean and environmental and not nigeria:return 'spanish_chilean_lakes_not_lagos_nigeria'
    return None

def canonical(u):
    p=urlsplit(str(u or '')); q=urlencode([(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if not k.lower().startswith('utm_') and k.lower() not in ('fbclid','gclid')])
    return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip('/'),q,''))

def dedup_diagnostics(rows):
    urls={}; same_place=0;multi_place=0; examples=[]
    for a in rows:
        key=canonical(a.get('url')); place=(a.get('place') or {}).get('name','')
        if not key:continue
        if key in urls:
            if urls[key]==place:same_place+=1
            else:
                multi_place+=1
                if len(examples)<15:examples.append({'url':key,'first':urls[key],'second':place})
        else:urls[key]=place
    return {'canonical_same_place_repeats':same_place,'cross_place_url_occurrences':multi_place,'cross_place_examples':examples,'note':'Cross-location reuse is not automatically incorrect; preserve separate evidence-backed assignments.'}

def build_report(raw,points,unmapped,now,lexical_rows,history):
    counts=Counter(x['reason'] for x in lexical_rows)
    by_source=Counter((a.get('publisher') or 'Unknown') for a in raw)
    return {'schema':1,'release':'v2.6.0','updated_at':now.isoformat(),'mode':'conservative_live_lexical_withholding_plus_observation',
       'lexical_suppressed_total':len(lexical_rows),'lexical_suppressed_by_reason':dict(counts),'lexical_suppressed_examples':lexical_rows[:30],
       'deduplication_review':dedup_diagnostics(raw),'top_publisher_share_pct':round(100*max(by_source.values())/len(raw),1) if raw else 0,
       'top_publishers':[{'publisher':x,'mapped_rows':y} for x,y in by_source.most_common(15)],
       'unmapped_rows':len(unmapped),'mapped_raw_rows':len(raw),'mapped_signal_groups':len(points),
       'history_samples':len(history.get('runs',[])),'geographic_attribution':'Geographic subject, not verified incident site',
       'limitations':['Rules are narrow reviewed-language safeguards, not a universal multilingual disambiguator.',
          'No automatic replacement coordinates, inferred countries or API enrichment.',
          'Daily rolling collection fluctuations do not establish recall improvement.']}
