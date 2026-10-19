import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_trials_d16 import simulate,benchmark,report
class D16Tests(unittest.TestCase):
 def test_collision(self):
  self.assertEqual(simulate('Los lagos de Chile','Lagos','','no_identifiable_publisher_metadata','language_collision_review')['candidate_action'],'withhold_for_review')
 def test_genuine_lagos(self):
  self.assertEqual(simulate('Flooding in Lagos, Nigeria','Lagos','','no_identifiable_publisher_metadata','retained_independent_evidence')['candidate_action'],'retain')
 def test_hierarchy_retained(self):
  self.assertEqual(simulate('IIT Bombay protest','Mumbai','','lost_after_isolation','hierarchy_consistent')['candidate_action'],'retain')
 def test_loss_review_only(self):
  self.assertEqual(simulate('Energy grid in Ukraine','Vietnam','','lost_after_isolation','potential_contradiction_review')['confidence'],'review_only')
 def test_benchmark_true_matches_untouched(self):
  b=benchmark();self.assertEqual(b['verified_true_flagged'],0);self.assertEqual(b['cases'],11)
 def test_report_dedupe(self):
  row={'url':'u','selected_place':'Lagos','title':'Los lagos de Chile','trial':'semantic_collision','candidate_action':'withhold_for_review','reason':'test'}
  r=report([row,row]);self.assertEqual(r['distinct_url_location_pairs'],1);self.assertFalse(r['safety_gates']['automatic_corrections_enabled'])
if __name__=='__main__':unittest.main()
