"""Conservative idempotent 2.0E.2 installer for original WorldPulse collector."""
import ast
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent

def main():
 path=HERE/'update.py'
 if not path.exists() or not (HERE/'geo_decision.py').exists() or not (HERE/'geo_accuracy_audit.py').exists():
  sys.exit('STOP: missing prerequisite files, no changes made.')
 original=path.read_text(encoding='utf8')
 anchors=[
  ('from geo_accuracy_audit import publish_audit\n', 'from geo_accuracy_audit import publish_audit\nfrom geo_decision import DecisionAudit\n'),
  ('geo_audit=CollectorAudit(); browse_retention=BrowseRetention()', 'geo_audit=CollectorAudit(); browse_retention=BrowseRetention(); decision_audit=DecisionAudit()'),
  ("   mapped+=1\n   geo_audit.record(source,'mapped',mapped=True)", "   place,match_origin=decision_audit.decide(a,place,match_origin)\n   mapped+=1\n   geo_audit.record(source,'mapped',mapped=True)"),
  (" collect.browse_stats=browse_retention.stats\n", " collect.browse_stats=browse_retention.stats\n collect.decision_audit=decision_audit\n"),
  (" publish_audit(raw,now,ROOT/'data')\n", " publish_audit(raw,now,ROOT/'data')\n collect.decision_audit.publish(ROOT/'data',now)\n")]
 applied=all(new in original for old,new in anchors)
 partially=any(new in original for old,new in anchors)
 if applied:
  print('WorldPulse v2.0E.2 already installed; nothing changed.');return
 if partially:sys.exit('STOP: partial installation detected. No changes made.')
 for old,new in anchors:
  if original.count(old)!=1:sys.exit('STOP: expected collector anchor missing or duplicated: '+old[:60])
 patched=original
 for old,new in anchors:patched=patched.replace(old,new,1)
 ast.parse(patched)
 path.write_text(patched,encoding='utf8')
 print('WorldPulse v2.0E.2 installed. Test, then commit scripts/update.py.')
if __name__=='__main__':main()
