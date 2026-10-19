"""D19.1 bounded Google RSS retries and conservative snapshot protection."""
from __future__ import annotations
import datetime as dt
import random
import time
import urllib.error

TRANSIENT_HTTP={429,500,502,503,504}

def retry_open(request, opener, *, timeout=30, retries=2, sleep=time.sleep, random_value=random.random):
    """Retry only transient HTTP/transport errors; maximum three total requests."""
    for attempt in range(retries+1):
        try:
            return opener(request,timeout=timeout)
        except urllib.error.HTTPError as exc:
            if exc.code not in TRANSIENT_HTTP or attempt == retries: raise
            retry_after=exc.headers.get('Retry-After') if exc.headers else None
            try: pause=min(8.0,max(0.0,float(retry_after))) if retry_after else 0
            except (ValueError,TypeError): pause=0
        except (urllib.error.URLError,TimeoutError,ConnectionError):
            if attempt == retries: raise
            pause=0
        sleep(max(pause,min(4.0,0.5*(2**attempt))+0.5*random_value()))

def assess_outage(health, old, *, now=None):
    """Conservative protection only for catastrophic aggregator outages with a healthy recent snapshot.
    Independent publisher failures alone never trip this gate.
    """
    now=now or dt.datetime.now(dt.timezone.utc)
    google=[h for h in health if h.get('kind')=='aggregator']
    google_failed=sum(h.get('status')=='failed' for h in google)
    google_ok=len(google)-google_failed
    prior_points=old.get('points',[]) if isinstance(old,dict) else []
    prior_articles=sum(len(p.get('articles',[])) for p in prior_points if isinstance(p,dict))
    prior_stamp=old.get('updated_at','') if isinstance(old,dict) else ''
    try:
        timestamp=dt.datetime.fromisoformat(prior_stamp.replace('Z','+00:00'))
        if timestamp.tzinfo is None: timestamp=timestamp.replace(tzinfo=dt.timezone.utc)
        age_hours=(now-timestamp).total_seconds()/3600
    except (ValueError,TypeError,AttributeError): age_hours=None
    previous_healthy=(prior_articles>=350 and age_hours is not None and 0<=age_hours<=30 and old.get('status') in ('live','partial'))
    google_outage=len(google)>=20 and google_failed/len(google)>=0.8 and google_ok<=max(5,int(len(google)*.1))
    block=bool(previous_healthy and google_outage)
    return {'schema':1,'version':'v2.4D.19.1','checked_at':now.isoformat(),
       'google_feeds':len(google),'google_failed':google_failed,'google_ok':google_ok,
       'previous_serialized_articles':prior_articles,'previous_snapshot_age_hours':round(age_hours,2) if age_hours is not None else None,
       'previous_snapshot_healthy':bool(previous_healthy),'major_google_outage':bool(google_outage),
       'publication_blocked':block,'reason':'catastrophic_aggregator_failure_preserved_previous_news' if block else 'publish_as_normal',
       'note':'Snapshot health uses serialized article count as a conservative proxy. An old snapshot is not preserved forever; age limit is 30 hours.'}
