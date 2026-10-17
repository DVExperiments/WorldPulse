#!/usr/bin/env python3
"""WorldPulse news collector v1.2 — Google News public RSS fallback.

Uses recent headline matches to explicit locations. These are *sample counts*,
not the complete number of stories published in a geographic area.
Dependencies: Python standard library only.
"""
import datetime as dt
import email.utils
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'news.json'
RSS = 'https://news.google.com/rss/search'
CATEGORIES = {
    'politics': '(election OR parliament OR government OR diplomacy) when:1d',
    'environment': '(climate OR wildlife OR pollution OR conservation) when:1d',
    'hazards': '(earthquake OR flood OR wildfire OR hurricane) when:1d',
    'society': '(protest OR education OR healthcare OR housing) when:1d',
    'economy': '(inflation OR trade OR economy OR employment) when:1d',
    'science': '(research OR technology OR discovery OR science) when:1d',
}
# Deliberately explicit gazetteer. Do not infer a news location from a publisher.
# Coordinates for countries are indicative map anchors, not exact event locations.
PLACES = [
 ('New Zealand',-41.29,174.78),('Auckland',-36.85,174.76),('Wellington',-41.29,174.78),
 ('Australia',-35.28,149.13),('Sydney',-33.87,151.21),('Melbourne',-37.81,144.96),
 ('Japan',35.68,139.69),('Tokyo',35.68,139.69),('Osaka',34.69,135.5),
 ('China',39.9,116.4),('Beijing',39.9,116.4),('Shanghai',31.23,121.47),
 ('Taiwan',25.03,121.56),('Taipei',25.03,121.56),('Hong Kong',22.32,114.17),
 ('South Korea',37.57,126.98),('Seoul',37.57,126.98),('North Korea',39.04,125.76),
 ('India',28.61,77.21),('Delhi',28.61,77.21),('Mumbai',19.08,72.88),
 ('Pakistan',33.69,73.06),('Bangladesh',23.81,90.41),('Indonesia',-6.21,106.85),
 ('Jakarta',-6.21,106.85),('Philippines',14.6,120.98),('Manila',14.6,120.98),
 ('Vietnam',21.03,105.85),('Thailand',13.76,100.50),('Bangkok',13.76,100.50),
 ('Singapore',1.35,103.82),('Malaysia',3.14,101.69),('Kuala Lumpur',3.14,101.69),
 ('United States',38.9,-77.04),('USA',38.9,-77.04),('Washington DC',38.9,-77.04),
 ('New York',40.71,-74.01),('Los Angeles',34.05,-118.24),('San Francisco',37.77,-122.42),
 ('Chicago',41.88,-87.63),('Houston',29.76,-95.37),('Seattle',47.61,-122.33),
 ('Miami',25.76,-80.19),('California',36.78,-119.42),('Texas',31.0,-99.9),
 ('Florida',27.66,-81.52),('Canada',45.42,-75.70),('Toronto',43.65,-79.38),
 ('Vancouver',49.28,-123.12),('Mexico City',19.43,-99.13),('Mexico',19.43,-99.13),
 ('Brazil',-15.79,-47.88),('Sao Paulo',-23.55,-46.63),('São Paulo',-23.55,-46.63),
 ('Rio de Janeiro',-22.91,-43.2),('Argentina',-34.6,-58.38),('Buenos Aires',-34.6,-58.38),
 ('Chile',-33.45,-70.67),('Santiago',-33.45,-70.67),('Colombia',4.71,-74.07),
 ('Bogota',4.71,-74.07),('Peru',-12.05,-77.04),('Lima',-12.05,-77.04),
 ('Venezuela',10.48,-66.9),('United Kingdom',51.51,-0.13),('Britain',51.51,-0.13),
 ('London',51.51,-0.13),('England',52.36,-1.17),('Scotland',55.95,-3.19),
 ('Ireland',53.35,-6.26),('Dublin',53.35,-6.26),('France',48.86,2.35),
 ('Paris',48.86,2.35),('Germany',52.52,13.41),('Berlin',52.52,13.41),
 ('Italy',41.9,12.5),('Rome',41.9,12.5),('Spain',40.42,-3.7),
 ('Madrid',40.42,-3.7),('Barcelona',41.39,2.17),('Portugal',38.72,-9.14),
 ('Netherlands',52.37,4.9),('Amsterdam',52.37,4.9),('Belgium',50.85,4.35),
 ('Switzerland',46.95,7.45),('Austria',48.21,16.37),('Poland',52.23,21.01),
 ('Ukraine',50.45,30.52),('Kyiv',50.45,30.52),('Russia',55.75,37.62),
 ('Moscow',55.75,37.62),('Sweden',59.33,18.07),('Norway',59.91,10.75),
 ('Finland',60.17,24.94),('Denmark',55.68,12.57),('Greece',37.98,23.73),
 ('Turkey',39.93,32.86),('Istanbul',41.01,28.98),('Israel',31.77,35.22),
 ('Jerusalem',31.77,35.22),('Tel Aviv',32.09,34.78),('Gaza',31.5,34.47),
 ('West Bank',31.9,35.2),('Lebanon',33.89,35.5),('Beirut',33.89,35.5),
 ('Syria',33.51,36.29),('Damascus',33.51,36.29),('Iran',35.69,51.39),
 ('Tehran',35.69,51.39),('Iraq',33.31,44.37),('Baghdad',33.31,44.37),
 ('Saudi Arabia',24.71,46.67),('Qatar',25.29,51.53),('Dubai',25.2,55.27),
 ('United Arab Emirates',24.45,54.38),('Yemen',15.37,44.19),('Egypt',30.04,31.24),
 ('Cairo',30.04,31.24),('Morocco',34.02,-6.84),('Algeria',36.75,3.06),
 ('Tunisia',36.81,10.18),('Libya',32.9,13.18),('Sudan',15.5,32.56),
 ('Ethiopia',9.03,38.75),('Kenya',-1.29,36.82),('Nairobi',-1.29,36.82),
 ('Uganda',0.35,32.58),('Nigeria',9.06,7.49),('Lagos',6.52,3.38),
 ('Ghana',5.56,-0.2),('South Africa',-25.75,28.23),('Johannesburg',-26.2,28.04),
 ('Cape Town',-33.92,18.42),('Zimbabwe',-17.83,31.05),('DR Congo',-4.32,15.31)
]
MATCHERS = [(name,lat,lng,re.compile(r'(?<!\w)' + re.escape(name) + r'(?!\w)', re.I)) for name,lat,lng in PLACES]

def fetch_category(category, query, now):
    url = RSS + '?' + urlencode({'q':query,'hl':'en-US','gl':'US','ceid':'US:en','num':'100'})
    req = Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; WorldPulse/1.2; +https://github.com/DVExperiments/WorldPulse)', 'Accept':'application/rss+xml, application/xml, text/xml'})
    try:
        with urlopen(req, timeout=40) as res:
            raw = res.read(3_000_000)
    except HTTPError as exc:
        raise RuntimeError(f'RSS HTTP {exc.code} ({url.split("?")[0]})') from exc
    except URLError as exc:
        raise RuntimeError(f'RSS connectivity error: {exc.reason}') from exc
    root = ET.fromstring(raw)
    if root.tag != 'rss' and not root.findall('.//item'):
        raise ValueError('Received a non-RSS response')
    items = root.findall('./channel/item')
    grouped = {}
    cutoff = now - dt.timedelta(hours=24)
    valid = 0
    for item in items:
        title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        published = (item.findtext('pubDate') or '').strip()
        if not title or not link.startswith(('https://','http://')):
            continue
        if published:
            try:
                article_time = email.utils.parsedate_to_datetime(published)
                if article_time.tzinfo is None: article_time = article_time.replace(tzinfo=dt.timezone.utc)
                if article_time < cutoff or article_time > now + dt.timedelta(hours=1):
                    continue
            except (TypeError, ValueError, IndexError):
                continue
        else:
            continue
        valid += 1
        # Google News embeds publisher suffix in titles; use titles as RSS provides.
        matches = [(name,lat,lng) for name,lat,lng,rx in MATCHERS if rx.search(title)]
        if not matches: continue
        name, lat, lng = max(matches,key=lambda t:len(t[0]))
        key = (name.lower(),lat,lng)
        entry = grouped.setdefault(key, {'lat':lat,'lng':lng,'name':name,'count':0,'category':category,'articles':[]})
        if len(entry['articles']) < 8 and link not in [a['url'] for a in entry['articles']]:
            entry['articles'].append({'title':title[:240],'url':link})
        # Unique URLs in this category/location (track beyond display limit).
        entry.setdefault('_seen',set()).add(link)
    for entry in grouped.values():
        entry['count'] = len(entry.pop('_seen'))
    return list(grouped.values()), valid

def main():
    now = dt.datetime.now(dt.timezone.utc)
    timestamp = now.isoformat(timespec='seconds')
    old = {}
    if OUT.exists():
        try: old = json.loads(OUT.read_text(encoding='utf-8'))
        except (OSError,ValueError): pass
    points,errors,successes,inspected = [],{},[],{}
    for category,query in CATEGORIES.items():
        try:
            found, scanned = fetch_category(category,query,now)
            points.extend(found)
            successes.append(category)
            inspected[category] = scanned
            print(f'{category}: RSS read {scanned} articles from last 24 hours, mapped {len(found)} headline locations',flush=True)
        except Exception as exc:
            errors[category] = str(exc)
            print(f'{category}: FAILED: {exc}',flush=True)
        time.sleep(2)
    if successes:
        prior = old.get('points',[]) if old.get('source') == 'Google News RSS' else []
        points.extend(p for p in prior if p.get('category') in errors)
    else:
        points = old.get('points',[])
    status = 'live' if len(successes)==len(CATEGORIES) else ('partial' if successes else 'stale')
    record = {'schema':1,'updated_at':timestamp if successes else old.get('updated_at'),
        'last_attempt_at':timestamp,'status':status,'source':'Google News RSS',
        'window':'rolling 24 hours',
        'metric':'Distinct RSS article URLs in sampled search results with an explicitly named place in the headline; not all news published there',
        'categories_updated':successes,'articles_scanned':inspected,'errors':errors,'points':points}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(record,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Wrote {len(points)} points to {OUT}, status={status}',flush=True)
    if not successes: raise SystemExit('All RSS feeds failed; retained last-known data')

if __name__=='__main__': main()
