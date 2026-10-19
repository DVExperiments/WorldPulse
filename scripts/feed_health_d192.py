"""D19.2: deterministic source-outage drills and transport-vs-empty reporting.
Observational only: real publication protection remains in D19.1 assess_outage.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
from collections import Counter
from feed_resilience_d191 import assess_outage

VERSION = 'v2.4D.19.2'

def canonical_fingerprint(snapshot):
    return hashlib.sha256(json.dumps(snapshot,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()

def classify_feed(row):
    status = str(row.get('status','')).lower()
    if status == 'failed': return 'transport_failure'
    if status != 'ok': return 'unknown_status'
    count = row.get('items')
    if isinstance(count,bool) or not isinstance(count,int) or count < 0: return 'unknown_item_count'
    return 'successful_empty' if count == 0 else 'successful_nonempty'

def feed_breakdown(health):
    out={}
    for kind in ('aggregator','publisher'):
        rows=[r for r in health if r.get('kind')==kind]
        counts=Counter(classify_feed(row) for row in rows)
        out[kind]={'total':len(rows),**{name:counts[name] for name in ('successful_nonempty','successful_empty','transport_failure','unknown_item_count','unknown_status')},
          'empty_samples':[r.get('source','') for r in rows if classify_feed(r)=='successful_empty'][:15],
          'failure_samples':[{'source':r.get('source',''),'error':r.get('error','')} for r in rows if classify_feed(r)=='transport_failure'][:15]}
    return out

def run_frozen_drills(*, now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    prior={'status':'live','updated_at':(now-dt.timedelta(hours=1)).isoformat(),
           'points':[{'name':'test','articles':[{'url':f'https://example.org/{i}/{j}'} for j in range(20)]} for i in range(30)]}
    before=canonical_fingerprint(prior)
    scenarios={
      'catastrophic_google_503': ([{'kind':'aggregator','status':'failed','items':0} for _ in range(121)]+[{'kind':'publisher','status':'ok','items':5} for _ in range(49)],True),
      'partial_google_outage': ([{'kind':'aggregator','status':'failed','items':0} for _ in range(30)]+[{'kind':'aggregator','status':'ok','items':5} for _ in range(91)],False),
      'successful_but_empty_google': ([{'kind':'aggregator','status':'ok','items':0} for _ in range(121)],False),
      'healthy_google': ([{'kind':'aggregator','status':'ok','items':5} for _ in range(121)],False),
    }
    results=[]
    for name,(health,expected) in scenarios.items():
        result=assess_outage(health,prior,now=now)
        # Publication simulation does not mutate the frozen snapshot.
        after=canonical_fingerprint(prior)
        results.append({'scenario':name,'expected_publication_blocked':expected,
          'actual_publication_blocked':result['publication_blocked'],
          'passed':result['publication_blocked'] is expected and before==after,
          'old_snapshot_preserved':before==after,
          'google_failed':result['google_failed'],
          'google_successful_empty':sum(classify_feed(h)=='successful_empty' for h in health if h['kind']=='aggregator')})
    stale=dict(prior,updated_at=(now-dt.timedelta(hours=40)).isoformat())
    result=assess_outage(scenarios['catastrophic_google_503'][0],stale,now=now)
    results.append({'scenario':'expired_snapshot_not_preserved','expected_publication_blocked':False,
      'actual_publication_blocked':result['publication_blocked'],'passed':result['publication_blocked'] is False,
      'old_snapshot_preserved':True,'google_failed':result['google_failed'],'google_successful_empty':0})
    return {'passed':all(r['passed'] for r in results),'scenarios':results,'frozen_snapshot_fingerprint':before,
      'note':'Synthetic in-memory scenarios confirm gate decisions and snapshot immutability; they do not simulate network fetches, GitHub commits, or guarantee future source availability.'}

def build_report(health,old,*,now=None,actual_d191=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    actual_d191=actual_d191 or assess_outage(health,old,now=now)
    return {'schema':1,'release':VERSION,'updated_at':now.isoformat(),'mode':'observation_and_offline_drills',
      'feed_outcomes':feed_breakdown(health),
      'actual_publication_decision':{'blocked':bool(actual_d191.get('publication_blocked')),'reason':actual_d191.get('reason'),
          'previous_snapshot_healthy':actual_d191.get('previous_snapshot_healthy')},
      'frozen_outage_drills':run_frozen_drills(now=now),
      'limits':['A successful HTTP response with zero parsed items is not a transport failure; it can still represent an upstream empty or malformed response.',
                'No automatic publication block is introduced for successful empty feeds.',
                'Drills exercise the D19.1 decision helper with synthetic feed statuses, not real HTTP requests.',
                'Geographic corrections remain disabled.']}
