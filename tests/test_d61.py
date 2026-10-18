import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from publisher_metadata import publisher_for, annotate
from geographic_quality import balanced_select

class PublisherTests(unittest.TestCase):
    def test_explicit_preserved(self):
        self.assertEqual(publisher_for({'publisher':'The Hindu','url':'https://www.abc.net.au/x'},'ABC Australia','publisher')[0], 'The Hindu')
    def test_direct_feed(self):
        self.assertEqual(publisher_for({'publisher':'','url':'https://example.com/a'},'RNZ National','publisher'), ('RNZ National','direct_feed'))
    def test_direct_url_recognised(self):
        self.assertEqual(publisher_for({'publisher':'','url':'https://www.abc.net.au/news/x'},'','aggregator')[0], 'ABC News Australia')
    def test_france24_language(self):
        self.assertEqual(publisher_for({'url':'https://www.france24.com/es/video/x'},'','aggregator')[0], 'France24')
    def test_google_link_is_unresolved(self):
        self.assertEqual(publisher_for({'url':'https://news.google.com/rss/articles/abc'},'','aggregator'), ('','unresolved'))
    def test_similar_domain_not_trusted(self):
        self.assertEqual(publisher_for({'url':'https://abc.net.au.evil.example/news'},'','aggregator')[0], '')
    def test_annotation_immutable(self):
        old={'publisher':'','url':'https://www.rnz.co.nz/news/x'}
        new=annotate(old,'','aggregator')
        self.assertEqual(new['publisher'],'RNZ');self.assertEqual(old['publisher'],'')
    def test_balance_different_sources(self):
        rows=[{'publisher':annotate({'url':url})['publisher'],'url':url,'published_at':f'2026-10-18T00:00:{i:02d}+00:00'} for i,url in enumerate(['https://www.rnz.co.nz/a','https://www.abc.net.au/b','https://www.france24.com/c'])]
        _, stats = balanced_select(rows,3)
        self.assertEqual(stats['distinct_publishers'],3)

if __name__ == '__main__':unittest.main()
