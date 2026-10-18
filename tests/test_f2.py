import unittest,tempfile,json,sys
from pathlib import Path
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from story_tracking import enrich_story_clusters

def sample(url='https://example.org/a',publisher='Outlet A'):
 return {'story_clusters':[{'id':'f1-initial','location':'france','category':'society','label':'A protest','articles':[{'url':url,'publisher':publisher},{'url':'https://example.org/b','publisher':'Outlet B'}]}]}
class Tests(unittest.TestCase):
 def test_first_observation_is_not_surge(self):
  with tempfile.TemporaryDirectory() as d:
   b=sample();enrich_story_clusters(b,datetime(2026,10,18,tzinfo=timezone.utc),Path(d)/'history.json')
   self.assertEqual(b['story_clusters'][0]['coverage_status'],'newly_observed')
   self.assertEqual(b['story_clusters'][0]['new_publishers_since_previous_observation'],0)
 def test_stable_tracking_with_changed_cluster_id(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'history.json';t=datetime(2026,10,18,tzinfo=timezone.utc)
   b=sample();enrich_story_clusters(b,t,p);first=b['story_clusters'][0]['tracking_id']
   b=sample();b['story_clusters'][0]['id']='f1-changed';enrich_story_clusters(b,t+timedelta(hours=1),p)
   self.assertEqual(b['story_clusters'][0]['tracking_id'],first)
   self.assertEqual(b['story_clusters'][0]['coverage_status'],'ongoing_coverage')
 def test_new_unique_publisher_not_duplicate(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'history.json';t=datetime(2026,10,18,tzinfo=timezone.utc)
   enrich_story_clusters(sample(),t,p)
   b=sample();b['story_clusters'][0]['articles'].append({'url':'https://example.org/c','publisher':'Outlet C'})
   enrich_story_clusters(b,t+timedelta(hours=1),p)
   self.assertEqual(b['story_clusters'][0]['coverage_status'],'increasing_coverage')
   self.assertEqual(b['story_clusters'][0]['new_publishers_since_previous_observation'],1)
 def test_unrelated_story_not_merged(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'history.json';t=datetime(2026,10,18,tzinfo=timezone.utc)
   enrich_story_clusters(sample(),t,p)
   b=sample('https://other.org/a');b['story_clusters'][0]['articles'][1]['url']='https://other.org/b'
   enrich_story_clusters(b,t+timedelta(hours=1),p)
   self.assertEqual(b['story_clusters'][0]['coverage_status'],'newly_observed')
 def test_corrupt_history_graceful(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'history.json';p.write_text('corrupt')
   b=sample();enrich_story_clusters(b,datetime.now(timezone.utc),p)
   self.assertEqual(json.loads(p.read_text())['schema'],1)
if __name__=='__main__':unittest.main()
