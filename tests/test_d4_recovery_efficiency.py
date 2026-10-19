"""Run with python tests/test_d4_recovery_efficiency.py, no network dependencies."""
import ast, sys, datetime as dt
from pathlib import Path
from types import SimpleNamespace
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from geo_recovery_d4 import recover_explicit_geography,diagnose_unmatched,summarize_efficiency
places=[{'name':'Mexico','level':'country','lat':23.0,'lng':-102.0},{'name':'South Africa','level':'country','lat':-30.0,'lng':25.0}]
assert recover_explicit_geography('Noticias importantes en México','',places)[0]['name']=='Mexico'
assert recover_explicit_geography('Crise no Brasil','',places) is None # no place in gazetteer
assert recover_explicit_geography('Mexico trade deal','',places) is None # no explicit qualifier
assert recover_explicit_geography('Talks in México and in África do Sul','',places) is None
assert recover_explicit_geography('News in Turkey','',places) is None
assert recover_explicit_geography('News in México','Report on South Africa',places)[0]['name']=='Mexico'
assert diagnose_unmatched('Global economy changes','')=='global_or_nonlocal_topic'
src=ROOT/'scripts'/'update.py'
tree=ast.parse(src.read_text(encoding='utf8'))
funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
ns={'dt':dt,'defaultdict':defaultdict,'collect':SimpleNamespace(pipeline={}), 'signature':lambda title:frozenset(title.lower().split()),'public_evidence':lambda a:{}}
exec(compile(ast.Module(body=[funcs['new_feed_audit'],funcs['produce']],type_ignores=[]),str(src),'exec'),ns)
now=dt.datetime(2026,10,18,12,tzinfo=dt.timezone.utc)
for key in ('google/a/US','direct/source'):
 ns['collect'].pipeline[key]=ns['new_feed_audit'](key,'aggregator','US','en')
base={'title':'Flooding in Auckland today','url':'https://example.org/story','at':now.isoformat(), 'place':{'name':'Auckland','lat':-36.8,'lng':174.7},'category':'hazards','publisher':'News','source_url':'','source_kind':'publisher','language':'en','geo_match':'headline'}
raw=[dict(base,audit_feed_key='google/a/US'),dict(base,audit_feed_key='direct/source')]
points,duplicates,kept=ns['produce'](raw,now)
assert duplicates==1 and kept==1
assert sum(f['duplicate_canonical'] for f in ns['collect'].pipeline.values())==1
assert sum(f['deduplication_survived'] for f in ns['collect'].pipeline.values())==1
assert sum(f['globe_articles'] for f in ns['collect'].pipeline.values())==1
report=summarize_efficiency(list(ns['collect'].pipeline.values()))
assert any(f['duplicate_canonical'] for f in report['overlap_by_feed'])
print('WorldPulse v2.4D.4 offline tests passed')
