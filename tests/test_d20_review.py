import sys,unittest,datetime as dt,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_review_d20 import *
class TestD20(unittest.TestCase):
 def setUp(self):self.now=dt.datetime(2026,10,19,tzinfo=dt.timezone.utc)
 def record(self):
  return dict(url='https://example.com/story',place='Lagos',rule='spanish_lagos_lakes',reviewer='Human Reviewer',reviewed_at=self.now.isoformat(),article_access='full_article',source_evidence='Full source discusses lakes in Chile with no Nigerian material.',location_evidence='No Lagos Nigeria reference is contained in the full source article.',conclusion='confirmed_false_match',source_url='https://example.com/story',source_title='Los lagos de Chile',independent_geography_check=True)
 def test_review(self):self.assertIsNone(validate_review(self.record()))
 def test_review_no_full_article(self):
  r=self.record();r['article_access']='rss_only';self.assertEqual(validate_review(r),'full_article_required')
 def test_review_no_secondary_check(self):
  r=self.record();r['independent_geography_check']=False;self.assertEqual(validate_review(r),'independent_check_required')
 def test_review_wrong_place(self):
  r=self.record();r['place']='Réunion';self.assertEqual(validate_review(r),'incorrect_rule_place')
 def test_review_no_evidence(self):
  r=self.record();r['source_evidence']='no';self.assertEqual(validate_review(r),'insufficient_documented_evidence')
 def test_drill(self):self.assertTrue(fixture_drill(self.now)['passed'])
 def test_real_no_review(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'review.json';p.write_text('{"schema":1,"reviews":[]}')
   x=[{'name':'Lagos','category':'environment','count':1,'articles':[{'url':'https://example.com/story'}]}]
   rs=[{'url':'https://example.com/story','selected_place':'Lagos','eligible_for_future_pilot':True,'candidate_action':'eligible_shadow_withhold'}]
   report=evaluate(x,rs,p,self.now)
   self.assertEqual(report['hypothetical_removed_visible_articles'],0);self.assertEqual(report['candidate_visible_entries'],1)
 def test_valid_review_simulation(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'review.json';p.write_text(json.dumps({'schema':1,'reviews':[self.record()]}))
   x=[{'name':'Lagos','category':'environment','count':1,'articles':[{'url':'https://example.com/story','published_at':self.now.isoformat(),'publisher':'P'}]}]
   rs=[{'url':'https://example.com/story','selected_place':'Lagos','eligible_for_future_pilot':True,'candidate_action':'eligible_shadow_withhold'}]
   r=evaluate(x,rs,p,self.now)
   self.assertEqual(r['hypothetical_removed_visible_articles'],1)
   self.assertEqual(r['hypothetical_after_signal_groups'],0)
 def test_capped_protected(self):
  t=self.now.isoformat();x=[{'name':'Réunion','category':'politics','count':21,'articles':[{'url':'https://example.com/a','published_at':t}]}]
  r=rebuild(x,{pair('https://example.com/a','Réunion')},self.now)
  self.assertEqual(r['projected_removed'],[]);self.assertEqual(len(r['blocked_groups']),1)
if __name__=='__main__':unittest.main()
