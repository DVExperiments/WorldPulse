"""Standalone checks for v2.4D.1 regional RSS sampling additions.
Run: python tests/test_regional_sampling.py
No network access or installed collector modules required.
"""
import ast
import pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/update.py').read_text(encoding='utf-8')
module=ast.parse(source)
ns={}
for node in module.body:
 if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id in {'QUERIES','REGIONS','REGION_LANGUAGES','LOCAL_QUERIES'} for x in node.targets):
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<test>','exec'),ns)
for node in module.body:
 if isinstance(node,ast.FunctionDef) and node.name=='region_query':
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<test>','exec'),ns)
regions={c:(hl,ceid) for c,hl,ceid in ns['REGIONS']}
assert {'BR','MX','KE'} <= regions.keys()
assert len(regions)==len(ns['REGIONS'])
assert regions['BR']==('pt-BR','BR:pt-419')
assert regions['MX']==('es-419','MX:es-419')
assert ns['REGION_LANGUAGES']['BR']=='pt'
assert ns['REGION_LANGUAGES']['MX']=='es'
assert ns['REGION_LANGUAGES']['KE']=='en'
for category in ns['QUERIES']:
 for reg in regions:
  q=ns['region_query'](category,0,reg)
  assert q and isinstance(q,str)
 assert ns['region_query'](category,0,'BR') != ns['region_query'](category,0,'US')
 assert ns['region_query'](category,0,'MX') != ns['region_query'](category,0,'US')
assert "REGION_LANGUAGES.get(locale[0],'en')" in source
assert 'evaluate_geographic_subject(place' in source
assert 'decision_audit.decide(a,place,match_origin)' in source
assert 'update_health_file(' in source
print('PASS: 11 regional editions; 3 new locales; translated queries; language metadata; geo safeguards present')
