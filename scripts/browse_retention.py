"""WorldPulse D.5: supplemental, location-unverified article browsing.
Never assigns coordinates or changes the existing 24-hour globe eligibility rule.
"""
import datetime as dt
import re
from urllib.parse import urlsplit

_MAX_EXTRA_HOURS = 72
_MAX_ITEMS = 350

class BrowseRetention:
    def __init__(self):
        self._rows = {}
        self.stats = {'recent_unlocated': 0, 'archive_24_to_72h': 0, 'excluded_older': 0, 'excluded_undated': 0}

    def add(self, item, when, now, category, reason):
        if when is None:
            self.stats['excluded_undated'] += 1
            return
        age = (now - when).total_seconds() / 3600
        if age < -(20/60) or age > _MAX_EXTRA_HOURS:
            self.stats['excluded_older'] += 1
            return
        title = (item.get('title') or '').strip()
        url = (item.get('url') or '').strip()
        try:
            parsed = urlsplit(url)
            valid = parsed.scheme == 'https' and bool(parsed.netloc) and not parsed.username and not parsed.password
        except ValueError:
            valid = False
        if not title or not valid or len(title) < 12:
            return
        # Only accept truly unmapped recent stories, or historically excluded stories.
        # This is an article browser, not a substitute for coordinates.
        is_archive = age > 24
        key = re.sub(r'\W+', ' ', title.casefold()).strip()
        if not key:
            return
        row = {
            'title': title[:260], 'url': url, 'publisher': str(item.get('publisher') or '')[:120],
            'published_at': when.isoformat(), 'category': category or 'society',
            'location_status': 'unverified', 'browse_status': 'archive' if is_archive else 'recent',
            'reason': 'outside_globe_window' if is_archive else 'no_confident_geography',
        }
        existing = self._rows.get(key)
        if existing is None or row['published_at'] > existing['published_at']:
            self._rows[key] = row

    def export(self):
        items = sorted(self._rows.values(), key=lambda r: r['published_at'], reverse=True)
        items = items[:_MAX_ITEMS]
        self.stats['recent_unlocated'] = sum(r['browse_status'] == 'recent' for r in items)
        self.stats['archive_24_to_72h'] = sum(r['browse_status'] == 'archive' for r in items)
        return items
