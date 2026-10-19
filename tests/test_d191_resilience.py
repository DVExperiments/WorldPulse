import sys,unittest,datetime as dt,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from feed_resilience_d191 import assess_outage,retry_open

class ResilienceTests(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime(2026,10,19,6,tzinfo=dt.timezone.utc)
  self.old={'status':'partial','updated_at':'2026-10-19T05:00:00+00:00','points':[{'articles':[{}]*20} for _ in range(30)]}
  self.fail=[{'kind':'aggregator','status':'failed'} for _ in range(121)]+[{'kind':'publisher','status':'ok'} for _ in range(49)]
 def test_catastrophic_google_failures_block(self):self.assertTrue(assess_outage(self.fail,self.old,now=self.now)['publication_blocked'])
 def test_successful_google_no_block(self):
  health=[{'kind':'aggregator','status':'ok'} for _ in range(121)]
  self.assertFalse(assess_outage(health,self.old,now=self.now)['publication_blocked'])
 def test_no_healthy_baseline_no_block(self):self.assertFalse(assess_outage(self.fail,{'points':[]},now=self.now)['publication_blocked'])
 def test_old_baseline_no_block(self):
  self.old['updated_at']='2026-10-15T05:00:00+00:00'
  self.assertFalse(assess_outage(self.fail,self.old,now=self.now)['publication_blocked'])
 def test_publisher_outage_no_block(self):
  health=[{'kind':'aggregator','status':'ok'} for _ in range(121)]+[{'kind':'publisher','status':'failed'} for _ in range(49)]
  self.assertFalse(assess_outage(health,self.old,now=self.now)['publication_blocked'])
 def test_retry_503_then_success(self):
  calls=[];sleeps=[]
  def opener(req,timeout):
   calls.append(1)
   if len(calls)<3:raise urllib.error.HTTPError('https://example.org',503,'fail',{},None)
   return 'ok'
  self.assertEqual(retry_open(None,opener,sleep=sleeps.append,random_value=lambda:0),'ok')
  self.assertEqual(len(calls),3);self.assertEqual(len(sleeps),2)
 def test_no_retry_404(self):
  calls=[]
  def opener(req,timeout):
   calls.append(1);raise urllib.error.HTTPError('https://example.org',404,'fail',{},None)
  with self.assertRaises(urllib.error.HTTPError):retry_open(None,opener,sleep=lambda _:None)
  self.assertEqual(len(calls),1)
 def test_retry_limit(self):
  calls=[]
  def opener(req,timeout):
   calls.append(1);raise urllib.error.HTTPError('https://example.org',503,'fail',{},None)
  with self.assertRaises(urllib.error.HTTPError):retry_open(None,opener,sleep=lambda _:None)
  self.assertEqual(len(calls),3)
if __name__=='__main__':unittest.main()
