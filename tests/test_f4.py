import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from cross_border import detect,publish_links

class CrossBorderTests(unittest.TestCase):
 def test_trade(self):self.assertEqual(detect('New Zealand and Australia sign new trade agreement'),(('Australia','New Zealand'),'agreement'))
 def test_no_co_mention(self):self.assertIsNone(detect('France and Germany both see heavy rainfall'))
 def test_no_sport(self):self.assertIsNone(detect('France vs Germany World Cup rugby'))
 def test_three_countries(self):self.assertIsNone(detect('Iran mediates Saudi Arabia Yemen dispute'))
 def test_incidental_diplomatic(self):self.assertIsNone(detect('Israeli settlers attack French diplomatic cars'))
 def test_one_place(self):self.assertIsNone(detect('Australia signs new investment pact'))
 def test_simple_publisher_dedup(self):
  a={'title':'New Zealand and Australia sign trade deal','url':'https://example.org/a','publisher':'A'}
  p=[{'articles':[a,a]}]
  x=publish_links(p)
  self.assertEqual(x['total_candidates'],1)
  self.assertEqual(x['links'][0]['article_count'],1)
 def test_limited_url(self):
  p=[{'articles':[{'title':'Australia and New Zealand sign trade deal','url':'javascript:hi','publisher':'P'}]}]
  self.assertEqual(publish_links(p)['total_candidates'],0)
if __name__=='__main__':unittest.main()
