"""WorldPulse v2.5: read-only comparative intelligence & quality reporting.
No live filtering, inferred event sites, external calls, or history writes.
"""
from __future__ import annotations
import copy, datetime as dt, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit


def fingerprint(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',',':')).encode()).hexdigest()


def canonical_url(url):
    u=urlsplit(str(url or ''))
    if u.scheme not in ('http','https') or not u.netloc:return ''
    drops={'utm_source','utm_medium','utm_campaign','utm_term','utm_content','fbclid','gclid'}
    query=urlencode([(k,v) for k,v in parse_qsl(u.query,keep_blank_values=True) if k.lower() not in drops])
    return urlunsplit((u.scheme.lower(),u.netloc.lower(),u.path.rstrip('/') or '/',query,''))


def quality_report(raw,points,feeds,unmapped,d21,now):
    """Observational metrics, not factual global-event distribution."""
    baseline=fingerprint(points)
    feed_rows=list(feeds.values()) if isinstance(feeds,dict) else list(feeds)
    source_stats=defaultdict(lambda:{'rows':0,'locations':set(),'examples':[]})
    geo_buckets=Counter(); pub_by_place=defaultdict(Counter)
    for a in raw:
        p=a.get('place') or {}; pub=(a.get('publisher') or 'Unknown').strip()
        if p.get('name'):
            name=p['name']; pub_by_place[name][pub]+=1
            s=source_stats[pub];s['rows']+=1;s['locations'].add(name)
            if len(s['examples'])<2:s['examples'].append(name)
        geo_buckets[a.get('geo_match','unknown')]+=1
    hotspots=[]
    for name,pubs in pub_by_place.items():
        total=sum(pubs.values()); top,pop=pubs.most_common(1)[0]
        if total>=8:hotspots.append({'location':name,'matched_rows':total,'leading_publisher':top,'leading_rows':pop,'publisher_concentration_pct':round(100*pop/total,1),'distinct_publishers':len(pubs)})
    hotspots.sort(key=lambda x:(-x['publisher_concentration_pct'],-x['matched_rows'],x['location']))
    top_sources=sorted(({'publisher':k,'matched_rows':v['rows'],'mapped_locations':len(v['locations'])} for k,v in source_stats.items()),key=lambda r:-r['matched_rows'])[:25]
    # Event proximity is exploratory ONLY; shared URL is not proof of a common event.
    cross=defaultdict(set); url_locations=defaultdict(set)
    for p in points:
        for a in p.get('articles',[]):
            key=canonical_url(a.get('url'))
            if key:
                cross[key].add((p.get('name'),p.get('category')))
                url_locations[key].add(p.get('name'))
    repeated=[{'url':url,'location_count':len(loc),'locations':sorted(loc)[:8]} for url,loc in url_locations.items() if len(loc)>1]
    repeated.sort(key=lambda x:(-x['location_count'],x['url']))
    failures=Counter(f.get('kind','unknown') for f in feed_rows if f.get('status')=='failed')
    empty=Counter(f.get('kind','unknown') for f in feed_rows if f.get('status')=='ok' and not f.get('parsed_entries'))
    result={'schema':1,'release':'v2.5.0','generated_at':now.isoformat(),'mode':'observational_non_mutating',
      'source_rows':len(raw),'displayed_articles':sum(len(p.get('articles',[])) for p in points),
      'signal_groups':len(points),'mapped_location_names':len({p.get('name') for p in points}),
      'feeds_total':len(feed_rows),'feeds_failed_by_kind':dict(failures),'feeds_successful_empty_by_kind':dict(empty),
      'geo_match_basis':dict(geo_buckets),'unmapped_sample_rows':len(unmapped),
      'publisher_concentration_hotspots':hotspots[:30], 'top_mapped_publishers':top_sources,
      'same_url_multiple_locations_samples':repeated[:25],
      'source_checked_visible_pairs':d21.get('source_checked_visible_pairs',0),
      'shadow_proposed_removals':d21.get('hypothetical_removed_visible_articles',0),
      'recommendations':['Publisher concentration is a sampling warning, not proof of an incorrect mapping',
                         'Shared URLs at several locations are review candidates, not automatically duplicates',
                         'RSS edition region is never treated as event-location evidence',
                         'No API dependencies or increased feed requests introduced'],
      'baseline_unchanged':fingerprint(points)==baseline,
      'limits':['Mapped location refers to geographic subject, not verified event site',
                'Concentration counts are pre-dedup raw mapped feed entries and can include repetitions',
                'One event may span multiple places; this report does not discard cross-location URLs']}
    return result


def shadow_consistency(points,d21,now,cluster_fn=None,links_fn=None):
    """Simulate derived outputs from corrected points without publishing or mutating history.
    Uses same pure builders as the live record where supplied. Never runs history-writing enrichment.
    """
    from geo_review_d20 import rebuild,pair
    original=fingerprint(points)
    pairs={pair(row.get('rss_url'),row.get('selected_place')) for row in d21.get('publisher_source_reviews',[])
           if row.get('source_checked_pending_human_approval') and not row.get('human_approved')}
    shadow=rebuild(points,pairs,now); projected=shadow['projected_points']
    checks={'input_unchanged':fingerprint(points)==original,
            'baseline_rollback_same':fingerprint(copy.deepcopy(points))==original,
            'article_delta_conserved':(sum(len(x.get('articles',[])) for x in points)-sum(len(x.get('articles',[])) for x in projected))==len(shadow['projected_removed']),
            'no_empty_projected_groups':all(p.get('articles') for p in projected),
            'no_incomplete_groups_modified':all(x.get('decision')=='blocked_incomplete_full_group' for x in shadow['blocked_groups'])}
    dependent={}
    for name,fn in [('story_cluster_builder',cluster_fn),('cross_border_builder',links_fn)]:
        if fn is None:dependent[name]={'status':'not_available'};continue
        try:
            before=fn(copy.deepcopy(points));after=fn(copy.deepcopy(projected))
            dependent[name]={'status':'shadow_rebuilt','before_sha256':fingerprint(before),'after_sha256':fingerprint(after),'changed':fingerprint(before)!=fingerprint(after)}
        except Exception as exc:
            dependent[name]={'status':'blocked_builder_error','error_type':type(exc).__name__}
    downstream_ok=all(v['status']=='shadow_rebuilt' for v in dependent.values())
    return {'schema':1,'release':'v2.5.0','mode':'full_snapshot_shadow_no_live_writes',
      'live_filtering_locked':True,'source_review_is_not_approval':True,
      'baseline_sha256':original,'rollback_sha256':fingerprint(copy.deepcopy(points)),
      'proposed_pairs':len(pairs),'projected_removed':len(shadow['projected_removed']),
      'blocked_group_count':len(shadow['blocked_groups']),
      'group_impacts':shadow['group_impacts'][:30], 'derived_builders':dependent,
      'checks':checks,'passed':all(checks.values()) and downstream_ok,
      'readiness':'NO_GO_live_corrections',
      'remaining_gates':['human_review_approval','feed_attribution_from_precorrection_rows',
         'persistent_history_rebuild','story_history_enrichment_rebuild',
         'full_end_to_end_build_under_a_clean_repository_checkout'],
      'limits':['Derived cluster and cross-border structures are computed in memory, never published',
                'Clustering history enrichment is intentionally excluded to avoid modifying persistent history',
                'Unapproved evidence is used only for comparison, never live removal']}


def validate_snapshot(news,audit,quality):
    points=news.get('points',[])
    serialized=sum(len(p.get('articles',[])) for p in points)
    mismatches=[]
    for n,p in enumerate(points):
        count=p.get('count',0);visible=len(p.get('articles',[]))
        if not isinstance(count,int) or count<visible or visible>20:
            mismatches.append({'index':n,'name':p.get('name'),'count':count,'serialized':visible})
    if serialized!=audit.get('totals',{}).get('globe_articles'):
        mismatches.append({'issue':'audit_serialized_total_mismatch','actual':serialized,'audited':audit.get('totals',{}).get('globe_articles')})
    return {'schema':1,'release':'v2.5.0','ok':not mismatches,'serialized_articles':serialized,
            'signal_groups':len(points),'violations':mismatches[:30],
            'read_only':True,'publication_gate_enabled':False,
            'note':'Validation is observational; never deletes or blocks a live snapshot.'}
