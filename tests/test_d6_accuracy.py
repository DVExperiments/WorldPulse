"""Offline D6 attribution regression checks."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_accuracy_d6 import audit_decision, summary
places=[{'name':n,'level':'country'} for n in ('Israel','Vietnam','France','Germany','Kenya')]
a={'title':'Israel election enters final stretch','description':'Vietnam trade relations in background'}
r=audit_decision(a,places[1],places)
assert r['action']=='withhold_description_conflict' and r['headline_places']==['Israel']
assert audit_decision(a,places[0],places)['action']=='retain'
assert audit_decision({'title':'Israel and Vietnam hold talks','description':'Delegations meet'},places[0],places)['action']=='review'
assert audit_decision({'title':'Anand announces reforms','description':''},places[0],places)['ambiguous_tokens']==['anand']
assert audit_decision({'title':'Kenya drought worsens','description':'No other places'},places[4],places)['action']=='retain'
assert summary([r],[r])['withheld_count']==1
src=(Path(__file__).resolve().parents[1]/'scripts/update.py').read_text()
assert "'release':'v2.4D.6'" in src and "'d6_attribution_accuracy'" in src
print('v2.4D.6 attribution accuracy tests passed')
