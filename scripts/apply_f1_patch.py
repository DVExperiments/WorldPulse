"""Fail-closed, idempotent WorldPulse F.1 collector installation."""
from pathlib import Path
import ast,sys
base=Path(__file__).resolve().parent
target=base/'update.py'
old_import='from geo_public_evidence import public_evidence\n'
new_import=old_import+'from story_clustering import build_clusters\n'
old_field="  'errors':failures,'points':points,\n"
new_field="  'errors':failures,'points':points,'story_clusters':build_clusters(points),\n"
def main():
    if not target.exists() or not (base/'story_clustering.py').exists():sys.exit('STOP: Missing update.py or story_clustering.py')
    src=target.read_text(encoding='utf8')
    if new_import in src and new_field in src:print('F.1 already installed');return
    if new_import in src or new_field in src:sys.exit('STOP: Partial F.1 installation detected; no changes made')
    if src.count(old_import)!=1 or src.count(old_field)!=1:sys.exit('STOP: E.4 collector anchors missing; no changes made')
    dst=src.replace(old_import,new_import,1).replace(old_field,new_field,1)
    ast.parse(dst)
    target.write_text(dst,encoding='utf8')
    print('F.1 installed in scripts/update.py. Run tests, then commit this file.')
if __name__=='__main__':main()
