"""Safely apply geographic fallback to existing scripts/update.py without replacing it.
Run from the original WorldPulse repo: python scripts/apply_geo_patch.py
"""
from pathlib import Path
import sys

TARGET=Path(__file__).resolve().parent/'update.py'
IMPORT='from geo_mapping_enhancements import find_explicit\n'
OLD="   place,match_origin=locate(a['title'],a.get('description',''))"
NEW="""   place,match_origin=locate(a['title'],a.get('description',''))
   if not place:
    place,match_origin=find_explicit(a['title'],a.get('description',''),a['url'],PLACES)"""

def main():
    if not TARGET.exists():
        sys.exit('No scripts/update.py found. Upload into ORIGINAL WorldPulse repository and retry.')
    if not (TARGET.parent/'geo_mapping_enhancements.py').exists():
        sys.exit('Missing scripts/geo_mapping_enhancements.py')
    src=TARGET.read_text(encoding='utf8')
    if IMPORT.strip() in src and 'place,match_origin=find_explicit' in src:
        print('Already installed; no changes needed.')
        return
    if OLD not in src:
        sys.exit('Safety stop: update.py has changed and the expected location call was not found. No files modified.')
    if 'from publisher_network import merge_feeds\n' not in src:
        sys.exit('Safety stop: unexpected update.py imports. No files modified.')
    new=src.replace('from publisher_network import merge_feeds\n', 'from publisher_network import merge_feeds\n'+IMPORT,1).replace(OLD,NEW,1)
    compile(new,str(TARGET),'exec')
    TARGET.write_text(new,encoding='utf8')
    print('Geographic fallback enabled. Existing changes remain in update.py.')
    print('Review and commit scripts/update.py plus geo_mapping_enhancements.py.')

if __name__=='__main__':main()
