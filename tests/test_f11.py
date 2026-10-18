import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from story_clustering import cluster_bundle,build_clusters,clean_headline,matching_reason
T='2026-10-18T02:30:00+00:00'
def a(title,url,publisher='A',time=T):return {'title':title,'url':'https://example.org/'+url,'publisher':publisher,'published_at':time}
def p(articles,place='France',category='society'):return {'name':place,'category':category,'articles':articles}
class Tests(unittest.TestCase):
 def test_publisher_suffix(self):self.assertEqual(clean_headline('Floods in Paris - BBC','BBC'),'Floods in Paris')
 def test_no_arbitrary_suffix(self):self.assertEqual(clean_headline('Floods in Paris - unrelated','BBC'),'Floods in Paris - unrelated')
 def test_same_publisher_exact_duplicate(self):
  out=cluster_bundle([p([a('Spain Housing Protest','a'),a('Spain Housing Protest','b'),a('Spain Housing Protest','c','B')],place='Spain')]);self.assertEqual(out['story_clusters'][0]['article_count'],2);self.assertEqual(out['cluster_diagnostics']['counts']['same_publisher_headlines_collapsed'],1)
 def test_same_publisher_distinct_coverage_remains(self):
  out=build_clusters([p([a('France parliament approves new transport law','a'),a('France parliament approves transport law amid protests','b'),a('France parliament approves transport law','c','B')])]);self.assertTrue(out);self.assertEqual(out[0]['publisher_count'],2)
 def test_no_single_publisher_group(self):self.assertEqual(build_clusters([p([a('Spain Housing Protest','a'),a('Spain Housing Protest','b')])]),[])
 def test_guarded_event_overlap(self):self.assertEqual(matching_reason('France protests over education costs school conditions clashes','France protests over school conditions and costs buildings burn'),'shared_event_terms')
 def test_topic_not_event(self):self.assertIsNone(matching_reason('France education improves school conditions for students','France education updates school conditions for teachers'))
 def test_unrelated_same_place(self):self.assertEqual(build_clusters([p([a('France students protest education costs','a'),a('France parliament debates education funding','b','B')])]),[])
 def test_separate_categories(self):self.assertEqual(build_clusters([p([a('Spain Housing Protest','a')]),p([a('Spain Housing Protest','b','B')],category='politics')]),[])
 def test_separate_locations(self):self.assertEqual(build_clusters([p([a('Spain Housing Protest','a')],place='Spain'),p([a('Spain Housing Protest','b','B')],place='Madrid')]),[])
 def test_repeatable(self):
  x=[p([a('Spain Housing Protest','a'),a('Spain Housing Protest','b','B')])];self.assertEqual(cluster_bundle(x),cluster_bundle(x))
 def test_diagnostics(self):self.assertIn('cluster_diagnostics',cluster_bundle([]))
if __name__=='__main__':unittest.main()
