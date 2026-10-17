import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_population_texture import normalize_density

class TestPopulationTexture(unittest.TestCase):
    def test_monotonic_brightness(self):
        assert list(normalize_density([0,1,10,100,1000,10000])) == sorted(normalize_density([0,1,10,100,1000,10000]))
        assert normalize_density([0])[0] == 0
        assert normalize_density([10000])[0] == 255
    def test_invalid_values(self):
        assert list(normalize_density([float('nan'),-1,float('inf')])) == [0,0,0]
if __name__=='__main__':unittest.main()
