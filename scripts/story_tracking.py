"""WorldPulse F.2: bounded, observational coverage history for conservative similarity groups.

NOT verified events. 'Increasing' means newly observed unique publishers in sampled feeds.
"""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter

MAX_STORIES=250
RETENTION_DAYS=14
MAX_EVENTS=80

def _date(value):
    try:
        d=datetime.fromisoformat(str(value).replace('Z','+00:00'))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError,ValueError):return None

def _publisher(article):
    return str(article.get('publisher') or '').casefold().strip()

def _urls(cluster):
    return {a['url'] for a in cluster.get('articles',[]) if isinstance(a.get('url'),str) and a['url'].startswith(('http://','https://'))}

def _match(cluster,history,claimed):
    urls=_urls(cluster)
    # Require identical geography/category and a shared canonical article URL.
    # No loose headline matching: unrelated stories sharing the same topic stay separate.
    choices=[]
    for sid,prior in history.items():
        if sid in claimed or prior.get('location')!=cluster.get('location') or prior.get('category')!=cluster.get('category'):continue
        overlap=len(urls.intersection(prior.get('urls',[])))
        if overlap:choices.append((overlap,sid))
    return sorted(choices,key=lambda x:(-x[0],x[1]))[0][1] if choices else None

def enrich_story_clusters(bundle,now,history_path):
    """Enrich bundle in place, persist independent bounded source-coverage history."""
    if not isinstance(now,datetime):raise TypeError('now must be datetime')
    now=now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    path=Path(history_path)
    prior={}
    if path.exists():
        try:
            data=json.loads(path.read_text(encoding='utf8'))
            if data.get('schema')==1 and isinstance(data.get('stories'),dict):prior=data['stories']
        except (OSError,ValueError,TypeError):pass
    cutoff=now-timedelta(days=RETENTION_DAYS)
    prior={k:v for k,v in prior.items() if isinstance(v,dict) and _date(v.get('last_seen_at')) and _date(v['last_seen_at'])>=cutoff}
    claimed=set();snapshots=[];counts=Counter()
    for cluster in bundle.get('story_clusters',[]):
        oldid=_match(cluster,prior,claimed)
        matched=prior.get(oldid) if oldid else None
        sid=oldid or cluster['id']
        if matched:claimed.add(sid)
        pubs=sorted({_publisher(a) for a in cluster.get('articles',[]) if _publisher(a)})
        urls=sorted(_urls(cluster))
        previous_publishers=set(matched.get('publishers',[])) if matched else set()
        added=sorted(set(pubs)-previous_publishers)
        first_seen=matched.get('first_seen_at') if matched else now.isoformat()
        events=list(matched.get('observations',[])) if matched else []
        # One observation per collection run. Unique publisher count based on current 24h window;
        # cumulative-ever unique publishers are kept separately.
        cumulative=set(matched.get('publishers',[])) if matched else set()
        cumulative.update(pubs)
        latest_snapshot=events[-1] if events else None
        recent_growth=bool(matched and added)
        if not matched:status='newly_observed'
        elif recent_growth:status='increasing_coverage'
        else:status='ongoing_coverage'
        if latest_snapshot is None or latest_snapshot.get('at')!=now.isoformat():
            events.append({'at':now.isoformat(),'active_publishers':len(pubs),'total_seen_publishers':len(cumulative),'new_publishers':len(added)})
        events=events[-MAX_EVENTS:]
        prior[sid]={'location':cluster.get('location'),'category':cluster.get('category'),'label':cluster.get('label'),
            'first_seen_at':first_seen,'last_seen_at':now.isoformat(),'urls':sorted(set(urls).union(matched.get('urls',[]) if matched else []))[-120:],
            'publishers':sorted(cumulative),'observations':events}
        cluster['tracking_id']=sid
        cluster['coverage_status']=status
        cluster['first_observed_at']=first_seen
        cluster['new_publishers_since_previous_observation']=len(added) if matched else 0
        cluster['observed_publishers_total']=len(cumulative)
        cluster['coverage_timeline']=events[-12:]
        cluster['tracking_note']='Sampled publisher coverage only; not event severity, verified facts, or global media volume.'
        counts[status]+=1
        snapshots.append(sid)
    if len(prior)>MAX_STORIES:
        prior=dict(sorted(prior.items(),key=lambda kv:kv[1]['last_seen_at'],reverse=True)[:MAX_STORIES])
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'schema':1,'updated_at':now.isoformat(),'retention_days':RETENTION_DAYS,
        'note':'Tracks sampled multi-publisher headline groups, NOT verified canonical events.',
        'stories':prior},ensure_ascii=False,indent=1),encoding='utf8')
    bundle['story_tracking_diagnostics']={'version':'2.0F.2','observed_clusters':len(snapshots),
        'tracked_stories_retained':len(prior),'statuses':dict(counts),'history_file':'data/story-history.json',
        'note':'Increases only reflect publishers newly encountered in these sampled feeds since last successful observation.'}
    return bundle
