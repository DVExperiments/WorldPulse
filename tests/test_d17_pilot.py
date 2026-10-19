import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_pilot_d17 import trial,benchmark,report,PILOT_ENABLED
class PilotTests(unittest.TestCase):
 def test_benchmark(self):self.assertEqual(benchmark()['failed'],0)
 def test_feature_off(self):self.assertFalse(PILOT_ENABLED)
 def test_collision(self):self.assertTrue(trial('Los lagos de Chile','Lagos','','es','withhold_for_review','language_collision_review')['eligible_for_future_pilot'])
 def test_positive_context(self):self.assertFalse(trial('Los lagos de Chile','Lagos','in Lagos, Nigeria','es','withhold_for_review','language_collision_review')['eligible_for_future_pilot'])
 def test_language_gate(self):self.assertFalse(trial('Reunión parlamentaria','Réunion','','en','withhold_for_review','language_collision_review')['eligible_for_future_pilot'])
 def test_evidence_gate(self):self.assertFalse(trial('Reunión parlamentaria','Réunion','','es','withhold_for_review','retained_independent_evidence')['eligible_for_future_pilot'])
 def test_exact_visible(self):
  r={'url':'u','selected_place':'Lagos','eligible_for_future_pilot':True,'title':'Los lagos','language':'es'}
  p=[{'name':'Lagos','category':'science','articles':[{'url':'u','title':'Los lagos'}]}]
  o=report([r,r],p);self.assertEqual(o['strict_eligible_pairs'],1);self.assertEqual(o['strict_eligible_visible_article_entries'],1)
if __name__=='__main__':unittest.main()
