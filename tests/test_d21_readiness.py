import sys,unittest,json,datetime as dt,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_readiness_d21 import evaluate

class D21Tests(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime.now(dt.timezone.utc)
  self.u='https://news.google.com/rss/articles/test?oc=5'
  self.p=[{'name':'Lagos','category':'environment','count':2,'publisher_count':2,
    'articles':[{'url':self.u,'publisher':'A','published_at':self.now.isoformat()},
               {'url':'https://good.example/story','publisher':'B','published_at':self.now.isoformat()}]}]
  self.q={'candidate_review_queue':[{'url':self.u,'place':'Lagos','title':'Spanish lakes'}]}
  self.doc={'reviews':[{'rss_url':self.u,'selected_place':'Lagos','source_url':'https://publisher.example/article',
    'evidence_summary':'Spanish lakes not city','status':'source_checked_pending_human_approval',
    'source_review_method':'AI-assisted'}]}
 def run_report(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'evidence.json';path.write_text(json.dumps(self.doc))
   return evaluate(self.p,self.q,path,self.now)
 def test_source_identified(self):self.assertEqual(self.run_report()['source_checked_visible_pairs'],1)
 def test_shadow_nonzero_removal(self):self.assertEqual(self.run_report()['hypothetical_removed_visible_articles'],1)
 def test_group_recount(self):self.assertEqual(self.run_report()['hypothetical_after_articles'],1)
 def test_no_live_filter(self):self.assertTrue(self.run_report()['live_filtering_locked'])
 def test_no_go(self):self.assertEqual(self.run_report()['readiness'],'NO_GO_live_corrections')
 def test_immutable(self):
  original=json.dumps(self.p,sort_keys=True);self.run_report();self.assertEqual(original,json.dumps(self.p,sort_keys=True))
 def test_missing_source(self):
  self.doc={'reviews':[]};self.assertEqual(len(self.run_report()['visible_candidates_without_source_review']),1)
 def test_capped_group(self):
  self.p[0]['count']=21;self.assertEqual(len(self.run_report()['blocked_groups']),1)
 def test_missing_file(self):
  r=evaluate(self.p,self.q,'/no/such/file.json',self.now);self.assertEqual(r['source_checked_visible_pairs'],0)
if __name__=='__main__':unittest.main()
