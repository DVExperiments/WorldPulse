#!/usr/bin/env python3
"""WorldPulse collector: GDELT DOC 2.0 articles, mapped only by explicit headline place names.

No publisher-IP/sourcelocation guesses. Counts = unique matching articles in returned
samples, NOT all articles published in the last 24 hours.
"""
import datetime as dt
import json
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'news.json'
API = 'https://api.gdeltproject.org/api/v2/doc/doc'
CATEGORIES = {
    'politics': '(election OR parliament OR government OR diplomacy)',
    'environment': '(climate OR wildlife OR pollution OR conservation)',
    'hazards': '(earthquake OR flood OR wildfire OR hurricane)',
    'society': '(protest OR education OR healthcare OR housing)',
    'economy': '(inflation OR trade OR economy OR employment)',
    'science': '(research OR technology OR discovery OR science)',
}
# Stable, deliberately small local gazetteer. Only unambiguous place names are
# included. Extend separately as needed; matching article text is not geocoding.
PLACES = [
 ('New Zealand',-41.29,174.78),('Auckland',-36.85,174.76),('Wellington',-41.29,174.78),
 ('Australia',-35.28,149.13),('Sydney',-33.87,151.21),('Melbourne',-37.81,144.96),
 ('Japan',35.68,139.69),('Tokyo',35.68,139.69),('Osaka',34.69,135.5),
 ('China',39.9,116.4),('Beijing',39.9,116.4),('Shanghai',31.23,121.47),
 ('Taiwan',25.03,121.56),('Taipei',25.03,121.56),('Hong Kong',22.32,114.17),
 ('South Korea',37.57,126.98),('Seoul',37.57,126.98),('North Korea',39.04,125.76),
 ('India',28.61,77.21),('Delhi',28.61,77.21),('Mumbai',19.08,72.88),
 ('Pakistan',33.69,73.06),('Islamabad',33.69,73.06),('Bangladesh',23.81,90.41),
 ('Indonesia',-6.21,106.85),('Jakarta',-6.21,106.85),('Philippines',14.6,120.98),
 ('Manila',14.6,120.98),('Vietnam',21.03,105.85),('Hanoi',21.03,105.85),
 ('Thailand',13.76,100.50),('Bangkok',13.76,100.50),('Singapore',1.35,103.82),
 ('Malaysia',3.14,101.69),('Kuala Lumpur',3.14,101.69),
 ('United States',38.9,-77.04),('USA',38.9,-77.04),('Washington DC',38.9,-77.04),
 ('New York',40.71,-74.01),('Los Angeles',34.05,-118.24),('San Francisco',37.77,-122.42),
 ('Chicago',41.88,-87.63),('Houston',29.76,-95.37),('Seattle',47.61,-122.33),
 ('Miami',25.76,-80.19),('Boston',42.36,-71.06),('California',36.78,-119.42),
 ('Texas',31.0,-99.9),('Florida',27.66,-81.52),('Canada',45.42,-75.70),
 ('Toronto',43.65,-79.38),('Vancouver',49.28,-123.12),('Ottawa',45.42,-75.7),
 ('Mexico',19.43,-99.13),('Mexico City',19.43,-99.13),
 ('Brazil',-15.79,-47.88),('Brasilia',-15.79,-47.88),('São Paulo',-23.55,-46.63),
 ('Sao Paulo',-23.55,-46.63),('Rio de Janeiro',-22.91,-43.2),
 ('Argentina',-34.6,-58.38),('Buenos Aires',-34.6,-58.38),
 ('Chile',-33.45,-70.67),('Santiago',-33.45,-70.67),
 ('Colombia',4.71,-74.07),('Bogota',4.71,-74.07),('Peru',-12.05,-77.04),
 ('Lima',-12.05,-77.04),('Venezuela',10.48,-66.9),('Caracas',10.48,-66.9),
 ('United Kingdom',51.51,-0.13),('Britain',51.51,-0.13),('London',51.51,-0.13),
 ('England',52.36,-1.17),('Scotland',55.95,-3.19),('Edinburgh',55.95,-3.19),
 ('Ireland',53.35,-6.26),('Dublin',53.35,-6.26),
 ('France',48.86,2.35),('Paris',48.86,2.35),('Germany',52.52,13.41),
 ('Berlin',52.52,13.41),('Munich',48.14,11.58),('Italy',41.9,12.5),
 ('Rome',41.9,12.5),('Milan',45.46,9.19),('Spain',40.42,-3.7),
 ('Madrid',40.42,-3.7),('Barcelona',41.39,2.17),('Portugal',38.72,-9.14),
 ('Lisbon',38.72,-9.14),('Netherlands',52.37,4.9),('Amsterdam',52.37,4.9),
 ('Belgium',50.85,4.35),('Brussels',50.85,4.35),('Switzerland',46.95,7.45),
 ('Zurich',47.38,8.54),('Austria',48.21,16.37),('Vienna',48.21,16.37),
 ('Poland',52.23,21.01),('Warsaw',52.23,21.01),('Ukraine',50.45,30.52),
 ('Kyiv',50.45,30.52),('Russia',55.75,37.62),('Moscow',55.75,37.62),
 ('Sweden',59.33,18.07),('Stockholm',59.33,18.07),('Norway',59.91,10.75),
 ('Oslo',59.91,10.75),('Finland',60.17,24.94),('Helsinki',60.17,24.94),
 ('Denmark',55.68,12.57),('Copenhagen',55.68,12.57),
 ('Greece',37.98,23.73),('Athens',37.98,23.73),('Turkey',39.93,32.86),
 ('Istanbul',41.01,28.98),('Ankara',39.93,32.86),
 ('Israel',31.77,35.22),('Jerusalem',31.77,35.22),('Tel Aviv',32.09,34.78),
 ('Gaza',31.5,34.47),('West Bank',31.9,35.2),('Lebanon',33.89,35.5),
 ('Beirut',33.89,35.5),('Syria',33.51,36.29),('Damascus',33.51,36.29),
 ('Iran',35.69,51.39),('Tehran',35.69,51.39),('Iraq',33.31,44.37),
 ('Baghdad',33.31,44.37),('Saudi Arabia',24.71,46.67),('Riyadh',24.71,46.67),
 ('Qatar',25.29,51.53),('Doha',25.29,51.53),('Dubai',25.2,55.27),
 ('United Arab Emirates',24.45,54.38),('Yemen',15.37,44.19),
 ('Egypt',30.04,31.24),('Cairo',30.04,31.24),('Morocco',34.02,-6.84),
 ('Rabat',34.02,-6.84),('Algeria',36.75,3.06),('Tunisia',36.81,10.18),
 ('Libya',32.9,13.18),('Tripoli',32.9,13.18),('Sudan',15.5,32.56),
 ('Khartoum',15.5,32.56),('Ethiopia',9.03,38.75),('Addis Ababa',9.03,38.75),
 ('Kenya',-1.29,36.82),('Nairobi',-1.29,36.82),('Uganda',0.35,32.58),
 ('Nigeria',9.06,7.49),('Abuja',9.06,7.49),('Lagos',6.52,3.38),
 ('Ghana',5.56,-0.2),('Accra',5.56,-0.2),('South Africa',-25.75,28.23),
 ('Johannesburg',-26.2,28.04),('Cape Town',-33.92,18.42),
 ('Zimbabwe',-17.83,31.05),('Harare',-17.83,31.05),
 ('DR Congo',-4.32,15.31),('Kinshasa',-4.32,15.31),
]
MATCHERS = [(name, lat, lng, re.compile(r'(?<!\w)' + re.escape(name) + r'(?!\w)', re.I)) for name,lat,lng in PLACES]

def fetch_category(category, query):
    params = urlencode({'query': query, 'mode': 'artlist', 'format': 'json',
                        'timespan': '1d', 'maxrecords': '250', 'sort': 'datedesc'})
    req = Request(API + '?' + params, headers={'User-Agent': 'WorldPulse/1.1 (+https://github.com/DVExperiments/WorldPulse)', 'Accept': 'application/json'})
    with urlopen(req, timeout=65) as res:
        payload = json.load(res)
    if not isinstance(payload, dict) or not isinstance(payload.get('articles'), list):
        raise ValueError('Expected GDELT DOC article list; check API response/query limits')
    groups = {}
    for article in payload['articles']:
        title = str(article.get('title') or '').strip()
        url = str(article.get('url') or '').strip()
        if not title or not url.startswith(('https://','http://')):
            continue
        # GDELT title text must explicitly contain the place; a publisher's
        # home country, story topic, and full article are NOT location evidence.
        matches = [(name,lat,lng) for name,lat,lng,regex in MATCHERS if regex.search(title)]
        # Prefer the most specific textual match so 'Mexico City' wins over Mexico.
        if matches:
            matches.sort(key=lambda row: len(row[0]), reverse=True)
            name,lat,lng = matches[0]
            key = (name.lower(), lat, lng)
            entry = groups.setdefault(key, {'lat':lat, 'lng':lng, 'name':name, 'count':0,
                                            'category':category, 'articles':[]})
            if all(item['url'] != url for item in entry['articles']):
                entry['count'] += 1
                if len(entry['articles']) < 8:
                    entry['articles'].append({'title':title[:240], 'url':url})
    return list(groups.values()), len(payload['articles'])

def main():
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    old = {}
    if OUT.exists():
        try: old = json.loads(OUT.read_text(encoding='utf-8'))
        except (OSError, ValueError): pass
    points, errors, successes, inspected = [], {}, [], {}
    for category, query in CATEGORIES.items():
        try:
            found, scanned = fetch_category(category, query)
            points.extend(found); successes.append(category); inspected[category] = scanned
            print(f'{category}: scanned {scanned} articles, mapped {len(found)} named places')
        except Exception as exc:
            errors[category] = str(exc)
            print(f'{category}: FAILED: {exc}')
        time.sleep(6)  # Avoid bursting GDELT's public API.
    if successes:
        # Old records from GEO 2.0 must NOT be mixed with article counts.
        prior = old.get('points', []) if old.get('source') == 'GDELT DOC 2.0' else []
        points.extend(p for p in prior if p.get('category') in errors)
    else:
        points = old.get('points', [])
    status = 'live' if len(successes) == len(CATEGORIES) else ('partial' if successes else 'stale')
    record = {'schema':1, 'updated_at': now if successes else old.get('updated_at'),
              'last_attempt_at':now, 'status':status, 'source':'GDELT DOC 2.0',
              'window':'rolling 24 hours',
              'metric':'Unique article URLs within sampled GDELT DOC results whose headline explicitly names this place; not total news output',
              'categories_updated':successes, 'articles_scanned':inspected,
              'errors':errors, 'points':points}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(record,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Wrote {len(points)} mapped points to {OUT} (status={status})')
    if not successes: raise SystemExit('All feeds failed; preserved last-known data')

if __name__ == '__main__': main()
