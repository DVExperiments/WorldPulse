import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'cross_border.py'
spec = importlib.util.spec_from_file_location('cross_border',PATH)
mod = importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class TestF45(unittest.TestCase):
 def test_waiver(self):
  self.assertEqual(mod.relationship_details("US Sanctions Waiver: Relief for India's Energy & Exporters",'sanctions')[0],'sanctions_waiver')
 def test_pause(self):
  self.assertEqual(mod.relationship_details('Zelenskyy urges support for new US sanctions on Russia after Trump puts them on hold','sanctions')[0],'sanctions_on_hold')
 def test_ambassador(self):
  self.assertEqual(mod.relationship_details('US ambassador urges Israel to prosecute attackers of American journalist','diplomacy')[0],'diplomatic_statement')
 def test_trade(self):
  self.assertEqual(mod.relationship_details('Egypt Thailand expand trade ties','trade')[0],'trade')
 def test_evidence_and_schema(self):
  title="US Sanctions Waiver: Relief for India's Energy & Exporters"
  result=mod.publish_links([{'articles':[{'url':'https://example.org/test','title':title,'publisher':'Sample'}]}])
  link=result['links'][0]
  self.assertEqual(link['relationship'],'sanctions_waiver')
  self.assertIn('waiver',link['relationship_label'].lower())
  self.assertIn('not establish',link['relationship_explanation'])
  self.assertEqual(link['evidence'],'explicit_bilateral_headline')
 def test_no_incidental_co_mentions(self):
  self.assertIsNone(mod.detect('New Zealand and Australia weather forecast on Tuesday'))

if __name__=='__main__':unittest.main()
