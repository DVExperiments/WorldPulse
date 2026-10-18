import unittest,sys,tempfile,json,datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_confidence import classify,build,publish_confidence

class EvidenceTests(unittest.TestCase):
 def row(self,title='Bihar government plan',method='description',place='Patna',description=''):
  return {'title':title,'description':description,'geo_match':method,'place':{'name':place},'publisher':'Demo','url':'https://example.org/story'}
 def test_headline(self):self.assertEqual(classify(self.row(method='headline'))['evidence_class'],'explicit_headline')
 def test_corrected(self):self.assertEqual(classify(self.row(method='headline-reviewed-correction'))['evidence_class'],'explicit_headline')
 def test_description(self):self.assertEqual(classify(self.row(title='University policy',method='description'))['evidence_class'],'description_context')
 def test_conflict(self):self.assertEqual(classify(self.row())['evidence_class'],'conflicting_evidence')
 def test_ambiguous(self):self.assertEqual(classify(self.row(title='Bihar and Gujarat discuss changes',method='headline'))['evidence_class'],'ambiguous_headline')
 def test_url(self):self.assertEqual(classify(self.row(title='University policy',method='url-explicit-place'))['evidence_class'],'url_context')
 def test_missing_catalogue_not_watch(self):
  result=classify(self.row(title='School policy update',method='other',place='Somewhere'))
  self.assertEqual(result['evidence_class'],'other_heuristic')
 def test_not_verified(self):self.assertFalse(classify(self.row())['event_location_verified'])
 def test_summary(self):
  x=build([self.row(method='headline'),self.row(method='description')],datetime.datetime.now(datetime.timezone.utc))
  self.assertEqual(sum(x['evidence_classes'].values()),2)
 def test_publish(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'unmatched-review.json';p.write_text('{"existing":42}')
   publish_confidence([self.row()],datetime.datetime.now(datetime.timezone.utc),d)
   content=json.loads(p.read_text());self.assertEqual(content['existing'],42)
   self.assertIn('geo_confidence_evidence',content)
if __name__=='__main__':unittest.main()
