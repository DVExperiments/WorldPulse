import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from publisher_network import NEW_FEEDS,merge_feeds
class PublisherNetworkTests(unittest.TestCase):
 def test_unique_config(self):
  self.assertEqual(len(NEW_FEEDS),len({p[0].casefold() for p in NEW_FEEDS}))
  self.assertTrue(all(p[1].startswith('https://') for p in NEW_FEEDS))
  self.assertTrue(all(len(p)==4 for p in NEW_FEEDS))
 def test_merge_skips_existing(self):
  first=merge_feeds([NEW_FEEDS[0]])
  self.assertEqual(len(first),len(NEW_FEEDS))
  self.assertEqual(len(merge_feeds(first)),len(first))
 def test_regions_languages(self):
  self.assertIn('africa',{x[2] for x in NEW_FEEDS})
  self.assertIn('oceania',{x[2] for x in NEW_FEEDS})
  self.assertIn('south-america',{x[2] for x in NEW_FEEDS})
  self.assertTrue({'fr','es','pt','id'}.issubset({x[3] for x in NEW_FEEDS}))
if __name__=='__main__':unittest.main()
