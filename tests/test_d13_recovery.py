import pathlib, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from geo_recovery_d13 import independent_evidence, summarize

def test_multilingual():
 assert independent_evidence('História do Vietnã','', 'Vietnam')['class']=='headline_country_alias'
 assert independent_evidence('Crise na Alemanha','','Germany')['class']=='headline_country_alias'
 assert independent_evidence('Inundaciones en México','','Mexico')['class']=='headline_country_alias'

def test_local_parent():
 assert independent_evidence('School in Con Dao','','Vietnam')['class']=='headline_parent_locality'
 assert independent_evidence('Evacuation in Wellington, New Zealand','','New Zealand')['class']=='headline_country_alias'

def test_metadata_not_evidence():
 assert independent_evidence('Company reports profits','', 'Vietnam')['class']=='unsupported_after_isolation'
 assert independent_evidence('Anand Sharma talks to press','', 'India')['class']=='unsupported_after_isolation'
 assert independent_evidence('Liberdade de expressão','', 'Brazil')['class']=='unsupported_after_isolation'

def test_balanced_sampling():
 rows=[]
 for p,n in [('Vietnam',20),('Mexico',3),('Nigeria',2)]:
  rows.extend(dict(url=f'https://example.com/{p}/{i}',current_place=p,title=str(i),classification='lost_after_isolation',recovery_class='unsupported_after_isolation') for i in range(n))
 r=summarize(rows,per_place=2)
 assert r['review_sample_places']==3
 assert len(r['balanced_review_samples'])==6
 assert r['affected_locations']==3
