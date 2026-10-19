import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_anomaly_d10 import report,headline_evidence

class D10(unittest.TestCase):
 def make(self,title,description,url,place='Vietnam',feed='a'):
  return {'title':title,'description':description,'url':url,'place':{'name':place},'audit_feed_key':feed,'source_region':'US','publisher':'Sample','geo_match':'gazetteer'}
 def test_description_only_and_source_not_location(self):
  a=self.make('US election updates','Vietnam mentioned in unrelated background','https://example.com/1')
  r=report([a]);loc=next(x for x in r['locations'] if x['place']=='Vietnam')
  self.assertEqual(loc['evidence_levels']['explicit_description_place'],1)
  self.assertEqual(loc['review_signals']['description_only_selected_place'],1)
  self.assertIn('source_editorial_regions',loc)
 def test_feed_duplicate_and_multiple_locations(self):
  a=self.make('Talks in Vietnam','report','https://example.com/a?tracking=2')
  b=self.make('Talks in Vietnam','report','https://example.com/a?tracking=3',feed='b')
  c=self.make('Talks in Vietnam','report','https://example.com/a',place='France')
  r=report([a,b,c]);self.assertEqual(r['distinct_url_location_pairs'],2)
  v=next(x for x in r['locations'] if x['place']=='Vietnam')
  self.assertEqual(v['duplicate_feed_observations'],1)
  self.assertEqual(v['review_signals']['same_url_multiple_selected_places'],1)
 def test_location_cue(self):
  self.assertEqual(headline_evidence('Flooding in Vietnam','Vietnam'),'preposition_locality_cue')
  self.assertEqual(headline_evidence('Vietnam to host summit','Vietnam'),'name_in_headline_no_locality_cue')
 def test_no_mutation(self):
  a=self.make('Floods in Vietnam','','https://example.com/4');before=repr(a)
  self.assertEqual(report([a])['policy'].startswith('Audit-only'),True)
  self.assertEqual(repr(a),before)

if __name__=='__main__':unittest.main()
