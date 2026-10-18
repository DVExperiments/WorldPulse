import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_public_evidence import public_evidence
class E4Tests(unittest.TestCase):
 def test_explicit(self):
  row={'title':'Protests in Bihar','description':'','geo_match':'headline','place':{'name':'Bihar','level':'region'}}
  p=public_evidence(row);self.assertEqual(p['evidence_class'],'explicit_headline');self.assertFalse(p['event_location_verified']);self.assertEqual(p['location_precision'],'region')
 def test_description(self):
  row={'title':'Local politics','description':'News in Bihar','geo_match':'description','place':{'name':'Bihar','level':'region'}}
  self.assertEqual(public_evidence(row)['evidence_class'],'description_context')
 def test_heuristic(self):
  row={'title':'Economic news','description':'','geo_match':'unknown','place':{'name':'France'}}
  self.assertIn(public_evidence(row)['evidence_class'],['other_heuristic','explicit_headline'])
 def test_no_incident_verification(self):
  row={'title':'France protests','description':'','geo_match':'headline','place':{'name':'France'}}
  self.assertFalse(public_evidence(row)['event_location_verified'])
if __name__=='__main__':unittest.main()
