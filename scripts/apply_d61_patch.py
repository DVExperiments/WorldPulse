"""Idempotent, fail-closed WorldPulse D.6.1 collector installer."""
import ast
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

def main():
    path = HERE / 'update.py'
    module = HERE / 'publisher_metadata.py'
    if not path.is_file() or not module.is_file():
        sys.exit('STOP: update.py or publisher_metadata.py missing. No modifications.')
    text = path.read_text(encoding='utf-8')
    import_line = 'from publisher_metadata import annotate\n'
    mark = '  for a in rows:\n   geo_audit.record(source,'
    replacement = '  for a in rows:\n   a = annotate(a,source,kind)\n   geo_audit.record(source,'
    if import_line in text and replacement in text:
        print('D.6.1 already installed; no changes.'); return
    if import_line in text or text.count(mark) != 1 or text.count('from browse_retention import BrowseRetention\n') != 1:
        sys.exit('STOP: unexpected collector structure or partial installation. No modifications.')
    # Version guard: D.6 publisher balancing should already be installed.
    retention = HERE / 'browse_retention.py'
    if not retention.is_file() or 'balanced_select(' not in retention.read_text(encoding='utf-8'):
        sys.exit('STOP: D.6 publisher balancing not detected. No modifications.')
    patched = text.replace('from browse_retention import BrowseRetention\n', 'from browse_retention import BrowseRetention\n' + import_line, 1)
    patched = patched.replace(mark, replacement, 1)
    ast.parse(patched)
    path.write_text(patched, encoding='utf-8')
    print('D.6.1 installed: source names resolved before mapping, browsing and publisher balancing.')
    print('Run tests, inspect git diff and commit scripts/update.py.')

if __name__ == '__main__':
    main()
