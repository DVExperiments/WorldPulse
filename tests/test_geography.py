"""Run from the repository root: python -m unittest discover -s tests -v"""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('worldpulse_update', ROOT/'scripts'/'update.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class GeographicMatchingTests(unittest.TestCase):
    def test_location_subjects(self):
        cases = {
            'Ships in Strait of Hormuz still face attacks': 'Strait of Hormuz',
            'Power struggle deepens in Iraqi Kurdistan': 'Iraqi Kurdistan',
            'HCM City reports meningococcal disease cluster': 'Ho Chi Minh City',
            'Deadly bird flu hits Macquarie Island': 'Macquarie Island',
            'Homicide suspect found in Kalispell': 'Kalispell',
            'Hospital in Bacolod reports an outbreak': 'Bacolod',
            'Somali opposition announces election plans': 'Somalia',
            'Opposition unites against governor rule in K-P province': 'Khyber Pakhtunkhwa',
        }
        for title, expected in cases.items():
            with self.subTest(title=title):
                p, basis = mod.locate(title)
                self.assertIsNotNone(p)
                self.assertEqual(p['name'], expected)
                self.assertEqual(basis, 'headline')

    def test_no_guessing(self):
        for title in ['On Our Radar', 'Nice new approach to housing',
                      'We cannot wait for wildlife to reach crisis point',
                      'Pediatric Medical Devices Market To 2035']:
            with self.subTest(title=title):
                p, basis = mod.locate(title)
                self.assertIsNone(p)
                self.assertEqual(basis, 'unmapped')

    def test_summary_as_lower_confidence_evidence(self):
        place, basis = mod.locate('Hospital reports disease cluster',
                                'The cases were detected in Bacolod')
        self.assertEqual(place['name'], 'Bacolod')
        self.assertEqual(basis, 'description')

if __name__ == '__main__':
    unittest.main()
