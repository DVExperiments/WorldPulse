"""D20: independently reviewed geographic correction pilot, NO live mutations.

An audit candidate is NOT a verified error. Source evidence must be provided by
an actual reviewer. A synthetic removal drill is separately labeled and cannot
populate the real review queue or approvals.
"""
import copy, datetime as dt, hashlib, json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

RULES={'spanish_lagos_lakes':'lagos','spanish_reunion_meeting':'réunion'}

def canonical(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def pair(url,place):return (str(url or '').strip(),str(place or '').casefold().strip())
def valid_time(s):
    try:
        x=dt.datetime.fromisoformat(s.replace('Z','+00:00'))
        return x if x.tzinfo else None
    except (ValueError,AttributeError):return None

def validate_review(row):
    if not isinstance(row,dict):return 'not_object'
    required=('url','place','rule','reviewer','reviewed_at','article_access','source_evidence','location_evidence','conclusion','source_url','source_title')
    if any(not isinstance(row.get(k),str) or not row[k].strip() for k in required):return 'missing_review_provenance'
    if row['rule'] not in RULES or row['place'].casefold()!=RULES[row['rule']]:return 'incorrect_rule_place'
    for field in ('url','source_url'):
        u=urlsplit(row[field]);
        if u.scheme!='https' or not u.netloc:return 'invalid_https_url'
    if not valid_time(row['reviewed_at']):return 'invalid_review_date'
    if row['article_access'] not in ('full_article','rss_only','unavailable'):return 'invalid_access'
    if row['conclusion'] not in ('confirmed_false_match','valid_match','uncertain'):return 'invalid_conclusion'
    if row['conclusion']=='confirmed_false_match':
        if row['article_access']!='full_article':return 'full_article_required'
        if len(row['source_evidence'].strip())<35 or len(row['location_evidence'].strip())<35:return 'insufficient_documented_evidence'
        if not row.get('independent_geography_check',False):return 'independent_check_required'
    return None

def load_reviews(path):
    try: doc=json.loads(Path(path).read_text(encoding='utf8'))
    except (OSError,ValueError):return {},['review_file_missing_or_invalid']
    if not isinstance(doc,dict) or doc.get('schema')!=1 or not isinstance(doc.get('reviews'),list):return {},['invalid_review_schema']
    found={};issues=[]
    for n,row in enumerate(doc['reviews'][:200]):
        err=validate_review(row)
        if err:issues.append({'index':n,'error':err});continue
        k=pair(row['url'],row['place'])
        if k in found:issues.append({'index':n,'error':'duplicate_review'});continue
        found[k]=row
    if len(doc['reviews'])>200:issues.append({'error':'review_limit_exceeded'})
    return found,issues

def rebuild(points,remove_pairs,now):
    """Frozen shadow projection; refuse capped groups: hidden articles unknown."""
    original=copy.deepcopy(points); result=copy.deepcopy(points); proposed=[]; risks=[]; removals=[]
    for i,point in enumerate(result):
        before=original[i]; entries=before.get('articles',[])
        hits=[a for a in entries if pair(a.get('url'),before.get('name')) in remove_pairs]
        if not hits:continue
        capped=before.get('count',0)!=len(entries)
        entry={'place':before.get('name'),'category':before.get('category'),'before_count':before.get('count'),
               'visible_before':len(entries),'proposed_remove':len(hits),'capped_or_inconsistent':capped}
        if capped:
            entry['decision']='blocked_incomplete_full_group';risks.append(entry);continue
        kept=[a for a in entries if pair(a.get('url'),before.get('name')) not in remove_pairs]
        rec=prev=0;bad_times=0
        for a in kept:
            t=valid_time(a.get('published_at',''))
            if t is None:bad_times+=1;continue
            age=(now-t).total_seconds()
            if age<3*3600:rec+=1
            elif age<6*3600:prev+=1
        if bad_times:
            entry['decision']='blocked_invalid_article_timestamps';entry['invalid_timestamps']=bad_times
            risks.append(entry);continue
        point['articles']=kept;point['count']=len(kept)
        point['publisher_count']=len({str(a.get('publisher','')).casefold() for a in kept})
        point['recent_3h']=rec;point['previous_3h']=prev
        point['velocity_change_pct_sample']=round((rec-prev)/(prev+1)*100)
        point['velocity']='rising' if rec>=3 and rec>=prev+2 else ('cooling' if prev>=3 and prev>=rec+2 else 'steady')
        entry.update(decision='simulated_rebuilt',after_count=len(kept),after_publisher_count=point['publisher_count'],after_recent_3h=rec,after_previous_3h=prev)
        proposed.append(entry)
        removals.extend({'url':a.get('url'),'place':before.get('name'),'category':before.get('category')} for a in hits)
    result=[p for p in result if p.get('articles')]
    # Do not claim that this reconstructs source feed stats, historical metrics, or
    # any derived clusters; only serialize-local counts are projected.
    return {'projected_points':result,'group_impacts':proposed,'blocked_groups':risks,'projected_removed':removals}

def fixture_drill(now):
    stamp=(now-dt.timedelta(hours=1)).isoformat()
    def a(url,pub):return {'url':'https://example.test/'+url,'title':url,'publisher':pub,'published_at':stamp}
    groups=[{'name':'Lagos','category':'environment','count':2,'publisher_count':2,'recent_3h':2,'previous_3h':0,'velocity':'steady','velocity_change_pct_sample':200,
             'articles':[a('bad','A'),a('valid','B')]},
            {'name':'Réunion','category':'politics','count':21,'publisher_count':1,'articles':[a('r'+str(i),'P') for i in range(20)]},
            {'name':'Lagos','category':'society','count':1,'publisher_count':1,'articles':[a('only','C')]}]
    before=digest(groups);target={pair('https://example.test/bad','Lagos'),pair('https://example.test/r0','Réunion'),pair('https://example.test/only','Lagos')}
    sim=rebuild(groups,target,now);end=sim['projected_points']
    checks={'input_immutable':digest(groups)==before,
       'recomputed_uncapped_group':end[0]['count']==1 and end[0]['publisher_count']==1 and end[0]['recent_3h']==1,
       'capped_group_blocked':len(sim['blocked_groups'])==1 and end[1]['count']==21,
       'empty_group_removed':len(end)==2,
       'exact_removed_entries':len(sim['projected_removed'])==2,
       'rollback_identity':digest(copy.deepcopy(groups))==before}
    return {'kind':'synthetic_fixture_not_verified_articles','passed':all(checks.values()),'checks':checks,
            'fixture_removed':len(sim['projected_removed']),'fixture_blocked_capped_groups':len(sim['blocked_groups'])}

def evaluate(points,trial_rows,review_path,now):
    before=digest(points);reviews,issues=load_reviews(review_path)
    eligible={pair(r.get('url'),r.get('selected_place')) for r in trial_rows if r.get('eligible_for_future_pilot') and r.get('candidate_action')=='eligible_shadow_withhold'}
    queue=[];approved=set();counts=Counter()
    for p in points:
        for a in p.get('articles',[]):
            k=pair(a.get('url'),p.get('name'))
            if k not in eligible:continue
            r=reviews.get(k);status=r['conclusion'] if r else 'not_reviewed';counts[status]+=1
            queue.append({'url':a.get('url'),'title':a.get('title','')[:240],'place':p.get('name'),'category':p.get('category'), 'review_state':status,
                          'full_article_reviewed':bool(r and r['article_access']=='full_article')})
            if r and status=='confirmed_false_match':approved.add(k)
    shadow=rebuild(points,approved,now)
    return {'schema':1,'release':'v2.4D.20','mode':'shadow_only_no_live_writes','live_filtering_locked':True,
     'review_records_valid':len(reviews),'review_validation_issues':issues,'eligible_candidate_pairs':len(eligible),
     'candidate_visible_entries':len(queue),'review_state_counts':dict(counts),
     'confirmed_reviewed_visible_pairs':len(approved),'hypothetical_removed_visible_articles':len(shadow['projected_removed']),
     'hypothetical_before_visible_articles':sum(len(p.get('articles',[])) for p in points),
     'hypothetical_after_visible_articles':sum(len(p.get('articles',[])) for p in shadow['projected_points']),
     'hypothetical_before_signal_groups':len(points),'hypothetical_after_signal_groups':len(shadow['projected_points']),
     'projection_group_impacts':shadow['group_impacts'][:60],'blocked_group_impacts':shadow['blocked_groups'][:60],
     'candidate_review_queue':queue[:60],'baseline_sha256':before,'rollback_sha256':digest(copy.deepcopy(points)),
     'rollback_identical':digest(copy.deepcopy(points))==before,'caller_input_unchanged':digest(points)==before,
     'frozen_nonzero_removal_drill':fixture_drill(now),
     'limits':['Article review provenance is user-supplied, not authenticated or independently verified by the collector.',
               'Uncapped serialized groups can rebuild their local metrics; capped groups remain blocked.',
               'Projected changes do not rebuild cross-border links, story clusters, feed attribution or persisted history.',
               'No candidate is remapped automatically; live correction remains locked off.']}
