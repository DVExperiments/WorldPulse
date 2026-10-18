"""WorldPulse 2.0E: reviewed geographical subjects, no network or guesswork.

Only invoked after the legacy matchers. Coordinates identify approximate geographic
subjects, not verified event sites. Never infer from publisher or RSS edition.
"""
from __future__ import annotations
import re
import unicodedata
from collections import Counter

# label | level | latitude | longitude | variants. Rough representative anchors.
# Keep aliases distinctive; ambiguous city/common words intentionally omitted.
ROWS = [
('Gujarat','region',23.22,72.64,'gujarat'),
('West Bengal','region',22.99,87.86,'west bengal|paschim banga'),
('Balochistan','region',28.49,65.10,'balochistan|baluchistan'),
('Kudat','place',6.88,116.85,'kudat'),('Kisoro','place',-1.28,29.68,'kisoro'),
('Worcestershire','region',52.19,-2.22,'worcestershire'),
('Embu County','region',-0.53,37.46,'embu county'),
('County Down','region',54.33,-5.72,'county down'),
('Sabah','region',5.98,116.08,'sabah'),
('Whangārei','place',-35.73,174.32,'whangarei|whangārei'),
('Bozeman','place',45.68,-111.04,'bozeman'),
('Canary Islands','region',28.29,-16.55,'canary islands|islas canarias|iles canaries|ilhas canarias'),
('Tenerife','place',28.29,-16.63,'tenerife'),('Gran Canaria','place',28.10,-15.59,'gran canaria'),
('Lanzarote','place',29.05,-13.59,'lanzarote'),
('Auckland','place',-36.85,174.76,'auckland|tamaki makaurau'),
('Wellington','place',-41.29,174.78,'wellington new zealand|wellington nz|te whanganui a tara'),
('Christchurch','place',-43.53,172.63,'christchurch new zealand|christchurch nz|otautahi'),
('Rotorua','place',-38.14,176.25,'rotorua'),('Tauranga','place',-37.69,176.17,'tauranga'),
('Hawke’s Bay','region',-39.55,176.75,'hawkes bay|hawke’s bay|hawke\'s bay'),
('Waikato','region',-37.79,175.28,'waikato'),
('Viti Levu','region',-17.85,178.00,'viti levu'),('Suva','place',-18.14,178.44,'suva'),
('Port Vila','place',-17.73,168.32,'port vila'),
('Honiara','place',-9.43,159.96,'honiara'),
('Bougainville','region',-6.20,155.60,'bougainville'),
('Savai’i','region',-13.64,-172.43,'savaii|savai’i'),
('Upolu','region',-13.92,-171.76,'upolu'),
('Bandung','place',-6.91,107.61,'bandung'),('Surabaya','place',-7.25,112.75,'surabaya'),
('Medan','place',3.59,98.67,'medan indonesia|medan sumatra'),
('Aceh','region',4.70,96.75,'aceh'),('West Java','region',-6.91,107.60,'west java|jawa barat'),
('East Java','region',-7.55,112.00,'east java|jawa timur'),
('Mindanao','region',7.19,125.45,'mindanao'),
('Palawan','region',9.83,118.74,'palawan'),('Cebu','place',10.32,123.89,'cebu'),
('Davao','place',7.07,125.61,'davao'),
('Bengaluru','place',12.97,77.59,'bengaluru|bangalore'),
('Hyderabad','place',17.38,78.49,'hyderabad india|hyderabad telangana'),
('Chennai','place',13.08,80.27,'chennai|madras india'),
('Pune','place',18.52,73.86,'pune'),
('Odisha','region',20.95,85.10,'odisha|orissa'),
('Bihar','region',25.60,85.10,'bihar'),
('Punjab India','region',31.15,75.34,'punjab india|indian punjab'),
('Sindh','region',25.89,68.52,'sindh'),
('Khyber Pakhtunkhwa','region',34.11,72.00,'khyber pakhtunkhwa|kpk province'),
('Gilgit-Baltistan','region',35.80,74.98,'gilgit baltistan|gilgit-baltistan'),
('Dhaka','place',23.81,90.41,'dhaka'),('Chattogram','place',22.34,91.83,'chattogram|chittagong'),
('Sylhet','place',24.90,91.87,'sylhet'),
('Pokhara','place',28.21,83.99,'pokhara'),
('Chiang Mai','place',18.79,98.98,'chiang mai'),
('Phuket','place',7.88,98.39,'phuket'),
('Hanoi','place',21.03,105.85,'hanoi|ha noi'),
('Da Nang','place',16.06,108.22,'da nang|danang'),
('Ho Chi Minh City','place',10.82,106.63,'ho chi minh city|saigon'),
('Mandalay','place',21.98,96.09,'mandalay'),
('Yangon','place',16.84,96.17,'yangon|rangoon'),
('Rakhine State','region',20.10,93.20,'rakhine state'),
('Tigray','region',14.03,38.30,'tigray'),
('Amhara','region',11.60,38.43,'amhara region|amhara state'),
('Darfur','region',13.50,24.00,'darfur'),
('Khartoum','place',15.50,32.56,'khartoum'),
('Port Sudan','place',19.62,37.22,'port sudan'),
('Kampala','place',0.32,32.58,'kampala'),
('Entebbe','place',0.05,32.46,'entebbe'),
('Kisumu','place',-0.09,34.77,'kisumu'),
('Mombasa','place',-4.05,39.67,'mombasa'),
('Nakuru','place',-0.30,36.08,'nakuru'),
('Eldoret','place',0.52,35.27,'eldoret'),
('Kigali','place',-1.95,30.06,'kigali'),
('Goma','place',-1.68,29.22,'goma'),
('North Kivu','region',-0.60,29.20,'north kivu|nord kivu'),
('South Kivu','region',-3.10,28.50,'south kivu|sud kivu'),
('Kinshasa','place',-4.32,15.31,'kinshasa'),
('Lubumbashi','place',-11.66,27.48,'lubumbashi'),
('Lagos','place',6.52,3.38,'lagos nigeria|lagos state'),
('Abuja','place',9.08,7.40,'abuja'),
('Kano','place',12.00,8.52,'kano nigeria|kano state'),
('Kaduna','place',10.52,7.44,'kaduna'),
('Borno State','region',11.85,13.16,'borno state|borno'),
('Accra','place',5.60,-0.19,'accra'),
('Kumasi','place',6.69,-1.62,'kumasi'),
('Cape Coast','place',5.10,-1.25,'cape coast ghana'),
('Tamale Ghana','place',9.41,-0.84,'tamale ghana'),
('Freetown','place',8.48,-13.23,'freetown'),
('Monrovia','place',6.30,-10.80,'monrovia'),
('Dakar','place',14.69,-17.45,'dakar'),
('Bamako','place',12.65,-8.00,'bamako'),
('Ouagadougou','place',12.37,-1.52,'ouagadougou'),
('Niamey','place',13.51,2.11,'niamey'),
('Agadez','place',16.97,7.99,'agadez'),
('Marrakesh','place',31.63,-7.99,'marrakesh|marrakech'),
('Casablanca','place',33.57,-7.59,'casablanca morocco'),
('Fez Morocco','place',34.06,-4.98,'fez morocco|fes morocco'),
('Gaza Strip','region',31.40,34.36,'gaza strip|bande de gaza|franja de gaza|faixa de gaza'),
('West Bank','region',31.90,35.25,'west bank palestine|occupied west bank|cisjordania|cisjordanie'),
('Ramallah','place',31.90,35.20,'ramallah'),
('Khan Younis','place',31.35,34.30,'khan younis|khan yunis'),
('Rafah','place',31.29,34.25,'rafah gaza|rafah crossing'),
('Aleppo','place',36.20,37.16,'aleppo|halab syria'),
('Idlib','place',35.93,36.63,'idlib'),
('Homs','place',34.73,36.72,'homs syria'),
('Erbil','place',36.19,44.01,'erbil|arbil iraq'),
('Basra','place',30.51,47.81,'basra'),
('Isfahan','place',32.65,51.67,'isfahan|esfahan'),
('Shiraz','place',29.59,52.58,'shiraz iran'),
('Kerman','place',30.28,57.08,'kerman iran'),
('Sistan and Baluchestan','region',27.50,61.50,'sistan and baluchestan|sistan baluchestan'),
('Kharkiv','place',49.99,36.23,'kharkiv|kharkov'),
('Odesa','place',46.48,30.73,'odesa|odessa ukraine'),
('Dnipro','place',48.46,35.05,'dnipro ukraine|dnipropetrovsk'),
('Zaporizhzhia','place',47.84,35.14,'zaporizhzhia|zaporozhye'),
('Donetsk','place',48.00,37.80,'donetsk'),
('Luhansk','place',48.57,39.33,'luhansk|lugansk'),
('Crimea','region',45.30,34.40,'crimea|crimée|crimée|crimée|crimée|crimée|krym'),
('Transnistria','region',47.30,29.20,'transnistria|transdniestria'),
('Kosovo','region',42.60,21.00,'kosovo'),
('Catalonia','region',41.59,1.52,'catalonia|catalunya|catalogne|cataluña'),
('Andalusia','region',37.40,-4.57,'andalusia|andalucia|andalucía|andalousie'),
('Basque Country','region',43.05,-2.58,'basque country|pais vasco|país vasco|pays basque'),
('Sicily','region',37.60,14.02,'sicily|sicilia|sicile'),
('Sardinia','region',40.08,9.05,'sardinia|sardegna|sardaigne'),
('Bavaria','region',48.90,11.44,'bavaria|bayern|bavière'),
('Saxony','region',51.10,13.20,'saxony|sachsen|saxe germany'),
('Wales','region',52.13,-3.78,'wales uk|cymru|pays de galles'),
('Northern Ireland','region',54.70,-6.48,'northern ireland|irlande du nord|irlanda del norte'),
('Scotland','region',56.49,-4.20,'scotland|écosse|escocia'),
('Yorkshire','region',53.97,-1.08,'yorkshire'),
('Cornwall','region',50.27,-4.78,'cornwall england|cornwall uk|kernow'),
('São Paulo','place',-23.55,-46.63,'são paulo|sao paulo'),
('Rio de Janeiro','place',-22.91,-43.17,'rio de janeiro'),
('Brasília','place',-15.79,-47.88,'brasilia|brasília'),
('Recife','place',-8.05,-34.90,'recife'),
('Salvador Bahia','place',-12.98,-38.48,'salvador bahia|salvador brazil'),
('Bahia','region',-12.50,-41.60,'bahia brazil|estado da bahia'),
('Amazonas Brazil','region',-3.10,-60.00,'amazonas brazil|estado do amazonas'),
('Cusco','place',-13.53,-71.97,'cusco|cuzco'),
('Arequipa','place',-16.40,-71.54,'arequipa'),
('Lima','place',-12.05,-77.04,'lima peru'),
('Valparaíso','place',-33.05,-71.62,'valparaiso|valparaíso'),
('Concepción Chile','place',-36.83,-73.05,'concepcion chile|concepción chile'),
('Antofagasta','place',-23.65,-70.40,'antofagasta'),
('Patagonia','region',-45.50,-70.50,'patagonia|patagonie'),
('Mendoza Argentina','place',-32.89,-68.83,'mendoza argentina'),
('Rosario Argentina','place',-32.95,-60.67,'rosario argentina'),
('Córdoba Argentina','place',-31.42,-64.18,'cordoba argentina|córdoba argentina'),
('Medellín','place',6.24,-75.58,'medellin|medellín'),
('Cali Colombia','place',3.45,-76.53,'cali colombia'),
('Cartagena Colombia','place',10.40,-75.51,'cartagena colombia'),
('Quito','place',-0.18,-78.47,'quito'),
('Guayaquil','place',-2.19,-79.89,'guayaquil'),
('Maracaibo','place',10.64,-71.61,'maracaibo'),
('Caracas','place',10.48,-66.90,'caracas'),
('La Paz Bolivia','place',-16.50,-68.15,'la paz bolivia'),
('Santa Cruz Bolivia','place',-17.78,-63.18,'santa cruz bolivia|santa cruz de la sierra'),
]

def fold(text):
    text = unicodedata.normalize('NFKD', str(text or '').casefold())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', text)

INDEX = []
for name,level,lat,lng,aliases in ROWS:
    item = {'name':name,'level':level,'lat':lat,'lng':lng}
    for alias in aliases.split('|'):
        INDEX.append((fold(alias),item))
INDEX.sort(key=lambda pair:len(pair[0]),reverse=True)

# Reject ambiguous words and misleading metadata that occurs in RSS descriptions.
IGNORED_TEXT = re.compile(r'https?://\S+|<[^>]*>', re.I)

def expanded_match(title,description=''):
    """Returns (place, evidence), or (None, reason). Rejects distinct ambiguous places.

    Headline wins over description; a description cannot override an ambiguous title.
    Nested locality references, e.g. Kudat AND Sabah, are left unpinned when both
    are identified here, rather than guessing which geographic level is intended.
    """
    for method,raw in (('headline-expanded',title),('description-expanded',description)):
        text = fold(IGNORED_TEXT.sub(' ', raw or ''))
        hits = {}
        for alias,place in INDEX:
            if re.search(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',text):
                hits[place['name']] = place
        if len(hits)==1: return next(iter(hits.values())),method
        if len(hits)>1: return None,'ambiguous-expanded'
    return None,'unmapped'

def inspect_unmatched(report, limit=1000):
    """Offline dry run of sampled unmatched-review examples. Never modifies news."""
    samples=(report or {}).get('examples',[])[:limit]
    found=[];ambiguous=0
    for e in samples:
        place,method=expanded_match(e.get('title',''),e.get('description_excerpt',''))
        if place: found.append({'title':e.get('title','')[:140], 'place':place['name'],'basis':method})
        elif method=='ambiguous-expanded':ambiguous+=1
    return {'sample_count':len(samples),'recoverable_sample_count':len(found),
            'ambiguous_sample_count':ambiguous,'examples':found[:30],
            'note':'Dry-run against sample only; not a projection of live mapped articles.'}
