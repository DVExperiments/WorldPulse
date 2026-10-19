"""No external services required."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_semantic_d7 import decision,summary

def check(title,place,expected,desc='',d6=None):
 x=decision({'title':title,'description':desc},{'name':place},d6)
 assert x['action']==expected,(title,x)
 return x

check('Protestos na Tunísia exigem mais liberdade e direitos','Liberdade','withhold')
check('Decision sparks outrage across parliament','Sparks','withhold')
check('Mobile phone sales surge','Mobile','withhold')
check('Reading scores decline at schools','Reading','withhold')
check('Floods reported in Sparks, Nevada','Sparks','retain')
check('New library opens in Reading','Reading','retain')
check('Protest in Liberdade district of São Paulo','Liberdade','retain')
check('Mexico and Toluca residents prepare for storms','Toluca','review',d6={'headline_places':['Mexico','Toluca'],'multiple_headline_places':True})
check('Trump suspende sanções contra a Rússia','Paraná','retain')
check('Israel elections enter final stretch','Vietnam','review',d6={'headline_places':['Israel']})
assert summary([check('Decision sparks outrage','Sparks','withhold')])['decision_counts']['withhold']==1
src=(Path(__file__).resolve().parents[1]/'scripts/update.py').read_text()
assert "'release':'v2.4D.8'" in src and "'d7_semantic_accuracy'" in src
print('v2.4D.7 semantic regression tests passed')
