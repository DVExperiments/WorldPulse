import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from intelligence_v26 import lexical_collision,dedup_diagnostics,build_report
import datetime as dt
class QualityV26Tests(unittest.TestCase):
 def test_meeting(self):self.assertTrue(lexical_collision({'name':'Réunion'},'Ignacio Mier ve viable reunión interparlamentaria con Estados Unidos','Legisladores de México'))
 def test_island_exempt(self):self.assertIsNone(lexical_collision({'name':'Réunion'},'Reunión parlamentaria en la isla de la Reunión',''))
 def test_lakes(self):self.assertTrue(lexical_collision({'name':'Lagos'},'Catorce lagos del sur de Chile podrían contar con nuevas normas ambientales',''))
 def test_nigeria_exempt(self):self.assertIsNone(lexical_collision({'name':'Lagos'},'Lagos state passes environmental rules','Nigeria'))
 def test_not_other_location(self):self.assertIsNone(lexical_collision({'name':'Mexico City'},'Reunión interparlamentaria',''))
 def test_other_reunion(self):self.assertIsNone(lexical_collision({'name':'Réunion'},'Reunion volcano alerts',''))
 def test_dedup(self):
  x=dedup_diagnostics([{'url':'https://a.test/a?utm_source=x','place':{'name':'X'}},{'url':'https://a.test/a','place':{'name':'X'}},{'url':'https://a.test/a','place':{'name':'Y'}}]);self.assertEqual((x['canonical_same_place_repeats'],x['cross_place_url_occurrences']),(1,1))
 def test_empty_report(self):self.assertEqual(build_report([],[],[],dt.datetime.now(dt.timezone.utc),[],{'runs':[]})['lexical_suppressed_total'],0)
if __name__=='__main__':unittest.main()
