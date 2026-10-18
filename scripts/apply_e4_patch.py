"""Idempotent fail-closed installer for WorldPulse E.4 collector (requires E.3)."""
from pathlib import Path
import ast,sys
base=Path(__file__).resolve().parent
target=base/'update.py'
replacements=[
 ('from geo_confidence import publish_confidence\n', 'from geo_confidence import publish_confidence\nfrom geo_public_evidence import public_evidence\n'),
 ("'source_url':a['source_url'],'source_kind':a.get('source_kind'),'language':a.get('language','en'),'geo_match':a.get('geo_match','headline')} for a in articles[:20]]", "'source_url':a['source_url'],'source_kind':a.get('source_kind'),'language':a.get('language','en'),'geo_match':a.get('geo_match','headline'),**public_evidence(a)} for a in articles[:20]]"),
]
def main():
 if not target.exists() or not (base/'geo_public_evidence.py').exists() or not (base/'geo_confidence.py').exists():sys.exit('STOP: E.3 collector and E.4 module required. No changes made.')
 src=target.read_text(encoding='utf8')
 checks=[new in src for old,new in replacements]
 if all(checks):print('E.4 already installed. No change.');return
 if any(checks):sys.exit('STOP: Partial E.4 patch found. No changes made.')
 for old,new in replacements:
  if src.count(old)!=1:sys.exit('STOP: Expected E.3 anchor missing/duplicated. No changes made: '+repr(old[:65]))
 result=src
 for old,new in replacements: result=result.replace(old,new,1)
 ast.parse(result)
 target.write_text(result,encoding='utf8')
 print('WorldPulse v2.0E.4 collector installed. Commit scripts/update.py after tests.')
if __name__=='__main__':main()
