"""Offline, deterministic checks; run from repository root."""
import sys, ast
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from geo_evidence_d5 import candidates_for_review, evidence_for_match, coverage_report
assert any(c['country']=='Germany' for c in candidates_for_review('Unfall in Deutschland',''))
assert any(c['country']=='Switzerland' for c in candidates_for_review('Proteste en Suisse',''))
assert {c['country'] for c in candidates_for_review('Talks in Deutschland and en France','')}=={'Germany','France'}
assert not candidates_for_review('Market outlook without a place', '')
a={'title':'Floods in Auckland today','description':'','place':{'name':'Auckland','lat':-36.8,'lng':174.7,'level':'place'},'geo_match':'headline','source_region':'GB','language':'en'}
assert evidence_for_match(a)['evidence_class']=='literal_name_in_headline'
b={**a,'title':'Weather alert','description':'Auckland experiences heavy rains','geo_match':'description'}
assert evidence_for_match(b)['evidence_class']=='literal_name_in_description'
c={**a,'title':'Weather alert','description':'The city experiences heavy rains','geo_match':'context'}
assert evidence_for_match(c)['confidence_label']=='contextual_review'
report=coverage_report([a,b,c],[{'name':'Auckland','articles':[a,b]}], [{'title':'Talks in Deutschland and en France','feed':'test','url':'https://example.org'}], [{'editorial_region':'GB','globe_articles':2,'geography_unmatched':1}])
assert report['mapped_by_hemisphere']['SE']==3
assert report['unmatched_multi_country_rows']==1
assert report['globe_serialized_articles']==2
assert report['discovery_edition_vs_actual_match']['GB']['matched_rows']==3
src=(root/'scripts/update.py').read_text(encoding='utf8');t=ast.parse(src)
assert any(n.name=='publish_pipeline_audit' for n in t.body if isinstance(n,ast.FunctionDef))
assert "'release':'v2.4D.5'" in src
print('WorldPulse v2.4D.5 evidence and coverage offline tests passed')
