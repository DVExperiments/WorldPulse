"""D19: non-mutating correction integrity simulation and structured review validation.

No live correction API. All dry-runs operate on isolated copies and never
return corrected points for publication.
"""
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ALLOWED_RULES={'spanish_lagos_lakes':'lagos','spanish_reunion_meeting':'réunion'}
REQUIRED_REVIEW=('url','place','rule','reviewer','reviewed_at','article_access','source_evidence','location_evidence','conclusion')

def key(url,place):return (str(url or '').strip(),str(place or '').strip().casefold())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
def load_reviews(path):
    """Documented human reviews are *not* activation approvals."""
    try: payload=json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError,ValueError):return {},['review_file_missing_or_invalid']
    if not isinstance(payload,dict) or payload.get('schema')!=1 or not isinstance(payload.get('reviews'),list):
        return {},['review_schema_invalid']
    reviews={};problems=[]
    for i,row in enumerate(payload['reviews'][:200]):
        if not isinstance(row,dict) or any(not isinstance(row.get(k),str) or not row[k].strip() for k in REQUIRED_REVIEW):
            problems.append(f'review_{i}_missing_required_fields');continue
        u,p=row['url'],row['place']
        if urlsplit(u).scheme!='https' or not urlsplit(u).netloc or row['rule'] not in ALLOWED_RULES or p.casefold()!=ALLOWED_RULES[row['rule']]:
            problems.append(f'review_{i}_invalid_url_rule_or_place');continue
        if row['article_access'] not in ('full_article','rss_only','unavailable') or row['conclusion'] not in ('confirmed_false_match','valid_match','uncertain'):
            problems.append(f'review_{i}_invalid_review_state');continue
        if row['conclusion']=='confirmed_false_match' and row['article_access']!='full_article':
            problems.append(f'review_{i}_confirmation_requires_full_article');continue
        k=key(u,p)
        if k in reviews:problems.append(f'review_{i}_duplicate_pair');continue
        reviews[k]=row
    if len(payload['reviews'])>200:problems.append('review_list_over_limit')
    return reviews,problems

def _group_metrics(p,articles):
    recent=sum(1 for a in articles if a.get('_d19_bucket')=='recent')
    previous=sum(1 for a in articles if a.get('_d19_bucket')=='previous')
    return {'count':len(articles),'publisher_count':len({str(a.get('publisher','')).casefold() for a in articles}),
            'recent_3h':recent,'previous_3h':previous,'velocity_change_pct_sample':round((recent-previous)/(previous+1)*100),
            'velocity':'rising' if recent>=3 and recent>=previous+2 else ('cooling' if previous>=3 and previous>=recent+2 else 'steady')}

def simulate(points,trial_rows,review_path):
    """Assess frozen input twice. Rebuild full-group counts ONLY for uncapped groups.

    A capped group is intentionally marked unsafe: underlying articles are
    not in serialized points, so aggregate metrics cannot be reconstructed.
    """
    frozen=copy.deepcopy(points);before_hash=digest(frozen)
    reviews,problems=load_reviews(review_path)
    eligible={key(r.get('url'),r.get('selected_place')) for r in trial_rows
              if r.get('eligible_for_future_pilot') and r.get('candidate_action')=='eligible_shadow_withhold'}
    candidates=[];proposed=[];risk=[];review_states=Counter()
    for ix,p in enumerate(frozen):
        originals=p.get('articles',[])
        for a in originals:
            pair=key(a.get('url'),p.get('name'))
            if pair not in eligible:continue
            review=reviews.get(pair)
            state=review['conclusion'] if review else 'not_reviewed'
            review_states[state]+=1
            candidate={'url':a.get('url'),'place':p.get('name'),'category':p.get('category'),
                       'title':a.get('title','')[:200],'review_state':state,
                       'full_article_reviewed':bool(review and review.get('article_access')=='full_article'),
                       'simulation_only':True}
            candidates.append(candidate)
            if state=='confirmed_false_match':proposed.append((ix,pair))
    proposals=set(proposed)
    corrected=copy.deepcopy(frozen)
    removed=[];affected=[]
    for ix,p in enumerate(corrected):
        source=frozen[ix];old=source.get('articles',[])
        matches=[a for a in old if (ix,key(a.get('url'),p.get('name'))) in proposals]
        if not matches:continue
        capped=source.get('count',0)>len(old)
        kept=[a for a in old if (ix,key(a.get('url'),p.get('name'))) not in proposals]
        ident={'place':p.get('name'),'category':p.get('category'),'before_count':source.get('count'),
               'before_serialized':len(old),'after_serialized':len(kept),'capped_group':capped,
               'removed_visible_entries':len(matches)}
        if capped:
            ident['integrity']='unsafe_unserialized_articles_missing'
            risk.append(ident)
            # No full-group recomputation can safely be claimed.
            continue
        p['articles']=kept
        p['count']=len(kept)
        p['publisher_count']=len({str(a.get('publisher','')).casefold() for a in kept})
        # published_at timestamps permit exact 3h/6h reconstruction only if
        # snapshot time is supplied, not inferred from ingestion time here.
        ident['integrity']='activity_metrics_require_snapshot_time'
        risk.append(ident)
        # Diagnostic only: time-series recomputation handled by future upstream
        # integration; no publication candidate is approved from this audit.
        removed.extend({'url':a.get('url'),'place':p.get('name'),'category':p.get('category')} for a in matches)
        affected.append(ident)
    corrected=[p for p in corrected if p.get('articles')]
    rollback=copy.deepcopy(frozen)
    before_groups={(p.get('name'),p.get('category')) for p in frozen}
    after_groups={(p.get('name'),p.get('category')) for p in corrected}
    report={'release':'v2.4D.19','mode':'shadow_only_non_mutating','live_filtering_locked':True,
            'review_records_loaded':len(reviews),'review_validation_issues':problems,
            'eligible_pairs':len(eligible),'eligible_visible_entries':len(candidates),
            'visible_review_state_counts':dict(review_states),'hypothetical_confirmed_removals':len(removed),
            'unsafe_capped_groups':sum(x['capped_group'] for x in risk),
            'metrics_requiring_rebuild':len(risk),
            'before_serialized_articles':sum(len(p.get('articles',[])) for p in frozen),
            'after_hypothetical_serialized_articles':sum(len(p.get('articles',[])) for p in corrected),
            'before_groups':len(before_groups),'after_hypothetical_groups':len(after_groups),
            'groups_disappearing':sorted([{'place':k[0],'category':k[1]} for k in before_groups-after_groups],key=lambda x:(x['place'],x['category'])),
            'before_snapshot_sha256':before_hash,'rollback_sha256':digest(rollback),
            'rollback_identical':digest(rollback)==before_hash,
            'caller_input_unchanged':digest(points)==before_hash,
            'proposed_group_impacts':risk[:80],'review_queue':candidates[:80],
            'note':'Hypothetical deletions are never published. Full article review and an upstream metrics rebuild are required before live activation. Capped groups are not simulated as safely deletable.'}
    return report
