"""Offline tests; no network required. Run: python -m unittest discover -s tests -p test_global_geography.py"""
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import global_geography as gg

def record(id,name,lat,lng,country,pop):
 f=['']*19
 for i,v in {0:id,1:name,2:name,4:str(lat),5:str(lng),8:country,10:'01',14:str(pop)}.items():f[i]=v
 return '\t'.join(f)

class GlobalGeographyTests(unittest.TestCase):
 def test_unique_city_and_ambiguity(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'cities15000.zip'
   rows='\n'.join([record('1','Kumasi',6.69,-1.62,'GH',300000),record('2','Lusaka',-15.4,28.3,'ZM',1000000),record('3','Springfield',40,-89,'US',100000),record('4','Springfield',37,-93,'US',100000),record('5','Nice',43.7,7.2,'FR',300000)])
   with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('cities15000.txt',rows)
   old=gg.CACHE; gg.CACHE=path
   try:
    # Synthetic sample is smaller than production minimum; inspect parser by mocking file threshold.
    original=Path.stat
    from unittest.mock import patch
    with patch.object(gg.Path,'stat',autospec=True) as fake:
     fake.return_value=type('Stat',(),{'st_size':600000})()
     obj=gg.get_resolver([])
    self.assertTrue(obj.meta['available'],obj.meta)
    self.assertEqual(obj.match('Flooding in Kumasi today')['country_code'],'GH')
    self.assertIsNone(obj.match('Springfield faces a challenge'))
    self.assertIsNone(obj.match('It is a nice day'))
   finally:gg.CACHE=old

if __name__=='__main__':unittest.main()
