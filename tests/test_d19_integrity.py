import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_integrity_d19 import simulate,load_reviews

class D19Test(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'review.json'
  self.p=[{'name':'Lagos','category':'environment','count':2,'publisher_count':2,'recent_3h':1,'previous_3h':1,'articles':[{'url':'https://example.com/wrong','title':'Los lagos de Chile','publisher':'A'},{'url':'https://example.com/real','title':'Lagos Nigeria','publisher':'B'}]}]
  self.rows=[{'url':'https://example.com/wrong','selected_place':'Lagos','eligible_for_future_pilot':True,'candidate_action':'eligible_shadow_withhold'}]
 def tearDown(self):self.tmp.cleanup()
 def write(self,reviews):self.path.write_text(json.dumps({'schema':1,'reviews':reviews}),encoding='utf8')
 def review(self,**kw):return dict(url='https://example.com/wrong',place='Lagos',rule='spanish_lagos_lakes',reviewer='Reviewer A',reviewed_at='2026-10-19',article_access='full_article',source_evidence='Article text mentions Chile lakes only',location_evidence='No reference to Lagos Nigeria',conclusion='confirmed_false_match',**kw)
 def test_empty_review_never_removes(self):
  self.write([]);b=copy.deepcopy(self.p);r=simulate(self.p,self.rows,self.path)
  self.assertEqual(r['hypothetical_confirmed_removals'],0);self.assertEqual(self.p,b);self.assertTrue(r['rollback_identical'])
 def test_review_removes_only_wrong_example_from_hypothesis(self):
  self.write([self.review()]);r=simulate(self.p,self.rows,self.path)
  self.assertEqual(r['hypothetical_confirmed_removals'],1);self.assertEqual(r['after_hypothetical_serialized_articles'],1);self.assertEqual(r['before_groups'],1);self.assertEqual(r['after_hypothetical_groups'],1)
 def test_entire_group_disappearance(self):
  self.write([self.review()]);self.p[0]['articles']=self.p[0]['articles'][:1];self.p[0]['count']=1
  r=simulate(self.p,self.rows,self.path);self.assertEqual(r['after_hypothetical_groups'],0);self.assertEqual(len(r['groups_disappearing']),1)
 def test_capped_group_never_hypothetically_drops(self):
  self.write([self.review()]);self.p[0]['count']=21
  r=simulate(self.p,self.rows,self.path);self.assertEqual(r['unsafe_capped_groups'],1);self.assertEqual(r['hypothetical_confirmed_removals'],0);self.assertEqual(r['after_hypothetical_serialized_articles'],2)
 def test_rss_only_cannot_confirm(self):
  row=self.review();row['article_access']='rss_only';self.write([row]);r=simulate(self.p,self.rows,self.path)
  self.assertEqual(r['review_records_loaded'],0);self.assertTrue(r['review_validation_issues'])
 def test_not_eligible_even_if_reviewed(self):
  self.write([self.review()]);r=simulate(self.p,[],self.path);self.assertEqual(r['hypothetical_confirmed_removals'],0)
 def test_invalid_rule_rejected(self):
  row=self.review();row['rule']='anywhere';self.write([row]);review,issues=load_reviews(self.path);self.assertFalse(review);self.assertTrue(issues)
 def test_rollback_and_input_preservation(self):
  self.write([self.review()]);b=copy.deepcopy(self.p);r=simulate(self.p,self.rows,self.path);self.assertEqual(self.p,b);self.assertTrue(r['rollback_identical']);self.assertTrue(r['caller_input_unchanged'])
if __name__=='__main__':unittest.main()
