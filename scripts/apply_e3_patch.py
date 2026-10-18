"""Fail-closed, idempotent E.3 patch for original collector after E.2."""
import ast
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent

def main():
    target=ROOT/'update.py'
    if not target.exists() or not (ROOT/'geo_confidence.py').exists() or not (ROOT/'geo_decision.py').exists():
        sys.exit('STOP: prerequisite collector files missing; no changes made')
    before=target.read_text(encoding='utf8')
    replacements=[
        ('from geo_decision import DecisionAudit\n','from geo_decision import DecisionAudit\nfrom geo_confidence import publish_confidence\n'),
        (" collect.decision_audit.publish(ROOT/'data',now)\n", " collect.decision_audit.publish(ROOT/'data',now)\n publish_confidence(raw,now,ROOT/'data')\n")]
    applied=[new in before for old,new in replacements]
    if all(applied):print('WorldPulse E.3 already installed; no changes made');return
    if any(applied):sys.exit('STOP: partial E.3 patch detected; no changes made')
    for old,new in replacements:
        if before.count(old)!=1:sys.exit('STOP: expected E.2 anchor missing or duplicated; no changes made: '+repr(old))
    after=before
    for old,new in replacements:after=after.replace(old,new,1)
    ast.parse(after)
    target.write_text(after,encoding='utf8')
    print('WorldPulse v2.0E.3 installed. Test, then commit scripts/update.py.')
if __name__=='__main__':main()
