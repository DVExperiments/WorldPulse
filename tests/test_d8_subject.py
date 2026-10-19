import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_subject_d8 import decision,summary

def test(title,place,expected,desc='',d6=None):
 result=decision({'title':title,'description':desc},{'name':place},d6)
 assert result['action']==expected,(title,result)
 return result

test('Trump suspende sanções contra a Rússia, contraria Congresso','Paraná','withhold')
test('Russia sanctions affect farming in Paraná','Paraná','retain')
test('Flood warnings in Paraná after heavy rainfall','Paraná','retain')
test('Minister Anand said talks will resume','Anand','withhold')
test('New clinic opens in Anand','Anand','retain')
test('Storms in Toluca, Mexico','Toluca','retain')
test('Mexico and Canada sign trade agreement','Mexico','review')
test('Ukraine and Russia negotiate ceasefire','Vietnam','review')
test('Floods near Sparks, Nevada','Sparks','retain')
test('Protestos exigem liberdade','Liberdade','retain') # D7 separately blocks this
assert summary([test('Dr Anand said reforms are coming','Anand','withhold')])['decision_counts']['withhold']==1
src=(Path(__file__).resolve().parents[1]/'scripts/update.py').read_text()
assert "'release':'v2.4D.8'" in src and "'d8_geographic_subject'" in src
print('v2.4D.8 subject tests passed')
