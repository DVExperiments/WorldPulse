"""Fail-closed D.6 installer: requires D.5, patches only known call sites."""
import ast
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent

def main():
    target=HERE/'update.py'; retention=HERE/'browse_retention.py'
    if not all(p.exists() for p in (target,retention,HERE/'geographic_quality.py')):
        sys.exit('STOP: collector, D.5 retention, or D.6 module missing. No modifications.')
    s=target.read_text(encoding='utf-8'); r=retention.read_text(encoding='utf-8')
    if 'from geographic_quality import curated_match' in s and 'balanced_select(self._rows.values()' in r:
        print('D.6 already installed.'); return
    edits=[
      ('from browse_retention import BrowseRetention\n','from browse_retention import BrowseRetention\nfrom geographic_quality import curated_match\n'),
      ("   if not place:\n    browse_retention.add(a,when,now,category or classify(a['title']),'no_confident_geography')", "   if not place:\n    place,match_origin=curated_match(a['title'],a.get('description',''))\n   if not place:\n    browse_retention.add(a,when,now,category or classify(a['title']),'no_confident_geography')"),
    ]
    for old,new in edits:
        if s.count(old)!=1:sys.exit('STOP: collector has unexpected structure. No modifications.')
        s=s.replace(old,new,1)
    old="        items = sorted(self._rows.values(), key=lambda r: r['published_at'], reverse=True)\n        items = items[:_MAX_ITEMS]"
    new="        items, balance_stats = balanced_select(self._rows.values(), _MAX_ITEMS)\n        self.stats['publisher_balance'] = balance_stats"
    if r.count(old)!=1 or r.count('from geographic_quality import balanced_select')!=0:
        sys.exit('STOP: retention module has unexpected structure. No modifications.')
    r=r.replace('import datetime as dt\n','import datetime as dt\nfrom geographic_quality import balanced_select\n',1).replace(old,new,1)
    ast.parse(s);ast.parse(r)
    target.write_text(s,encoding='utf-8');retention.write_text(r,encoding='utf-8')
    print('D.6 installed: curated location fallback + publisher-balanced Discover retention.')
    print('Review changes and commit scripts/update.py scripts/browse_retention.py and geographic_quality.py.')
if __name__=='__main__':main()
