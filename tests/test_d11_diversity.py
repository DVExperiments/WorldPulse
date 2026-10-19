import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_diversity_d11 import report

class D11(unittest.TestCase):
 def row(self, place, publisher, title, url, level='country', description='', feed='google/community/MX'):
  return dict(place={'name':place,'level':level},publisher=publisher,title=title,url=url,description=description,geo_match='headline',source_region='MX',audit_feed_key=feed,category='community')
 def test_all_places_and_diversity(self):
  rows=[self.row('Vietnam','News A','Local story in Vietnam','https://example.org/1'),
        self.row('Vietnam','News A','Village report Vietnam','https://example.org/2'),
        self.row('Vietnam','News B','Science Vietnam','https://example.org/3'),
        self.row('Kenya','News K','Floods in Kenya','https://example.org/4'),
        self.row('Brazil','News B','Harvest in Brazil','https://example.org/5'),
        self.row('Chile','News C','Research in Chile','https://example.org/6')]
  r=report(rows,[]);self.assertEqual(r['global_summary']['mapped_locations'],4)
  v=next(x for x in r['locations'] if x['place']=='Vietnam')
  self.assertEqual(v['publisher_count'],2)
  self.assertAlmostEqual(v['dominant_publisher_share_pct'],66.7)
  self.assertGreater(v['effective_publishers_simpson'],1)
 def test_no_unverified_mapping_and_review_candidates(self):
  rows=[self.row('Vietnam','P','Teacher training in Con Dao','https://ex.org/a',description='Vietnam local news')]
  places=[{'name':'Con Dao','level':'place'},{'name':'Con Dao','level':'place'}]
  r=report(rows,places)
  v=r['locations'][0]
  self.assertIn('Con Dao',str(v['headline_gazetteer_candidate_names']))
  self.assertEqual(v['review_samples'][0]['selected_place'],'Vietnam')
  self.assertEqual(r['policy'].startswith('Audit only'),True)
 def test_repeated_feeds_and_cross_locations(self):
  a=self.row('Kenya','P','Flooding in Kenya','https://ex.org/same?utm_source=a')
  b=self.row('Kenya','P','Flooding in Kenya','https://ex.org/same?utm_source=b')
  c=self.row('France','P','Flooding in France','https://ex.org/same')
  r=report([a,b,c],[]); k=next(x for x in r['locations'] if x['place']=='Kenya')
  self.assertEqual(k['repeated_observations'],1)
  self.assertEqual(k['review_signals']['same_url_multiple_locations'],1)
 def test_safe_with_empty_data(self):
  r=report([],[]);self.assertEqual(r['global_summary']['mapped_locations'],0)
 def test_no_mutations(self):
  a=self.row('Brazil','P','Education in Brazil','https://ex.org/one');before=repr(a)
  report([a],[{'name':'Rio de Janeiro','level':'place'}]);self.assertEqual(repr(a),before)

if __name__=='__main__': unittest.main()
