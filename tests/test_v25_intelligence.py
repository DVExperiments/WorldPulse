import unittest,sys,datetime as dt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from intelligence_v25 import canonical_url,quality_report,shadow_consistency,validate_snapshot,fingerprint

class V25(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime.now(dt.timezone.utc)
  self.article={'url':'https://example.org/news','title':'Example','published_at':self.now.isoformat(),'publisher':'X'}
  self.points=[{'name':'Lagos','category':'environment','count':1,'publisher_count':1,'articles':[self.article]}]
  self.evidence={'publisher_source_reviews':[{'rss_url':'https://example.org/news','selected_place':'Lagos','source_checked_pending_human_approval':True,'human_approved':False}]}
 def test_url_tracking_normalization(self):self.assertEqual(canonical_url('https://EXAMPLE.org/news/?utm_source=a&id=1'), 'https://example.org/news?id=1')
 def test_shadow_is_immutable(self):
  before=fingerprint(self.points)
  out=shadow_consistency(self.points,self.evidence,self.now,lambda x:{'groups':len(x)},lambda x:{'links':0})
  self.assertTrue(out['passed']);self.assertEqual(out['projected_removed'],1);self.assertEqual(before,fingerprint(self.points));self.assertEqual(out['readiness'],'NO_GO_live_corrections')
 def test_capped_group_blocks(self):
  self.points[0]['count']=21
  out=shadow_consistency(self.points,self.evidence,self.now,lambda x:{'groups':len(x)},lambda x:{'links':0})
  self.assertEqual(out['projected_removed'],0);self.assertEqual(out['blocked_group_count'],1)
 def test_builder_failure_visible(self):
  def crash(x):raise ValueError('bad')
  out=shadow_consistency(self.points,self.evidence,self.now,crash,lambda x:{})
  self.assertFalse(out['passed']);self.assertEqual(out['derived_builders']['story_cluster_builder']['status'],'blocked_builder_error')
 def test_feed_and_publisher_report(self):
  raw=[{'place':{'name':'Lagos'},'publisher':'X','geo_match':'headline'},{'place':{'name':'Lagos'},'publisher':'X','geo_match':'description'}]
  feeds={'a':{'status':'ok','kind':'aggregator','parsed_entries':0},'b':{'status':'failed','kind':'publisher','parsed_entries':0}}
  out=quality_report(raw,self.points,feeds,[],{},self.now)
  self.assertEqual(out['feeds_successful_empty_by_kind']['aggregator'],1)
  self.assertEqual(out['feeds_failed_by_kind']['publisher'],1)
  self.assertTrue(out['baseline_unchanged'])
 def test_validator(self):
  a=validate_snapshot({'points':self.points},{'totals':{'globe_articles':1}},{})
  self.assertTrue(a['ok'])
  self.points[0]['count']=0
  self.assertFalse(validate_snapshot({'points':self.points},{'totals':{'globe_articles':1}},{} )['ok'])
 def test_no_evidence(self):
  out=shadow_consistency(self.points,{},self.now,lambda x:{},lambda x:{})
  self.assertEqual(out['projected_removed'],0)

if __name__=='__main__':unittest.main()
