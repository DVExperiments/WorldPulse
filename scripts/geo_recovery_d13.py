"""D13: globally balanced shadow recovery of publisher-isolation losses.

Explicit country aliases and tightly scoped, curated locality-parent evidence are
review aids only. Neither creates nor moves any globe pin.
"""
from collections import Counter, defaultdict
import re
import unicodedata

COUNTRY_ALIASES = {
 'Vietnam': ('vietnam', 'viet nam', 'vietnã', 'vietnám', 'việt nam'),
 'Brazil': ('brazil', 'brasil', 'brésil'),
 'Mexico': ('mexico', 'méxico', 'mexique'),
 'India': ('india', 'índia', 'inde'),
 'Germany': ('germany', 'alemania', 'alemanha', 'allemagne', 'deutschland'),
 'France': ('france', 'frança', 'francia'),
 'United States': ('united states', 'estados unidos', 'états-unis'),
 'United Kingdom': ('united kingdom', 'reino unido', 'royaume-uni'),
 'China': ('china', 'chine'),
 'Japan': ('japan', 'japão', 'japón', 'japon'),
 'South Korea': ('south korea', 'coreia do sul', 'corea del sur', 'corée du sud'),
 'Russia': ('russia', 'rússia', 'rusia', 'russie'),
 'Ukraine': ('ukraine', 'ucrânia', 'ucrania'),
 'Nigeria': ('nigeria', 'nigéria'),
 'Portugal': ('portugal',),
 'Kenya': ('kenya', 'quénia', 'quênia'),
 'Argentina': ('argentina', 'argentine'),
 'Indonesia': ('indonesia', 'indonésia'),
 'Thailand': ('thailand', 'tailândia', 'tailandia', 'thaïlande'),
 'Turkey': ('turkey', 'türkiye', 'turquía', 'turquia', 'turquie'),
 'Egypt': ('egypt', 'egito', 'egipto', 'egipto', 'égypte'),
 'Canada': ('canada', 'canadá'),
 'Australia': ('australia', 'austrália', 'australie'),
 'New Zealand': ('new zealand', 'nova zelândia', 'nueva zelanda', 'nouvelle-zélande'),
 'South Africa': ('south africa', 'áfrica do sul', 'sudáfrica', 'afrique du sud'),
 'Chile': ('chile', 'chili'),
 'Colombia': ('colombia', 'colômbia', 'colombie'),
 'Peru': ('peru', 'perú', 'pérou'),
 'Spain': ('spain', 'españa', 'espanha', 'espagne'),
 'Italy': ('italy', 'italia', 'itália', 'italie'),
}
# Manual high-confidence administrative geography; not inferred from source edition.
# Additions must be tested for ambiguities and independent geographical validity.
PARENT_LOCALITIES = {
 'Vietnam': ('con dao', 'côn đảo', 'khanh hoa', 'khánh hòa', 'ho chi minh city', 'hanoi', 'hà nội', 'da nang', 'đà nẵng'),
 'Mexico': ('ciudad de méxico', 'mexico city', 'toluca, estado de méxico', 'guadalajara, jalisco'),
 'India': ('new delhi', 'mumbai, maharashtra', 'chennai, tamil nadu'),
 'Brazil': ('rio de janeiro', 'são paulo', 'brasília'),
 'Kenya': ('nairobi, kenya', 'mombasa, kenya'),
 'Nigeria': ('lagos, nigeria', 'abuja, nigeria'),
 'New Zealand': ('wellington, new zealand', 'auckland, new zealand'),
 'Chile': ('santiago de chile',),
 'France': ('paris, france', 'marseille, france'),
 'Australia': ('sydney, australia', 'melbourne, australia'),
 'Canada': ('toronto, canada', 'ottawa, canada'),
 'Portugal': ('lisboa, portugal', 'porto, portugal'),
}

def fold(s):
 s = unicodedata.normalize('NFKD', (s or '').casefold())
 return ''.join(c for c in s if not unicodedata.combining(c))

def contains(text, phrase):
 # Prevent substring collisions with people's names and longer tokens.
 return bool(re.search(r'(?<!\w)'+re.escape(fold(phrase))+r'(?!\w)', fold(text)))

def independent_evidence(title, clean_description, selected_place):
 """No source/publisher/url evidence is ever used; title and cleaned description only."""
 title=title or ''; clean_description=clean_description or ''
 aliases=COUNTRY_ALIASES.get(selected_place, ())
 localities=PARENT_LOCALITIES.get(selected_place, ())
 for phrase in aliases:
  if contains(title,phrase): return {'class':'headline_country_alias','evidence':phrase,'field':'headline'}
 for phrase in localities:
  if contains(title,phrase): return {'class':'headline_parent_locality','evidence':phrase,'field':'headline'}
 for phrase in aliases:
  if contains(clean_description,phrase): return {'class':'clean_description_country_alias','evidence':phrase,'field':'clean_description'}
 for phrase in localities:
  if contains(clean_description,phrase): return {'class':'clean_description_parent_locality','evidence':phrase,'field':'clean_description'}
 return {'class':'unsupported_after_isolation','evidence':None,'field':None}

def summarize(rows, per_place=4, max_samples=120):
 # Deduplicate URL/location pairs and distribute samples across all affected places.
 unique={}
 for row in rows:
  key=(row.get('url',''),row.get('current_place',''))
  unique.setdefault(key,row)
 values=list(unique.values())
 counts=Counter(r['recovery_class'] for r in values)
 affected_counts=Counter(r['recovery_class'] for r in values if r.get('classification') in ('lost_after_isolation','changed_after_isolation'))
 per=defaultdict(list)
 for r in values:
  if r.get('classification') in ('lost_after_isolation','changed_after_isolation'):
   per[r.get('current_place','Unknown')].append(r)
 for name in per: per[name].sort(key=lambda r:(r.get('recovery_class')!='unsupported_after_isolation',r.get('title','')))
 balanced=[]; active=sorted(per,key=lambda p:(-len(per[p]),p))
 # round-robin avoids top-location monopolies, while retaining the largest impact first.
 for i in range(per_place):
  for name in active:
   if len(balanced)>=max_samples:break
   if i<len(per[name]):
    r=per[name][i]
    balanced.append({k:r.get(k) for k in ('title','url','current_place','shadow_place','classification','recovery_class','evidence','evidence_field','publisher','clean_description_excerpt')})
  if len(balanced)>=max_samples:break
 impacted=Counter(r.get('current_place','Unknown') for r in values if r.get('classification') in ('lost_after_isolation','changed_after_isolation'))
 return {'mode':'shadow_only_no_live_changes','scope':'all_mapped_locations','distinct_url_location_pairs':len(values),'recovery_class_counts':dict(counts),'affected_only_recovery_class_counts':dict(affected_counts),
 'affected_locations':len(impacted),'affected_places_ranked':[{'place':p,'affected_pairs':n,'recovery_counts':dict(Counter(r['recovery_class'] for r in per[p]))} for p,n in impacted.most_common()],
 'balanced_review_samples':balanced,'review_sample_places':len(set(r['current_place'] for r in balanced)),
 'limits':['Curated language aliases and locality parents cover examples, not every language or world locality.','Presence of a country or parent locality is subject evidence, not independently verified event location.','No automatic pin removal or reassignment.','Shadow candidate matching does not perfectly reproduce the whole live decision chain.']}
