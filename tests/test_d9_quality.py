import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from geo_quality_d9 import run_benchmark,report,story_classification,normalize_url
from geo_semantic_d7 import decision as d7
from geo_subject_d8 import decision as d8
class D9Test(unittest.TestCase):
 def test_benchmark(self):
  b=run_benchmark(json.loads((ROOT/'tests/d9_geo_benchmark.json').read_text(encoding='utf8')),d7,d8)
  self.assertEqual(b['failed'],0,b)
 def test_dedupe_and_no_geocoding(self):
  a={'title':'France and Italy face protests','description':'','url':'https://example.com/a?utm_source=foo','place':{'name':'France'},'geo_match':'headline'}
  r=report([a,{**a,'url':'https://example.com/a?utm_source=bar'}],[])
  self.assertEqual(r['unique_mapped_url_location_pairs'],1)
  self.assertEqual(r['multilocation_classifications']['multi_country_unresolved'],1)
  self.assertEqual(r['international_review_samples'][0]['automatic_additional_pins'],0)
 def test_nested_city_not_renamed(self):
  a={'title':'School opens in Toluca, Mexico','place':{'name':'Toluca'}}
  self.assertEqual(story_classification(a)['existing_selected_place'],'Toluca')
if __name__=='__main__':unittest.main()
