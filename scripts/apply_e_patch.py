"""WorldPulse v2.0E safe/idempotent installer; requires D.6.1."""
import ast
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent

def main():
    target=HERE/'update.py'; feature=HERE/'geo_expansion.py'
    if not target.is_file() or not feature.is_file(): sys.exit('STOP: collector/feature file missing; no edits.')
    text=target.read_text(encoding='utf8')
    if 'from geo_expansion import expanded_match' in text:
        if "place,match_origin=expanded_match(a['title'],a.get('description',''))" in text:
            print('v2.0E already installed.');return
        sys.exit('STOP: partial installation detected; no edits.')
    if 'from publisher_metadata import annotate\n' not in text or 'from geographic_quality import curated_match\n' not in text:
        sys.exit('STOP: D.6.1 prerequisites absent; no edits.')
    insertion="   if not place:\n    place,match_origin=curated_match(a['title'],a.get('description',''))\n"
    if text.count(insertion)!=1:sys.exit('STOP: unexpected collector structure; no edits.')
    out=text.replace('from geographic_quality import curated_match\n','from geographic_quality import curated_match\nfrom geo_expansion import expanded_match\n',1)
    out=out.replace(insertion,insertion+"   if not place:\n    place,match_origin=expanded_match(a['title'],a.get('description',''))\n",1)
    ast.parse(out)
    target.write_text(out,encoding='utf8')
    print('WorldPulse v2.0E installed. New conservative expanded-place fallback enabled.')
    print('Commit scripts/update.py after testing. No changes to website or Actions.')
if __name__=='__main__':main()
