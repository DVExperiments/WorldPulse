"""Guard against accidentally importing geo validation without invoking it."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class GeoIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse((ROOT / 'scripts' / 'update.py').read_text(encoding='utf-8'))

    def test_validation_is_called(self):
        calls = [n for n in ast.walk(self.tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        self.assertTrue(any(n.func.id == 'evaluate_geographic_subject' for n in calls))

    def test_rejected_matches_are_skipped(self):
        source = (ROOT / 'scripts' / 'update.py').read_text(encoding='utf-8')
        between = source.split('accepted,reason=evaluate_geographic_subject', 1)[1].split('mapped+=1', 1)[0]
        self.assertIn('if not accepted:', between)
        self.assertIn('browse_retention.add(', between)
        self.assertIn('continue', between)

    def test_rejection_report_is_in_output(self):
        source = (ROOT / 'scripts' / 'update.py').read_text(encoding='utf-8')
        self.assertIn("'geographic_disambiguation':", source)
        self.assertIn("collect.geo_rejections=geo_rejections", source)

if __name__ == '__main__': unittest.main()
