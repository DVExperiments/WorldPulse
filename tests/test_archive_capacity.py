import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parents[1] / 'scripts' / 'archive_news.py'
spec = importlib.util.spec_from_file_location('archive_news', ARCHIVE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def feed(size, stamp='2026-10-18T08:27:53+00:00'):
    return {'updated_at': stamp, 'status': 'partial', 'query_successes': 1, 'query_attempts': 2,
            'points': [{'name': f'Place {i}', 'category': 'politics', 'lat': i % 90,
                        'lng': i % 180, 'count': 1, 'articles': []} for i in range(size)]}


class ArchiveCapacityTests(unittest.TestCase):
    def test_full_recent_feed(self):
        result = m.compact(feed(249))
        self.assertEqual(len(result['locations']), 249)
        self.assertEqual(result['location_entries_omitted'], 0)
        self.assertEqual(result['mapped_signals'], 249)

    def test_bounded_large_feed(self):
        result = m.compact(feed(510))
        self.assertEqual(len(result['locations']), 500)
        self.assertEqual(result['location_entries_available'], 510)
        self.assertEqual(result['location_entries_omitted'], 10)

    def test_same_snapshot_does_not_overwrite_old_day(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            old = m.compact(feed(249))
            old['locations'] = old['locations'][:45]
            payload = {'schema':1, 'day':'2026-10-18','snapshots':[old]}
            day = dest / '2026-10-18.json'
            day.write_text(json.dumps(payload))
            added, _ = m.archive(feed(249), dest, today=m.dt.date(2026,10,18))
            self.assertFalse(added)
            self.assertEqual(len(json.loads(day.read_text())['snapshots'][0]['locations']),45)

    def test_new_snapshot_appends_with_full_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            added, index = m.archive(feed(249), dest, today=m.dt.date(2026,10,18))
            self.assertTrue(added)
            self.assertEqual(index['snapshots_total'], 1)
            row = json.loads((dest/'2026-10-18.json').read_text())['snapshots'][0]
            self.assertEqual(len(row['locations']),249)

    def test_stale_rejected(self):
        f = feed(249)
        f['status'] = 'stale'
        with self.assertRaises(ValueError): m.compact(f)

if __name__=='__main__': unittest.main()
