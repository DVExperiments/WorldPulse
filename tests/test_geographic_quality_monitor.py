import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from geographic_quality_monitor import build_monitor, update_health_file

class MonitorTests(unittest.TestCase):
    def sample(self, at='2026-10-18T09:17:52+00:00'):
        return {'updated_at': at, 'distinct_mapped_articles':410,
                'query_successes':131, 'query_attempts':136,
                'points':[{'name':'France','category':'society','count':8},
                          {'name':'Ontario','category':'community','count':1}],
                'geographic_disambiguation':{'rejected_total':19,
                    'rejected_examples':[{'place':'Rubio'}, {'place':'Rubio'}, {'place':'David'}]}}
    def test_latest(self):
        result=build_monitor(self.sample())
        self.assertEqual(result['latest']['rejected_matching_occurrences'],19)
        self.assertEqual(result['latest']['geographic_signals'],2)
    def test_flags_only(self):
        source=self.sample()
        result=build_monitor(source)
        self.assertEqual(result['ambiguous_mapped_review'][0]['name'],'Ontario')
        self.assertEqual(len(source['points']),2)
    def test_rejections_by_label(self):
        self.assertEqual(build_monitor(self.sample())['rejected_place_labels_in_examples']['Rubio'],2)
    def test_same_timestamp_idempotent(self):
        old=build_monitor(self.sample())
        new=build_monitor(self.sample(),old)
        self.assertEqual(len(new['observations']),1)
    def test_order_and_delta(self):
        early=build_monitor(self.sample('2026-10-18T08:17:52+00:00'))
        nxt=self.sample()
        nxt['points']=nxt['points'][:1]
        last=build_monitor(nxt,early)
        self.assertEqual(last['recent_change']['geographic_signals_delta'],-1)
    def test_old_pruned(self):
        old=build_monitor(self.sample('2026-01-01T09:17:52+00:00'))
        now=build_monitor(self.sample(),old)
        self.assertEqual(len(now['observations']),1)
    def test_health_preserves_other_fields(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data-health.json'
            p.write_text(json.dumps({'schema':1,'feeds_total':136}))
            update_health_file(p,self.sample())
            x=json.loads(p.read_text())
            self.assertEqual(x['feeds_total'],136)
            self.assertEqual(x['geographic_quality_monitor']['schema'],1)
    def test_invalid_timestamp(self):
        with self.assertRaises(ValueError):
            build_monitor(self.sample('not a date'))
if __name__=='__main__':unittest.main()
