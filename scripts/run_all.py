"""Independent collectors. News is required, official-event overlays are optional."""
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def invoke(name, optional=False):
    result=subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT)
    if result.returncode and not optional:raise SystemExit(result.returncode)
    if result.returncode:print(f'Optional adapter {name} failed; continuing')

if __name__=='__main__':
    invoke('update.py')
    invoke('events.py',optional=True)
