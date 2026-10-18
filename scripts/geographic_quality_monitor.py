"""WorldPulse 2.2C.2 geographic-quality monitoring; never changes mapping decisions.

Stores a bounded observation history inside the already committed data-health.json.
The values describe sampled feed data, not independently verified geocoding errors.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

SCHEMA = 1
MAX_SAMPLES = 180
RETENTION_DAYS = 90
REVIEW_LABELS = frozenset({'rubio', 'david', 'forest', 'union', 'sunrise', 'split',
                           'hassan', 'serra', 'ontario', 'georgia', 'jordan',
                           'turkey', 'reading', 'nice', 'mobile', 'victoria'})


def build_monitor(snapshot, previous=None):
    """Return a report using only collected evidence, without altering the snapshot."""
    previous = previous if isinstance(previous, dict) else {}
    at = snapshot.get('updated_at', '')
    dt_at = datetime.fromisoformat(at.replace('Z', '+00:00'))
    if dt_at.tzinfo is None:
        raise ValueError('Timestamp must have timezone')
    dt_at = dt_at.astimezone(timezone.utc)
    disamb = snapshot.get('geographic_disambiguation') or {}
    rejected = disamb.get('rejected_examples') or []
    rejected_counts = Counter(str(r.get('place', '')).strip() for r in rejected if isinstance(r, dict) and r.get('place'))
    mapped_review = []
    for point in snapshot.get('points') or []:
        if not isinstance(point, dict):
            continue
        name = str(point.get('name', '')).strip()
        if name.casefold() in REVIEW_LABELS:
            mapped_review.append({'name': name, 'category': str(point.get('category', '')),
                                  'sampled_article_count': point.get('count', 0),
                                  'review_reason': 'ambiguous_place_name_needs_manual_review'})
    mapped_review.sort(key=lambda r: (-r['sampled_article_count'], r['name']))
    row = {'at': dt_at.isoformat(), 'mapped_articles': snapshot.get('distinct_mapped_articles', 0),
           'geographic_signals': len(snapshot.get('points') or []),
           'feeds_ok': snapshot.get('query_successes', 0),
           'feeds_attempted': snapshot.get('query_attempts', 0),
           'rejected_matching_occurrences': int(disamb.get('rejected_total', 0)),
           'ambiguous_mapped_signal_count': len(mapped_review)}
    cutoff = dt_at - timedelta(days=RETENTION_DAYS)
    by_time = {}
    for item in previous.get('observations', []):
        if not isinstance(item, dict):
            continue
        try:
            t = datetime.fromisoformat(str(item['at']).replace('Z', '+00:00')).astimezone(timezone.utc)
        except (ValueError, TypeError, KeyError):
            continue
        if cutoff <= t <= dt_at:
            by_time[t.isoformat()] = item
    by_time[row['at']] = row  # idempotent for repeated collection timestamp
    history = [by_time[t] for t in sorted(by_time)][-MAX_SAMPLES:]
    recent = history[-min(len(history), 10):]
    first = recent[0] if recent else row
    def movement(field):
        return row[field] - int(first.get(field, row[field]))
    return {'schema': SCHEMA, 'version': '2.2C.2', 'retention_days': RETENTION_DAYS,
            'observations': history, 'latest': row,
            'recent_change': {'baseline_at': first['at'],
                              'geographic_signals_delta': movement('geographic_signals'),
                              'rejected_occurrences_delta': movement('rejected_matching_occurrences'),
                              'feed_successes_delta': movement('feeds_ok')},
            'rejected_place_labels_in_examples': dict(rejected_counts.most_common(15)),
            'ambiguous_mapped_review': mapped_review[:25],
            'limitations': ['This report flags possible mistakes; flags are not proven errors.',
                            'Repeated RSS items may inflate rejected matching occurrences.',
                            'Changes can reflect different feeds, article ages or publication cycles.',
                            'Monitoring does not change or remove any globe markers.']}


def update_health_file(path: Path, snapshot):
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise ValueError('data-health JSON must be an object')
    obj['geographic_quality_monitor'] = build_monitor(snapshot, obj.get('geographic_quality_monitor'))
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')
    return obj['geographic_quality_monitor']
