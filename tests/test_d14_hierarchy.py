import unittest
from scripts.geo_hierarchy_d14 import classify,report
class GeographyD14Test(unittest.TestCase):
 def test_mexico_locality(self):
  self.assertEqual(classify('Air pollution in Apodaca, Nuevo León','', 'Mexico','lost_after_isolation')['decision'],'supported_by_headline')
 def test_india_locality(self):
  self.assertEqual(classify('IIT Bombay students protest','', 'India','lost_after_isolation')['decision'],'supported_by_headline')
 def test_vietnam_multilingual(self):
  self.assertEqual(classify('História do Vietnã','Vietnam.vn','Vietnam','lost_after_isolation')['decision'],'supported_by_headline')
 def test_china_mexico_contradiction(self):
  r=classify('Hurricane Trudy threatens coast of Mexico','', 'China','lost_after_isolation')
  self.assertEqual(r['decision'],'potential_headline_country_contradiction')
  self.assertEqual(r['contradiction_country'],'Mexico')
 def test_multi_country_no_conflict(self):
  self.assertEqual(classify('Trade between France and Italy','', 'China','lost_after_isolation')['decision'],'multicountry_requires_review')
 def test_genuine_clean_description(self):
  self.assertEqual(classify('Education report','Floods in Nigeria', 'Nigeria','same_location_after_isolation')['decision'],'supported_by_clean_description')
 def test_unknown_not_suppressed(self):
  self.assertEqual(classify('Local festival','', 'Ghana','lost_after_isolation')['decision'],'unsupported_after_isolation')
 def test_report_global_balancing(self):
  rows=[]
  for i in range(20):rows.append({'url':f'https://a/{i}','selected_place':'Vietnam','decision':'unsupported_after_isolation','title':str(i)})
  rows.append({'url':'https://b/1','selected_place':'India','decision':'potential_headline_country_contradiction','title':'a'})
  r=report(rows,5)
  self.assertEqual(r['distinct_url_location_pairs'],21)
  self.assertIn('India',{x['selected_place'] for x in r['balanced_review_samples']})
if __name__=='__main__':unittest.main()
