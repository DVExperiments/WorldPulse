import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from geographic_disambiguation import evaluate

class DisambiguationTests(unittest.TestCase):
    def test_surname_rejected(self):
        self.assertFalse(evaluate({'name':'Rubio'}, 'Rubio says sanctions could be delayed')[0])
    def test_place_referenced_directly(self):
        self.assertTrue(evaluate({'name':'Rubio'}, 'Mayor in Rubio announces a new school')[0])
    def test_speaking_to_person_rejected(self):
        self.assertFalse(evaluate({'name':'David'}, 'Officials spoke to David')[0])
    def test_country_qualifier(self):
        self.assertTrue(evaluate({'name':'David'}, 'Flooding in David, Panama')[0])
    def test_common_word_rejected(self):
        self.assertFalse(evaluate({'name':'Forest'}, 'Forest fires threaten wildlife')[0])
    def test_town_qualifier(self):
        self.assertTrue(evaluate({'name':'Forest'}, 'Town of Forest opens library')[0])
    def test_person_name_rejected(self):
        self.assertFalse(evaluate({'name':'David'}, 'David speaks on marine energy')[0])
    def test_explicit_city_accepted(self):
        self.assertTrue(evaluate({'name':'David'}, 'Flooding near David forces evacuations')[0])
    def test_description_context(self):
        self.assertTrue(evaluate({'name':'Union'}, 'Local report', 'Residents in Union protest closure')[0])
    def test_neutral_pass(self):
        self.assertTrue(evaluate({'name':'France'}, 'France protests continue')[0])
    def test_no_name(self):
        self.assertTrue(evaluate({'name':''}, 'Report')[0])
    def test_no_context(self):
        self.assertFalse(evaluate({'name':'Sunrise'}, 'Sunrise brings hope')[0])

if __name__ == '__main__': unittest.main()
