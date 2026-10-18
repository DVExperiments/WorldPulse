"""Fail-closed D.5 patch. Requires the D.4 collector; edits only scripts/update.py."""
import ast
from pathlib import Path
import sys

TARGET = Path(__file__).resolve().with_name('update.py')

def main():
    if not TARGET.exists() or not TARGET.with_name('geo_intelligence.py').exists() or not TARGET.with_name('browse_retention.py').exists():
        sys.exit('STOP: original WorldPulse D.4 collector/modules not found. No changes made.')
    s = TARGET.read_text(encoding='utf8')
    if 'from browse_retention import BrowseRetention' in s:
        print('WorldPulse D.5 collector is already installed; no changes made.')
        return
    replacements = [
        ('from geo_intelligence import CollectorAudit, context_match, classify_unmatched, embed_geo_report\n',
         'from geo_intelligence import CollectorAudit, context_match, classify_unmatched, embed_geo_report\nfrom browse_retention import BrowseRetention\n'),
        (' results=[];failures={}; scanned=Counter();health=[];seen_queries=0;unmapped=[]; geo_audit=CollectorAudit()',
         ' results=[];failures={}; scanned=Counter();health=[];seen_queries=0;unmapped=[]; geo_audit=CollectorAudit(); browse_retention=BrowseRetention()'),
        ("   if not when or not cutoff<=when<=now+dt.timedelta(minutes=20):\n    geo_audit.record(source,'out_of_window',a.get('title',''),language,a.get('url',''))",
         "   if not when or not cutoff<=when<=now+dt.timedelta(minutes=20):\n    browse_retention.add(a,when,now,category or classify(a['title']),'outside_globe_window')\n    geo_audit.record(source,'out_of_window',a.get('title',''),language,a.get('url',''))"),
        ("   if not place:\n    geo_audit.record(source,'unmapped',a['title'],language,a['url'])",
         "   if not place:\n    browse_retention.add(a,when,now,category or classify(a['title']),'no_confident_geography')\n    geo_audit.record(source,'unmapped',a['title'],language,a['url'])"),
        (" geo_audit.save(ROOT/'data/geo-intelligence.json',now)\n return results,failures,dict(scanned),seen_queries,health,unmapped",
         " geo_audit.save(ROOT/'data/geo-intelligence.json',now)\n collect.browse_articles=browse_retention.export()\n collect.browse_stats=browse_retention.stats\n return results,failures,dict(scanned),seen_queries,health,unmapped"),
        ("  'errors':failures,'points':points}",
         "  'errors':failures,'points':points,\n  'unlocated_articles':getattr(collect,'browse_articles',[]),\n  'browse_retention':{'window_hours':72,'globe_window_hours':24,'note':'Unlocated articles are for browsing only, never globe pins. Archive entries are older than 24 hours.', **getattr(collect,'browse_stats',{})}}"),
    ]
    for old, new in replacements:
        n=s.count(old)
        if n!=1:
            sys.exit(f'STOP: expected collector pattern occurs {n} times (must be 1): {old[:85]!r}. No files modified.')
        s=s.replace(old,new,1)
    ast.parse(s)
    TARGET.write_text(s,encoding='utf8')
    print('D.5 installed. Globe still uses 24h; news.json now carries 72h unlocated Discover entries.')
    print('Review scripts/update.py, commit and run Refresh geographic news.')

if __name__=='__main__': main()
