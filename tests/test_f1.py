import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from story_clustering import build_clusters,similarity
T='2026-10-18T02:30:00+00:00'
def a(title,url,publisher='A',time=T):return {'title':title,'url':'https://example.org/'+url,'publisher':publisher,'published_at':time}
def point(articles,place='Paris',category='politics'):return {'name':place,'category':category,'articles':articles}
class ClusterTests(unittest.TestCase):
 def test_similar_sources(self):
  p=point([a('France parliament approves new transport law','1'),a('France parliament approves transport law amid protests','2','B')]);g=build_clusters([p]);self.assertEqual(len(g),1);self.assertEqual(g[0]['publisher_count'],2)
 def test_different_place(self):
  p=[point([a('France parliament approves new transport law','1')]),point([a('France parliament approves transport law amid protests','2','B')],place='Lyon')];self.assertEqual(build_clusters(p),[])
 def test_different_category(self):
  p=[point([a('France parliament approves new transport law','1')]),point([a('France parliament approves transport law amid protests','2','B')],category='economy')];self.assertEqual(build_clusters(p),[])
 def test_same_publisher_not_clustered(self):
  p=point([a('France parliament approves new transport law','1'),a('France parliament approves transport law amid protests','2')]);self.assertEqual(build_clusters([p]),[])
 def test_age_limit(self):
  p=point([a('France parliament approves new transport law','1'),a('France parliament approves transport law amid protests','2','B','2026-10-15T02:30:00+00:00')]);self.assertEqual(build_clusters([p]),[])
 def test_distinct_story(self):
  p=point([a('France parliament approves new transport law','1'),a('France parliament debates education funding plans','2','B')]);self.assertEqual(build_clusters([p]),[])
 def test_deduped_url(self):
  p=point([a('France parliament approves new transport law','1'),a('France parliament approves transport law amid protests','1','B')]);self.assertEqual(build_clusters([p]),[])
 def test_deterministic(self):
  p=point([a('France parliament approves new transport law','1'),a('France parliament approves transport law amid protests','2','B')]);self.assertEqual(build_clusters([p]),build_clusters([p]))
 def test_short_title(self):self.assertEqual(similarity('War today','War here'),0)
if __name__=='__main__':unittest.main()
