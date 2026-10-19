import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import unittest
from scripts.geo_semantic_d15 import classify,report

class D15Tests(unittest.TestCase):
 def review(self,title,selected,old='potential_headline_country_contradiction'):
  return classify(title,'',selected,{'decision':old,'contradiction_country':'Mexico'})
 def test_paris_france(self):
  self.assertEqual(self.review('Protests in France and Paris','Paris')['decision'],'hierarchy_consistent')
 def test_kyiv_ukraine(self):
  self.assertEqual(self.review('Ukraine officials gather in Kyiv','Kyiv')['decision'],'hierarchy_consistent')
 def test_toluca_mexico(self):
  self.assertEqual(self.review('Toluca, Estado de México sees heavy rain','Toluca')['decision'],'hierarchy_consistent')
 def test_santiago_chile(self):
  self.assertEqual(self.review('Chile reports protests in Santiago','Santiago')['decision'],'hierarchy_consistent')
 def test_california_usa(self):
  self.assertEqual(self.review('United States weather alert in California','California')['decision'],'hierarchy_consistent')
 def test_spanish_lakes(self):
  self.assertEqual(self.review('Los lagos de Chile attract visitors','Lagos')['decision'],'language_collision_review')
 def test_spanish_meeting(self):
  self.assertEqual(self.review('Reunión del parlamento en Madrid','Réunion')['decision'],'language_collision_review')
 def test_real_lagos_no_blanket_block(self):
  self.assertNotEqual(self.review('Lagos, Nigeria braces for floods','Lagos')['decision'],'language_collision_review')
 def test_mexico_china_still_review(self):
  self.assertEqual(self.review('Storm in Mexico','China')['decision'],'potential_contradiction_review')
 def test_multi_country_remains_review(self):
  self.assertEqual(self.review('Trade talks between France and Italy','China','multicountry_requires_review')['decision'],'multicountry_context_review')
 def test_review_balancing(self):
  rows=[{'url':str(i),'selected_place':'Vietnam','title':'x','decision':'potential_contradiction_review','d14_decision':'potential_headline_country_contradiction'} for i in range(15)]
  rows.append({'url':'other','selected_place':'Kenya','title':'y','decision':'language_collision_review','d14_decision':'no_curated_hierarchy_evidence'})
  self.assertEqual(report(rows,3)['sampled_locations'],2)
if __name__=='__main__':unittest.main()
