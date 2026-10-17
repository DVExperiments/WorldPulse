"""WorldPulse official event adapter: USGS 24-hour earthquake GeoJSON.
Events are observations, never counted as news articles. Standard library only.
"""
import datetime as dt
import json
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'data/events.json'
ENDPOINT='https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'

def convert(payload, now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    cutoff=now-dt.timedelta(hours=24)
    seen=set(); events=[]
    for feature in payload.get('features',[]):
        properties=feature.get('properties') or {}
        geometry=feature.get('geometry') or {}
        coords=geometry.get('coordinates') or []
        if len(coords)<2 or not isinstance(properties.get('time'),(float,int)):continue
        lon,lat=coords[:2]
        if not isinstance(lat,(int,float)) or not isinstance(lon,(int,float)) or not (-90<=lat<=90 and -180<=lon<=180):continue
        occurred=dt.datetime.fromtimestamp(properties['time']/1000,dt.timezone.utc)
        if not cutoff<=occurred<=now:continue
        link=properties.get('url') or ''
        if not link.startswith('https://earthquake.usgs.gov/'):continue
        event_id=str(feature.get('id') or link)
        if event_id in seen:continue
        seen.add(event_id)
        magnitude=properties.get('mag')
        events.append({'id':event_id,'lat':lat,'lng':lon,'type':'earthquake','category':'hazards',
                       'name':properties.get('place') or 'Earthquake','title':f"Earthquake: {properties.get('place') or 'Location not specified'}",
                       'magnitude':magnitude,'published_at':occurred.isoformat(),'url':link,
                       'source':'USGS','location_basis':'observed_event_coordinates','confidence':'reported_coordinates'})
    return sorted(events,key=lambda x:x['published_at'],reverse=True)

def collect():
    req=urllib.request.Request(ENDPOINT,headers={'User-Agent':'WorldPulse/1.5 (+https://github.com/DVExperiments/WorldPulse)'})
    with urllib.request.urlopen(req,timeout=25) as response:payload=json.load(response)
    events=convert(payload)
    OUTPUT.write_text(json.dumps({'schema':1,'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
          'status':'live','source':'USGS earthquakes 24h GeoJSON','meaning':'Recorded seismic events; not news articles','events':events},indent=1),encoding='utf-8')
    return len(events)

if __name__=='__main__':
    try:print(f'USGS events: {collect()}')
    except Exception as exc:
        print(f'USGS event source unavailable; retaining last-known snapshot: {exc}')
