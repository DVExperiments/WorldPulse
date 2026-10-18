import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_expansion import expanded_match,inspect_unmatched,ROWS
class ExpansionTests(unittest.TestCase):
 def test_size(self):self.assertGreaterEqual(len(ROWS),130)
 def test_explicit(self):self.assertEqual(expanded_match('Earthquake shakes Tigray')[0]['name'],'Tigray')
 def test_france_alias(self):self.assertEqual(expanded_match('Manifestations en Catalogne')[0]['name'],'Catalonia')
 def test_accent(self):self.assertEqual(expanded_match('Incidents in São Paulo')[0]['name'],'São Paulo')
 def test_word_boundary(self):self.assertIsNone(expanded_match('Sabulous conditions')[0])
 def test_ambiguous(self):
  place,reason=expanded_match('Kudat and Sabah sign agreement')
  self.assertIsNone(place);self.assertEqual(reason,'ambiguous-expanded')
 def test_title_preferred(self):self.assertEqual(expanded_match('Meeting in Goma','Report from Kigali')[0]['name'],'Goma')
 def test_no_publisher_inference(self):self.assertIsNone(expanded_match('Government announces changes','News report')[0])
 def test_url_not_used(self):self.assertIsNone(expanded_match('Economy grows','https://example.org/khartoum')[0])
 def test_samples(self):
  report={'examples':[{'title':'Kisoro hospital construction delayed'},{'title':'The science of hope'}]}
  self.assertEqual(inspect_unmatched(report)['recoverable_sample_count'],1)
if __name__=='__main__':unittest.main()
