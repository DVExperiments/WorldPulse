import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_decision import DecisionAudit

class DecisionTests(unittest.TestCase):
 def setUp(self):self.audit=DecisionAudit()
 def choose(self,title,where='Patna',method='description'):
  return self.audit.decide({'title':title,'publisher':'A','url':'https://example.org/test'}, {'name':where,'lat':25,'lng':85,'level':'place'},method)
 def test_bihar(self):
  p,m=self.choose('Bihar Government Plans AI Policy For Universities');self.assertEqual((p['name'],m),('Bihar','headline-reviewed-correction'))
 def test_west_bank(self):
  p,m=self.choose('Cisjordanie occupée : des colons attaquent un convoi diplomatique','Israel','description-normalized');self.assertEqual((p['name'],m),('West Bank','headline-reviewed-correction'))
 def test_headline_unchanged(self):self.assertEqual(self.choose('Bihar government',method='headline')[1],'headline')
 def test_no_place(self):self.assertEqual(self.choose('University policy debated')[0]['name'],'Patna')
 def test_agrees(self):self.assertEqual(self.choose('Bihar government',where='Bihar')[1],'description')
 def test_multiple_withheld(self):self.assertEqual(self.choose('Bihar and Gujarat discuss AI research')[0]['name'],'Patna')
 def test_no_publisher_inference(self):self.assertEqual(self.choose('Education policy update')[0]['name'],'Patna')
 def test_west_bank_subject_is_not_event_site(self):self.assertNotIn('event_location_verified',self.choose('Cisjordanie occupée',where='Israel')[0])
 def test_counters(self):
  self.choose('Bihar Government Plans AI Policy');self.assertEqual(self.audit.counts['corrected_to_explicit_headline_place'],1)
if __name__=='__main__':unittest.main()
