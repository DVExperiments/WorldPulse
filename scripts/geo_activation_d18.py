"""D18 controlled, default-off URL/place-approved semantic correction pilot.

No broad filtering, reassignment, or publisher isolation. The only optional
live action removes explicitly approved *article entries* in eligible signals.
Requires BOTH environment switch and local review manifest authorization.
"""
import copy
import json
import os
from collections import Counter
from pathlib import Path

ENV_SWITCH='WORLDPULSE_D18_ENABLE_APPROVED_CORRECTIONS'

def _key(url, place):
    return (str(url or '').strip(), str(place or '').strip().casefold())

def load_approvals(path):
    """Missing/malformed manifest fails CLOSED rather than allowing corrections."""
    try:
        obj=json.loads(Path(path).read_text(encoding='utf8'))
        if obj.get('schema') != 1 or obj.get('enable_live_corrections') is not True:
            return set(), 'manifest_disabled_or_invalid'
        items=obj.get('approved', [])
        if not isinstance(items,list) or len(items)>20:return set(),'invalid_approval_list'
        approved=set()
        for x in items:
            if not isinstance(x,dict) or x.get('manual_article_review') is not True:
                return set(),'unreviewed_approval'
            if x.get('rule') not in ('spanish_lagos_lakes','spanish_reunion_meeting'):
                return set(),'unknown_rule'
            url=x.get('url','');place=x.get('place','')
            if not isinstance(url,str) or not url.startswith('https://') or place.casefold() not in ('lagos','réunion'):
                return set(),'invalid_approval'
            if (place.casefold()=='lagos') != (x['rule']=='spanish_lagos_lakes'):
                return set(),'rule_place_mismatch'
            approved.add(_key(url,place))
        return approved, 'manifest_enabled'
    except (OSError,ValueError,TypeError,AttributeError):
        return set(), 'manifest_missing_or_invalid'

def simulate(points, trial_rows, manifest_path, enabled=None):
    """Returns unchanged point structure when disabled, plus full impact report.

    Even enabled mode applies only for items satisfying D17 eligibility AND
    review manifest approval. Does not change non-article point geography.
    """
    if enabled is None:enabled=os.environ.get(ENV_SWITCH,'')=='1'
    approved,status=load_approvals(manifest_path)
    eligible={_key(r.get('url'),r.get('selected_place')) for r in trial_rows if r.get('eligible_for_future_pilot') and r.get('candidate_action')=='eligible_shadow_withhold'}
    matches=approved & eligible
    proposed=[]
    for p in points:
        for a in p.get('articles',[]):
            k=_key(a.get('url'),p.get('name'))
            if k in eligible:
                proposed.append({'url':a.get('url'),'place':p.get('name'),'category':p.get('category'),
                                 'title':a.get('title','')[:180],'approved':k in approved})
    active=bool(enabled and status=='manifest_enabled' and matches)
    result=copy.deepcopy(points) if active else points
    removed=[]
    if active:
        retained=[]
        for p in result:
            original=p.get('articles',[])
            # Limit changes to displayed article entries. Count is recomputed
            # proportionally only where all represented articles were serialized;
            # otherwise leave original total untouched and flag the limitation.
            keep=[]
            for a in original:
                if _key(a.get('url'),p.get('name')) in matches:
                    removed.append({'url':a['url'],'place':p['name'],'category':p.get('category')})
                else:keep.append(a)
            if len(original)==p.get('count'):
                p['count']=len(keep)
            p['articles']=keep
            if keep:retained.append(p)
            # If the entire serialized list is empty, omit group (count max 20).
        result=retained
    report={'release':'v2.4D.18','mode':'approved_live_only' if active else 'shadow_only',
      'env_switch_requested':bool(enabled),'manifest_status':status,
      'corrections_active':active,'approved_pairs':len(approved),
      'eligible_pairs':len(eligible),'approved_and_eligible_pairs':len(matches),
      'eligible_visible_entries':len(proposed),'approved_visible_entries':sum(x['approved'] for x in proposed),
      'actual_removed_entries':len(removed),'affected_group_count':len({(x['place'],x['category']) for x in proposed}),
      'projected_review_samples':proposed[:30], 'removed_records':removed,
      'notes':['No global publisher isolation or automatic relocation.',
               'Only displayed entries are filterable; historic and diagnostic counts remain pre-correction.',
               'Live mode requires BOTH explicit env switch and a manually reviewed URL/place manifest.',
               'A location/category group disappears only if all serialized articles were approved and removed.',
               'For capped groups, count and activity metrics may include withheld articles; never enable this pilot on a capped group without verifying the downstream presentation.'],
      'rollback':'Set WORLDPULSE_D18_ENABLE_APPROVED_CORRECTIONS=0 (or remove it), or set enable_live_corrections=false in data/d18-reviewed-approvals.json; run the workflow again.'}
    return result, report
