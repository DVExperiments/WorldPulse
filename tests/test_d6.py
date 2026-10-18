import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geographic_quality import curated_match,balanced_select
class QualityTests(unittest.TestCase):
 def test_explicit_place(self):
  self.assertEqual(curated_match('Hospitals planned in Gujarat')[0]['name'],'Gujarat')
 def test_not_publisher_origin(self):
  self.assertIsNone(curated_match('Healthcare crisis', 'No clear geographical reference')[0])
 def test_caution_multiple_places(self):
  self.assertIsNone(curated_match('Gujarat and West Bengal collaborate')[0])
 def test_word_boundary(self):
  self.assertIsNone(curated_match('Bozemanite tradition discussed')[0])
 def test_accent(self):
  self.assertEqual(curated_match('Whangārei weather')[0]['name'],'Whangārei')
 def test_balance(self):
  rows=[{'title':str(i),'published_at':f'2026-10-18T00:{i:02d}:00+00:00','url':f'https://example.org/{i}','publisher':'Dominant' if i<25 else 'Small'} for i in range(40)]
  selected,stats=balanced_select(rows,20,5)
  self.assertEqual(len(selected),20)
  self.assertGreaterEqual(sum(r['publisher']=='Small' for r in selected),5)
  self.assertEqual(stats['distinct_publishers'],2)
if __name__=='__main__':unittest.main()
