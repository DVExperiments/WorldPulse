"""Offline regression test for D.3 stage accounting without invoking network collection."""
import ast
import datetime as dt
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

src=Path(__file__).resolve().parents[1]/'scripts'/'update.py'
tree=ast.parse(src.read_text(encoding='utf8'))
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
assert {'new_feed_audit','produce','publish_pipeline_audit'} <= functions.keys()
assert 'audit_feed_key' in src.read_text(encoding='utf8')
ns={'dt':dt,'defaultdict':defaultdict,'collect':SimpleNamespace(pipeline={}),
    'signature':lambda title:frozenset(title.lower().split()),
    'public_evidence':lambda a:{}}
code=compile(ast.Module(body=[functions['new_feed_audit'],functions['produce']],type_ignores=[]),str(src),'exec')
exec(code,ns)
now=dt.datetime(2026,10,18,12,tzinfo=dt.timezone.utc)
ns['collect'].pipeline={'google/politics/US':ns['new_feed_audit']('google/politics/US','aggregator','US','en'),
                        'direct/example':ns['new_feed_audit']('direct/example','publisher','GB','en')}
base={'title':'Major flooding in Auckland today','url':'https://example.org/story','at':now.isoformat(),
      'place':{'name':'Auckland','lat':-36.8,'lng':174.7},'category':'hazards','publisher':'Publisher',
      'source_url':'','source_kind':'publisher','language':'en','geo_match':'headline'}
records=[dict(base,audit_feed_key='google/politics/US'),dict(base,audit_feed_key='direct/example')]
points,duplicates,unique=ns['produce'](records,now)
assert unique==1 and duplicates==1 and len(points)==1
assert sum(f['deduplication_survived'] for f in ns['collect'].pipeline.values())==1
assert sum(f['globe_articles'] for f in ns['collect'].pipeline.values())==1
print('D.3 audit smoke test passed')
