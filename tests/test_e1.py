import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_accuracy_audit import examine,build_audit,mentioned_places
from datetime import datetime,timezone

CAT=[('France',['france']),('Germany',['germany']),('Gujarat',['gujarat'])]
class AccuracyAuditTests(unittest.TestCase):
    def article(self,title='',description='',method='headline',chosen='France'):
        return {'title':title,'description':description,'geo_match':method,'place':{'name':chosen},'publisher':'Test','url':'https://example.com/article'}
    def test_single_place(self):
        r=examine(self.article('Protests in France'),CAT)
        self.assertEqual(r['risk_band'],'low')
    def test_two_places(self):
        r=examine(self.article('France and Germany hold talks'),CAT)
        self.assertIn('multiple_reviewed_headline_places',r['flags'])
        self.assertEqual(r['risk_band'],'review_priority')
    def test_description_override(self):
        r=examine(self.article('Gujarat announces reform','France is also cited','description',chosen='France'),CAT)
        self.assertEqual(r['risk_band'],'review_priority')
    def test_description_only(self):
        r=examine(self.article('New climate policy','France proposes action','description'),CAT)
        self.assertIn('description_only_selection',r['flags'])
    def test_no_publisher_location_inference(self):
        r=examine(self.article('New climate policy','New initiatives','headline'),CAT)
        self.assertEqual(r['headline_places'],[])
    def test_url_doesnt_add_place(self):
        a=self.article('New policy','',chosen='France');a['url']='https://example.com/france'
        self.assertEqual(examine(a,CAT)['headline_places'],[])
    def test_accent_folding(self):
        self.assertEqual(mentioned_places('In Français café in FRANCE',CAT),['France'])
    def test_count(self):
        r=build_audit([self.article('Gujarat and West Bengal',chosen='Gujarat'),self.article('Gujarat',chosen='Gujarat')],datetime.now(timezone.utc))
        self.assertEqual(r['mapped_occurrences_audited'],2)
        self.assertEqual(r['risk_bands']['review_priority'],1)
    def test_no_event_claim(self):
        r=build_audit([],datetime.now(timezone.utc))
        self.assertIn('never verified event sites',r['limitations'])
if __name__=='__main__':unittest.main()
