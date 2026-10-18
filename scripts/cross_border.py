"""WorldPulse F4: cautious headline-evidenced bilateral news links.

No claim is made about verified event sites, direction of influence, or causality.
"""
import re
from collections import Counter

# Geographic coordinates are schematic national anchors, not event coordinates.
COUNTRIES = {
 'New Zealand':(-41.3,174.8,['new zealand','nz']), 'Australia':(-25.3,133.8,['australia','australian']),
 'United States':(39.8,-98.6,['united states','u.s.','u.s.a.','usa','american','us']),
 'Canada':(56.1,-106.3,['canada','canadian']), 'Mexico':(23.6,-102.6,['mexico','mexican']),
 'United Kingdom':(54.0,-2.0,['united kingdom','britain','british','uk']),
 'France':(46.6,2.2,['france','french']), 'Germany':(51.2,10.4,['germany','german']),
 'Spain':(40.4,-3.7,['spain','spanish']), 'Italy':(42.5,12.5,['italy','italian']),
 'Portugal':(39.5,-8.0,['portugal','portuguese']), 'Ireland':(53.3,-8.0,['ireland','irish']),
 'Ukraine':(49.0,32.0,['ukraine','ukrainian']), 'Russia':(61.5,105.3,['russia','russian']),
 'China':(35.9,104.2,['china','chinese']), 'India':(21.0,78.0,['india','indian']),
 'Pakistan':(30.4,69.3,['pakistan','pakistani']), 'Bangladesh':(23.7,90.4,['bangladesh','bangladeshi']),
 'Japan':(36.2,138.3,['japan','japanese']), 'South Korea':(35.9,127.8,['south korea','south korean']),
 'North Korea':(40.3,127.5,['north korea','north korean']), 'Taiwan':(23.7,121.0,['taiwan','taiwanese']),
 'Vietnam':(14.1,108.3,['vietnam','vietnamese']), 'Thailand':(15.9,100.9,['thailand','thai']),
 'Indonesia':(-0.8,113.9,['indonesia','indonesian']), 'Philippines':(12.9,121.8,['philippines','philippine','filipino']),
 'Malaysia':(4.2,101.9,['malaysia','malaysian']), 'Singapore':(1.35,103.8,['singapore','singaporean']),
 'Israel':(31.0,34.9,['israel','israeli']), 'Iran':(32.4,53.7,['iran','iranian']),
 'Saudi Arabia':(23.9,45.1,['saudi arabia','saudi']), 'Turkey':(39.0,35.2,['turkey','turkish','türkiye']),
 'Egypt':(26.8,30.8,['egypt','egyptian']), 'Yemen':(15.6,48.5,['yemen','yemeni']), 'South Africa':(-30.6,22.9,['south africa','south african']),
 'Nigeria':(9.1,8.7,['nigeria','nigerian']), 'Kenya':(-0.02,37.9,['kenya','kenyan']),
 'Brazil':(-14.2,-51.9,['brazil','brazilian']), 'Argentina':(-38.4,-63.6,['argentina','argentine']),
 'Chile':(-35.7,-71.5,['chile','chilean']), 'Colombia':(4.6,-74.3,['colombia','colombian']),
 'Poland':(51.9,19.1,['poland','polish']), 'Sweden':(60.1,18.6,['sweden','swedish']),
 'Norway':(60.5,8.5,['norway','norwegian']), 'Denmark':(56.3,9.5,['denmark','danish']),
 'Finland':(61.9,25.7,['finland','finnish']), 'Greece':(39.1,21.8,['greece','greek']),
}
# Only explicit bilateral framing; no link simply because two countries co-occur.
RELATIONS = {
 'agreement':r'\b(?:agreement|deal|pact|treaty|signs?|signed|partnership|joint declaration|memorandum)\b',
 'diplomacy':r'\b(?:bilateral|diplomatic|diplomacy|talks|summit|negotiat\w*|meeting|meet|leaders? discuss|ambassadors?)\b',
 'trade':r'\b(?:trade|tariffs?|imports?|exports?|investment|economic ties)\b',
 'sanctions':r'\b(?:sanctions?|embargo|restrictions?)\b',
 'dispute':r'\b(?:dispute|row|tensions?|clash|border standoff|accus\w*|condemn\w*)\b',
 'security':r'\b(?:military cooperation|defence cooperation|defense cooperation|joint drills?|security cooperation|ceasefire)\b',
}
EXCLUSIONS = re.compile(r'\b(?:world cup|football|cricket|rugby|tennis|versus|\bvs\.?\b|recipe|tourism guide|holiday destinations)\b',re.I)
def named_countries(title):
 found=[]
 for name,(lat,lng,aliases) in COUNTRIES.items():
  if any(re.search(r'(?<![\w])'+re.escape(a)+r'(?![\w])',title,re.I) for a in aliases):found.append(name)
 return found

def detect(title):
 if not isinstance(title,str) or EXCLUSIONS.search(title) or re.search(r'\bdiplomatic (?:cars?|convoy|vehicles?)\b',title,re.I):return None
 countries=named_countries(title)
 if len(countries)!=2:return None
 relation=next((kind for kind,pattern in RELATIONS.items() if re.search(pattern,title,re.I)),None)
 if relation is None:return None
 return tuple(sorted(countries)),relation

def publish_links(points,max_articles=3000):
 # Deduplicate the same article syndicated into several country/category points.
 by_url={}
 for point in points:
  for article in point.get('articles',[]):
   url=article.get('url','');title=article.get('title','')
   if url and url.startswith(('http://','https://')) and url not in by_url:by_url[url]=article
   if len(by_url)>=max_articles:break
 grouped={}
 for article in by_url.values():
  match=detect(article.get('title',''))
  if not match:continue
  pair,relation=match
  key=(pair,relation)
  grouped.setdefault(key,[]).append({'title':article.get('title',''),'publisher':article.get('publisher',''),'url':article['url'],'published_at':article.get('published_at','')})
 links=[]
 for (pair,relation),articles in grouped.items():
  dedup=list({a['url']:a for a in articles}.values())
  publisher_count=len({a['publisher'].casefold() for a in dedup if a['publisher']})
  links.append({'countries':[{'name':n,'lat':COUNTRIES[n][0],'lng':COUNTRIES[n][1]} for n in pair],
    'relationship':relation,'article_count':len(dedup),'publisher_count':publisher_count,
    'evidence':'explicit_bilateral_headline','note':'Headline-based relationship candidate. Country points are representative anchors; not verified event sites.',
    'articles':dedup[:12]})
 links.sort(key=lambda x:(-x['publisher_count'],-x['article_count'],x['countries'][0]['name']))
 return {'schema':1,'method':'explicit_two_country_headline_with_relationship_terms','scope':'Sampled feed headlines only; potential cross-border relationship, not fact-checked or verified','total_candidates':len(links),'links':links[:40]}
