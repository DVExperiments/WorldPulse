import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_mapping_enhancements import find_explicit
P=[{'name':'Whangarei','lat':-35.7,'lng':174.3},{'name':'Auckland','lat':-36.8,'lng':174.7}, {'name':'Nice','lat':43.7,'lng':7.2},{'name':'Paris','lat':48.85,'lng':2.3}]
class MappingTests(unittest.TestCase):
 def test_diacritics(self):
  p,origin=find_explicit('Whangārei floods','', '',P)
  self.assertEqual(p['name'],'Whangarei')
 def test_url_positive(self):
  p,_=find_explicit('Council votes', '', 'https://example.org/news/city/auckland',P)
  self.assertEqual(p['name'],'Auckland')
 def test_unrelated_url(self):
  p,_=find_explicit('Council votes', '', 'https://auckland.example.org/news/council',P)
  self.assertIsNone(p)
 def test_ambiguity_guard(self):
  p,_=find_explicit('Nice new study', '', '',P)
  self.assertIsNone(p)
if __name__=='__main__':unittest.main()
