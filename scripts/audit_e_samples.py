"""Optional offline audit: python scripts/audit_e_samples.py data/unmatched-review.json"""
import json,sys
from pathlib import Path
from geo_expansion import inspect_unmatched

def main():
 if len(sys.argv)!=2:raise SystemExit('Usage: python scripts/audit_e_samples.py data/unmatched-review.json')
 report=json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
 print(json.dumps(inspect_unmatched(report),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
