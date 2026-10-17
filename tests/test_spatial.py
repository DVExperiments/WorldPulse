import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.update import locate
class SpatialTests(unittest.TestCase):
    def test_states(self):
        for title,expected in [('Wildfire in California state','California, USA'),('Texas state legislature votes','Texas, USA'),('Ontario province introduces new measure','Ontario, Canada'),('Quebec province reports flooding','Quebec, Canada'),('Jalisco state reports new investment','Jalisco, Mexico')]:
            place,origin=locate(title)
            self.assertIsNotNone(place,title)
            self.assertEqual(place['name'],expected,title)
            self.assertEqual(place['level'],'region')
    def test_existing(self):
        self.assertEqual(locate('HCM City reports outbreak')[0]['name'],'Ho Chi Minh City')
        self.assertIsNone(locate('On our radar')[0])
    def test_no_ambiguous_abbreviation(self):
        self.assertIsNone(locate('CA moves to the next stage')[0])
if __name__=='__main__':unittest.main()
