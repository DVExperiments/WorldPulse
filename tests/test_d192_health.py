import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from feed_health_d192 import classify_feed,feed_breakdown,run_frozen_drills,build_report,canonical_fingerprint

class FeedHealthTests(unittest.TestCase):
 def setUp(self): self.now=dt.datetime(2026,10,19,6,tzinfo=dt.timezone.utc)
 def test_transport_failure(self): self.assertEqual(classify_feed({'status':'failed','items':0}),'transport_failure')
 def test_successful_empty(self): self.assertEqual(classify_feed({'status':'ok','items':0}),'successful_empty')
 def test_successful_nonempty(self): self.assertEqual(classify_feed({'status':'ok','items':3}),'successful_nonempty')
 def test_missing_items_not_empty(self): self.assertEqual(classify_feed({'status':'ok'}),'unknown_item_count')
 def test_boolean_not_count(self): self.assertEqual(classify_feed({'status':'ok','items':False}),'unknown_item_count')
 def test_feed_counts(self):
  data=[{'kind':'aggregator','status':'ok','items':0,'source':'a'}, {'kind':'aggregator','status':'failed','items':0,'source':'b','error':'503'}, {'kind':'publisher','status':'ok','items':4,'source':'c'}]
  out=feed_breakdown(data);self.assertEqual(out['aggregator']['successful_empty'],1);self.assertEqual(out['aggregator']['transport_failure'],1);self.assertEqual(out['publisher']['successful_nonempty'],1)
 def test_drills_all_pass(self): self.assertTrue(run_frozen_drills(now=self.now)['passed'])
 def test_expected_catastrophic_block(self): self.assertTrue(next(d for d in run_frozen_drills(now=self.now)['scenarios'] if d['scenario']=='catastrophic_google_503')['actual_publication_blocked'])
 def test_empty_google_not_transport_outage(self): self.assertFalse(next(d for d in run_frozen_drills(now=self.now)['scenarios'] if d['scenario']=='successful_but_empty_google')['actual_publication_blocked'])
 def test_expired_baseline_not_protected(self): self.assertFalse(next(d for d in run_frozen_drills(now=self.now)['scenarios'] if d['scenario']=='expired_snapshot_not_preserved')['actual_publication_blocked'])
 def test_report_shape(self):
  r=build_report([{'kind':'aggregator','status':'ok','items':0}],{},now=self.now)
  self.assertEqual(r['release'],'v2.4D.19.2');self.assertIn('frozen_outage_drills',r)
 def test_fingerprint_key_independent(self): self.assertEqual(canonical_fingerprint({'a':1,'b':2}),canonical_fingerprint({'b':2,'a':1}))
if __name__=='__main__':unittest.main()
