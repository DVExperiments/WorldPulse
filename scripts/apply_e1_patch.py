"""Fail-closed, repeat-safe v2.0E.1 installer for original WorldPulse collector."""
import ast
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

def main():
    path=HERE/'update.py'
    if not path.exists() or not (HERE/'geo_accuracy_audit.py').exists() or not (HERE/'geo_expansion.py').exists():
        sys.exit('STOP: required collector files missing. Nothing changed.')
    before=path.read_text(encoding='utf8')
    imp='from geo_accuracy_audit import publish_audit\n'
    call=" publish_audit(raw,now,ROOT/'data')\n"
    if imp in before or call in before:
        if imp in before and call in before:
            print('v2.0E.1 already installed; nothing changed.');return
        sys.exit('STOP: partial E.1 installation detected. Nothing changed.')
    anchor_import='from geo_expansion import expanded_match\n'
    anchor_call=" embed_geo_report(ROOT/'data')\n"
    if before.count(anchor_import)!=1 or before.count(anchor_call)!=1:
        sys.exit('STOP: unexpected update.py structure or missing v2.0E. Nothing changed.')
    after=before.replace(anchor_import,anchor_import+imp,1).replace(anchor_call,anchor_call+call,1)
    ast.parse(after)
    path.write_text(after,encoding='utf8')
    print('WorldPulse v2.0E.1 installed: advisory match-quality report enabled.')
    print('Existing locations and frontend unchanged. Commit scripts/update.py after testing.')

if __name__=='__main__':main()
