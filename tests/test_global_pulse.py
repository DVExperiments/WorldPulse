"""Run with python -m unittest discover -s tests -p 'test_global_pulse.py'"""
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / 'scripts/global_pulse.py'
spec = importlib.util.spec_from_file_location('global_pulse', MODULE_PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class GlobalPulseTests(unittest.TestCase):
    def test_deduplicates_across_signals(self):
        news = {'points': [
            {'name':'France','category':'society','articles':[{'url':'https://a.com/x','publisher':'A'}]},
            {'name':'Paris','category':'politics','articles':[{'url':'https://a.com/x','publisher':'A'}]}]}
        result = m.analyze(news)
        self.assertEqual(result['overview']['distinct_mapped_preview_urls'], 1)
        self.assertEqual(len(result['categories']), 2)
    def test_removes_only_tracking_parameters(self):
        self.assertEqual(m.article_key('https://EXAMPLE.com/x?id=7&utm_source=rss'), 'https://example.com/x?id=7')
        self.assertNotEqual(m.article_key('https://example.com/x?id=7'),m.article_key('https://example.com/x?id=8'))
    def test_no_invented_geo(self):
        res = m.analyze({'points': []})
        self.assertEqual(res['overview']['distinct_mapped_preview_urls'], 0)
        self.assertEqual(res['source_diversity']['top_10_url_share'], 0)
    def test_scope_and_clusters(self):
        res = m.analyze({'points': [], 'story_clusters':[{'id':'c','coverage_status':'ongoing_coverage'}],
                         'cross_border':{'links':[{'relationship':'trade'}]}})
        self.assertEqual(res['story_groups']['statuses']['ongoing_coverage'], 1)
        self.assertEqual(res['cross_border']['types']['trade'],1)
    def test_browse_only_not_mapped(self):
        res = m.analyze({'points':[], 'unlocated_articles':[{'url':'https://x.com/1'}]})
        self.assertEqual(res['overview']['distinct_mapped_preview_urls'], 0)
        self.assertEqual(res['overview']['unlocated_browse_only_records'],1)

if __name__ == '__main__': unittest.main()
