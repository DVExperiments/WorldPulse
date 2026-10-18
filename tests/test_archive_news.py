import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE=Path(__file__).resolve().parents[1]/'scripts/archive_news.py'
spec=importlib.util.spec_from_file_location('archive_news',MODULE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ArchiveTests(unittest.TestCase):
    def news(self, at='2026-10-18T06:30:17+00:00'):
        return {'updated_at':at,'status':'partial','query_successes':132,'query_attempts':136,
            'distinct_mapped_articles':2,
            'points':[{'name':'France','lat':48.86,'lng':2.35,'category':'society','count':2,
                'articles':[{'title':'Example','url':'https://example.com/a','publisher':'A','published_at':at},
                {'title':'Another','url':'https://example.com/b','publisher':'B','published_at':at}]},
                {'name':'Paris','category':'society','count':1,'articles':[{'url':'https://example.com/a'}]}],
            'cross_border':{'links':[{'countries':['France','Germany'],'relationship':'trade'}]},
            'story_clusters':[{'id':'f1-a','label':'Example','publisher_count':2}]}
    def test_compact_and_url_dedupe(self):
        row=mod.compact(self.news())
        self.assertEqual(row['sampled_article_previews'],2)
        self.assertEqual(row['mapped_signals'],2)
        self.assertEqual(row['category_signal_article_counts']['society'],3)
    def test_duplicate_timestamp(self):
        with tempfile.TemporaryDirectory() as td:
            directory=Path(td)
            first,_=mod.archive(self.news(),directory,today=dt.date(2026,10,18))
            second,index=mod.archive(self.news(),directory,today=dt.date(2026,10,18))
            self.assertTrue(first)
            self.assertFalse(second)
            self.assertEqual(index['snapshots_total'],1)
    def test_second_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            directory=Path(td)
            mod.archive(self.news(),directory,today=dt.date(2026,10,18))
            new,index=mod.archive(self.news('2026-10-18T07:00:00+00:00'),directory,today=dt.date(2026,10,18))
            self.assertTrue(new)
            self.assertEqual(index['snapshots_total'],2)
    def test_stale_rejected(self):
        bad=self.news();bad['status']='stale'
        with self.assertRaises(ValueError):mod.compact(bad)
    def test_no_corrupt_on_failed_input(self):
        with tempfile.TemporaryDirectory() as td:
            directory=Path(td)
            mod.archive(self.news(),directory,today=dt.date(2026,10,18))
            original=(directory/'2026-10-18.json').read_bytes()
            bad=self.news();bad['updated_at']='not-a-date'
            with self.assertRaises(ValueError):mod.archive(bad,directory,today=dt.date(2026,10,18))
            self.assertEqual(original,(directory/'2026-10-18.json').read_bytes())
    def test_retention(self):
        with tempfile.TemporaryDirectory() as td:
            directory=Path(td)
            mod.archive(self.news('2026-10-17T06:30:17+00:00'),directory,today=dt.date(2026,10,18),retention_days=2)
            self.assertTrue((directory/'2026-10-17.json').exists())
            mod.archive(self.news(),directory,today=dt.date(2026,10,19),retention_days=2)
            self.assertFalse((directory/'2026-10-17.json').exists())
    def test_future_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):mod.archive(self.news('2026-10-22T00:00:00+00:00'),Path(td),today=dt.date(2026,10,18))

if __name__=='__main__': unittest.main()
