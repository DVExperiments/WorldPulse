"""D14: audit-only hierarchy and country contradiction evidence.

Country aliases sourced from D13 curated multilingual labels. Hierarchy is a
small explicit verified administrative relationship set; never infer from publisher
origin, feed edition, coordinates alone, or an ambiguous place name.
"""
from collections import Counter, defaultdict
import re
from geo_recovery_d13 import COUNTRY_ALIASES, PARENT_LOCALITIES, contains

# Only unambiguous names or administratively qualified phrases. This expands
# coverage worldwide without pretending to be a complete gazetteer.
PARENTS = {
 'India': ('mumbai', 'bombay', 'new delhi', 'chennai', 'kolkata', 'bengaluru', 'hyderabad, telangana', 'pune, maharashtra'),
 'Mexico': ('apodaca, nuevo leon', 'apodaca, nuevo león', 'nuevo leon', 'nuevo león', 'guadalajara, jalisco', 'monterrey, nuevo león', 'oaxaca, mexico', 'oaxaca, méxico'),
 'Vietnam': ('con dao', 'côn đảo', 'khanh hoa', 'khánh hòa', 'son thuy', 'sơn thủy', 'ho chi minh city', 'hanoi', 'da nang'),
 'Brazil': ('sao paulo', 'são paulo', 'rio de janeiro', 'brasilia', 'brasília', 'belo horizonte, minas gerais', 'porto alegre, rio grande do sul'),
 'Argentina': ('buenos aires, argentina', 'córdoba, argentina', 'rosario, santa fe'),
 'Chile': ('santiago de chile', 'valparaiso, chile', 'valparaíso, chile', 'concepcion, chile', 'concepción, chile'),
 'Peru': ('lima, peru', 'lima, perú', 'cusco, peru', 'arequipa, peru'),
 'Colombia': ('bogota', 'bogotá', 'medellin', 'medellín', 'cali, colombia'),
 'Nigeria': ('lagos, nigeria', 'abuja', 'ibadan, nigeria', 'kano, nigeria'),
 'Kenya': ('nairobi', 'mombasa', 'kisumu, kenya', 'nakuru, kenya'),
 'Ghana': ('accra', 'kumasi, ghana', 'tamale, ghana'),
 'South Africa': ('johannesburg', 'cape town', 'pretoria', 'durban, south africa'),
 'France': ('paris, france', 'marseille', 'lyon, france', 'toulouse, france'),
 'Germany': ('berlin, germany', 'munich', 'münchen', 'hamburg, germany', 'frankfurt am main'),
 'Spain': ('madrid', 'barcelona, spain', 'sevilla, españa', 'valencia, spain'),
 'Italy': ('rome, italy', 'roma, italia', 'milan', 'milano', 'naples, italy'),
 'Portugal': ('lisboa', 'lisbon', 'porto, portugal', 'coimbra, portugal'),
 'United Kingdom': ('london, england', 'manchester, england', 'birmingham, england', 'glasgow, scotland'),
 'United States': ('new york city', 'los angeles, california', 'washington, dc', 'chicago, illinois'),
 'Canada': ('toronto', 'ottawa, canada', 'vancouver, canada', 'montreal, quebec', 'montréal, québec'),
 'Australia': ('sydney, australia', 'melbourne, australia', 'brisbane, queensland', 'perth, western australia'),
 'New Zealand': ('auckland, new zealand', 'wellington, new zealand', 'christchurch, new zealand', 'dunedin, new zealand'),
 'China': ('beijing', 'shanghai', 'guangzhou', 'shenzhen, china'),
 'Japan': ('tokyo', 'osaka, japan', 'kyoto, japan', 'yokohama, japan'),
 'South Korea': ('seoul', 'busan, south korea', 'incheon, south korea'),
 'Indonesia': ('jakarta', 'surabaya, indonesia', 'bandung, indonesia'),
 'Thailand': ('bangkok', 'chiang mai', 'phuket, thailand'),
 'Ukraine': ('kyiv', 'kiev, ukraine', 'odesa, ukraine', 'kharkiv, ukraine'),
 'Russia': ('moscow', 'moskva', 'saint petersburg, russia', 'st petersburg, russia'),
 'Turkey': ('istanbul', 'ankara', 'izmir, turkey', 'i̇zmir, türkiye'),
 'Egypt': ('cairo', 'alexandria, egypt', 'giza, egypt'),
 'Qatar': ('doha, qatar',),
 'United Arab Emirates': ('abu dhabi', 'dubai, uae'),
}
# Curated lists give independent parent-country support only. They are not a
# substitute for administrative hierarchy records or verification of an event.
for k, values in PARENT_LOCALITIES.items():
 PARENTS[k] = tuple(dict.fromkeys(PARENTS.get(k, ()) + values))

def mentions(text):
 """Find country evidence in a field; return keyed evidence, not an event location."""
 found={}
 for country, aliases in COUNTRY_ALIASES.items():
  for alias in aliases:
   if contains(text, alias):
    found[country]={'kind':'country_alias','phrase':alias};break
 for country, localities in PARENTS.items():
  if country in found:continue
  for locality in localities:
   if contains(text, locality):
    found[country]={'kind':'curated_parent_locality','phrase':locality};break
 return found

def classify(title, clean_description, selected_place, isolation_status):
 """No live change. Contradiction requires a single explicit OTHER country."""
 title_evidence=mentions(title)
 desc_evidence=mentions(clean_description)
 selected_title=title_evidence.get(selected_place)
 selected_desc=desc_evidence.get(selected_place)
 other_explicit={k:v for k,v in title_evidence.items() if k!=selected_place and v['kind']=='country_alias'}
 if selected_title:
  decision='supported_by_headline'
 elif selected_desc:
  decision='supported_by_clean_description'
 elif len(other_explicit)==1 and len(title_evidence)==1:
  decision='potential_headline_country_contradiction'
 elif len(title_evidence)>=2:
  decision='multicountry_requires_review'
 elif isolation_status in ('lost_after_isolation','changed_after_isolation'):
  decision='unsupported_after_isolation'
 else:
  decision='no_curated_hierarchy_evidence'
 return {'decision':decision,'selected_evidence':selected_title or selected_desc,
         'headline_countries':title_evidence,'description_countries':desc_evidence,
         'contradiction_country':next(iter(other_explicit)) if decision=='potential_headline_country_contradiction' else None,
         'live_action':'none'}

def report(rows, max_samples=120):
 unique={}
 for r in rows:unique.setdefault((r.get('url',''),r.get('selected_place','')),r)
 vals=list(unique.values()); classes=Counter(r['decision'] for r in vals)
 by_place=defaultdict(list)
 for r in vals:
  if r['decision'] in ('potential_headline_country_contradiction','unsupported_after_isolation','multicountry_requires_review'):
   by_place[r['selected_place']].append(r)
 # Round-robin by geography, not volume. Examples need to include minority regions.
 for v in by_place.values():v.sort(key=lambda r:(r['decision']!='potential_headline_country_contradiction',r.get('title','')))
 sample=[];places=sorted(by_place,key=lambda k:(-len(by_place[k]),k))
 for idx in range(max((len(x) for x in by_place.values()),default=0)):
  for p in places:
   if idx<len(by_place[p]):
    r=by_place[p][idx]
    sample.append({k:r.get(k) for k in ('title','url','publisher','selected_place','decision','contradiction_country','isolation_status','selected_evidence','headline_countries','description_countries')})
    if len(sample)>=max_samples:break
  if len(sample)>=max_samples:break
 return {'release':'v2.4D.14','mode':'shadow_only_no_live_changes','scope':'all_mapped_locations',
  'distinct_url_location_pairs':len(vals),'classification_counts':dict(classes),
  'review_locations':len(by_place),'review_counts_by_place':[{'place':k,'count':len(v),'contradictions':sum(r['decision']=='potential_headline_country_contradiction' for r in v)} for k,v in sorted(by_place.items(),key=lambda x:-len(x[1]))],
  'balanced_review_samples':sample,'sampled_places':len({r['selected_place'] for r in sample}),
  'hierarchy_country_count':len(PARENTS),'limits':['Curated explicit locality-country relationships are incomplete, even across listed countries.', 'Alias mentions do not prove an event happened in that country.', 'Headline contradiction is a review flag, not proof the selected location is wrong; diplomatic, comparison, and international stories may legitimately mention another country.', 'Uses cleaned description; no publisher or feed geography evidence.','Never changes or removes a globe marker.']}
