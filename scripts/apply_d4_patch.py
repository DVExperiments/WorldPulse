"""Idempotent, fail-closed patch for the original WorldPulse scripts/update.py."""
from pathlib import Path
import ast
import sys

TARGET=Path(__file__).resolve().parent/'update.py'
IMPORT='from geo_intelligence import CollectorAudit, context_match, classify_unmatched, embed_geo_report\n'
OLD=' results=[];failures={}; scanned=Counter();health=[];seen_queries=0;unmapped=[]'
NEW=' results=[];failures={}; scanned=Counter();health=[];seen_queries=0;unmapped=[]; geo_audit=CollectorAudit()'
INGEST_OLD='''  for a in rows:
   when=parsed_timestamp(a['published'])
   if not when or not cutoff<=when<=now+dt.timedelta(minutes=20):continue
   if not a['title'] or not a['url'].startswith('https://'):continue
   place,match_origin=locate(a['title'],a.get('description',''))
   if not place:
    place,match_origin=find_explicit(a['title'],a.get('description',''),a['url'],PLACES)
   if not place:
    unmapped.append'''
INGEST_NEW='''  for a in rows:
   geo_audit.record(source,'feed_items',mapped=True)
   when=parsed_timestamp(a['published'])
   if not when or not cutoff<=when<=now+dt.timedelta(minutes=20):
    geo_audit.record(source,'out_of_window',a.get('title',''),language,a.get('url',''))
    continue
   if not a['title'] or not a['url'].startswith('https://'):
    geo_audit.record(source,'invalid_article',a.get('title',''),language,a.get('url',''))
    continue
   geo_audit.record(source,'eligible',mapped=True)
   place,match_origin=locate(a['title'],a.get('description',''))
   if not place:
    place,match_origin=find_explicit(a['title'],a.get('description',''),a['url'],PLACES)
   if not place:
    place,match_origin=context_match(a['title'],a.get('description',''),a['url'],PLACES)
   if not place:
    geo_audit.record(source,'unmapped',a['title'],language,a['url'])
    geo_audit.record(source,classify_unmatched(a['title'],a.get('description',''),a['url'],language),mapped=True)
    unmapped.append'''
AFTER_OLD="   mapped+=1\n   results.append"
AFTER_NEW="   mapped+=1\n   geo_audit.record(source,'mapped',mapped=True)\n   geo_audit.record(source,'method/'+match_origin,mapped=True)\n   results.append"
EMBED_OLD=' update_diagnostics(now,health,unmapped,points,duplicates)'
EMBED_NEW=EMBED_OLD+"\n embed_geo_report(ROOT/'data')"
RETURN_OLD=' return results,failures,dict(scanned),seen_queries,health,unmapped'
RETURN_NEW=" geo_audit.save(ROOT/'data/geo-intelligence.json',now)\n return results,failures,dict(scanned),seen_queries,health,unmapped"

def main():
    if not TARGET.exists():sys.exit('STOP: scripts/update.py not found; use ORIGINAL WorldPulse repository.')
    if not (TARGET.parent/'geo_intelligence.py').exists():sys.exit('STOP: geo_intelligence.py is missing.')
    source=TARGET.read_text(encoding='utf-8')
    if 'geo_audit.save(' in source:
        print('WorldPulse 2.0D.4 already installed; nothing changed.');return
    if 'from geo_mapping_enhancements import find_explicit' not in source:
        sys.exit('STOP: 2.0D.3 geography module must be installed first. No changes made.')
    changes=[('from geo_mapping_enhancements import find_explicit\n','from geo_mapping_enhancements import find_explicit\n'+IMPORT), (OLD,NEW),(INGEST_OLD,INGEST_NEW),(AFTER_OLD,AFTER_NEW),(RETURN_OLD,RETURN_NEW),(EMBED_OLD,EMBED_NEW)]
    for old,new in changes:
        count=source.count(old)
        if count!=1:sys.exit(f'STOP: expected collector pattern occurs {count} times (needed 1). No files modified. Pattern: {old[:75]!r}')
        source=source.replace(old,new,1)
    ast.parse(source)
    TARGET.write_text(source,encoding='utf-8')
    print('WorldPulse 2.0D.4 installed: extra geo recognition + article eligibility audit.')
    print('Commit scripts/update.py; run Refresh geographic news; review data/geo-intelligence.json.')
if __name__=='__main__':main()
