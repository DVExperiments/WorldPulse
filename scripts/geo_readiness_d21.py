"""D21 source-evidence dossier and production-shaped *shadow* correction readiness.
This cannot mutate, approve, or activate any production correction.
"""
import json,copy,datetime as dt
from pathlib import Path
from geo_review_d20 import pair,digest,rebuild

def evaluate(points,d20_review,evidence_path,now):
    before=digest(points)
    issues=[]
    try: document=json.loads(Path(evidence_path).read_text(encoding='utf8'))
    except (ValueError,OSError):document={};issues.append('evidence_manifest_unavailable')
    rows=document.get('reviews',[]) if isinstance(document,dict) else []
    if not isinstance(rows,list):rows=[];issues.append('reviews_not_list')
    found={};duplicates=[]
    for row in rows:
        if not isinstance(row,dict):continue
        k=pair(row.get('rss_url'),row.get('selected_place'))
        if k in found:duplicates.append(k);continue
        if (not k[0].startswith('https://') or not row.get('source_url','').startswith('https://') or
                not row.get('evidence_summary') or row.get('status')!='source_checked_pending_human_approval'):
            issues.append('invalid_evidence_row');continue
        found[k]=row
    review_queue=d20_review.get('candidate_review_queue',[])
    present=[];missing=[]
    for row in review_queue:
        k=pair(row.get('url'),row.get('place'))
        data=found.get(k)
        if data:
            present.append({'selected_place':row['place'],'title':row.get('title'),
               'rss_url':row['url'],'publisher_source_url':data['source_url'],
               'source_review_method':data['source_review_method'],
               'evidence_summary':data['evidence_summary'],
               'source_checked_pending_human_approval':True,
               'human_approved':False})
        else:missing.append({'url':row.get('url'),'place':row.get('place')})
    # Shadow removal is a readiness probe only. An AI page review never unlocks filtering.
    proposals={pair(r['rss_url'],r['selected_place']) for r in found.values() if pair(r['rss_url'],r['selected_place']) in
               {pair(x['url'],x['place']) for x in review_queue}}
    projection=rebuild(points,proposals,now)
    impacted=projection['group_impacts']
    blocked=projection['blocked_groups']
    removed=projection['projected_removed']
    count=sum(len(x.get('articles',[])) for x in points)
    after=sum(len(x.get('articles',[])) for x in projection['projected_points'])
    dependency_gates={
      'source_publisher_page_checked':bool(present) and not missing,
      'human_signed_review_complete':False,
      'uncapped_full_group_for_every_candidate':not blocked and len(removed)==len(proposals),
      'serialized_group_metrics_recomputed_in_shadow':bool(proposals) and not blocked and len(removed)==len(proposals),
      'story_cluster_rebuild_validated':False,
      'historical_metrics_rebuild_validated':False,
      'feed_attribution_reconciled':False,
      'cross_border_links_rebuilt':False,
      'production_live_filtering_enabled':False}
    return {'schema':1,'release':'v2.4D.21','mode':'source_checked_shadow_only','live_filtering_locked':True,
      'source_checked_visible_pairs':len(present),'visible_candidates_without_source_review':missing,
      'publisher_source_reviews':present,'evidence_manifest_issues':issues,
      'duplicates_ignored':len(duplicates),'human_approved_pairs':0,
      'hypothetical_proposed_pairs':len(proposals),
      'hypothetical_removed_visible_articles':len(removed),'hypothetical_before_articles':count,'hypothetical_after_articles':after,
      'hypothetical_before_groups':len(points),'hypothetical_after_groups':len(projection['projected_points']),
      'group_impacts':impacted,'blocked_groups':blocked,
      'downstream_dependency_gates':dependency_gates,
      'readiness':'NO_GO_live_corrections','reasons':['AI-assisted source review does not constitute human approval',
        'D21 projection cannot guarantee full rebuild of downstream clusters/history/cross-border links',
        'Approval and live filtering are hard-locked out of this release'],
      'baseline_sha256':before,'rollback_sha256':digest(copy.deepcopy(points)),
      'rollback_identical':before==digest(copy.deepcopy(points)),
      'input_unchanged':before==digest(points)}
