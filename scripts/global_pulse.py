#!/usr/bin/env python3
"""WorldPulse F.5.1: honest, bounded analytics for the sampled news snapshot.
Run: python scripts/global_pulse.py. Standard library only.
This script NEVER rewrites news.json or story-history.json.
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit

ROOT = Path(__file__).resolve().parents[1]

def valid_url(value):
    return isinstance(value, str) and urlsplit(value).scheme in ('http', 'https') and bool(urlsplit(value).netloc)

def article_key(url):
    # Only remove conventional tracking parameters, not publisher IDs or Google News tokens.
    parts = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
         if not (k.casefold().startswith('utm_') or k.casefold() in ('fbclid', 'gclid'))]
    return urlunsplit((parts.scheme.casefold(), parts.netloc.casefold(), parts.path, urlencode(q), ''))

def analyze(news):
    points = news.get('points', [])
    if not isinstance(points, list):
        raise ValueError('news.json points must be a list')
    unique = {}  # URL-based (not semantic or syndication-level) dedupe across points
    location_articles = defaultdict(set)
    category_articles = defaultdict(set)
    publisher_articles = defaultdict(set)
    category_publishers = defaultdict(set)
    location_publishers = defaultdict(set)
    point_categories = Counter()
    for p in points:
        if not isinstance(p, dict):
            continue
        location = str(p.get('name') or 'Unspecified mapped location')
        category = str(p.get('category') or 'uncategorized')
        point_categories[category] += 1
        for a in p.get('articles', []):
            if not isinstance(a, dict) or not valid_url(a.get('url')):
                continue
            key = article_key(a['url'])
            publisher = str(a.get('publisher') or 'Unspecified publisher').strip()
            # One URL might be classified into multiple places/categories; preserve those
            # memberships but count the article once in the overall total.
            unique.setdefault(key, {'title': a.get('title', ''), 'publisher': publisher})
            location_articles[location].add(key)
            category_articles[category].add(key)
            publisher_articles[publisher].add(key)
            category_publishers[category].add(publisher)
            location_publishers[location].add(publisher)
    links = news.get('cross_border', {}).get('links', []) if isinstance(news.get('cross_border'), dict) else []
    links = links if isinstance(links, list) else []
    clusters = news.get('story_clusters', [])
    clusters = clusters if isinstance(clusters, list) else []
    cluster_status = Counter(str(c.get('coverage_status') or 'unclassified') for c in clusters if isinstance(c, dict))
    relationships = Counter(str(c.get('relationship') or 'other') for c in links if isinstance(c, dict))
    publishers = Counter({p: len(keys) for p, keys in publisher_articles.items()})
    biggest = publishers.most_common(10)
    feed_success = news.get('query_successes')
    feed_attempts = news.get('query_attempts')
    try:
        success, attempts = int(feed_success), int(feed_attempts)
        if not (0 <= success <= attempts):
            success = attempts = None
    except (TypeError, ValueError):
        success = attempts = None
    return {
        'schema': 1, 'version': '2.0F.5.1',
        'source_updated_at': news.get('updated_at'),
        'analysis_scope': 'Published mapped article previews in this rolling RSS sample',
        'overview': {
            'distinct_mapped_preview_urls': len(unique),
            'mapped_signals': len(points),
            'distinct_mapped_location_labels': len(location_articles),
            'distinct_publisher_labels': len(publisher_articles),
            'multi_publisher_story_groups': len(clusters),
            'cross_border_relationship_candidates': len(links),
            'unlocated_browse_only_records': len(news.get('unlocated_articles', [])) if isinstance(news.get('unlocated_articles'), list) else 0,
        },
        'categories': [{'name': name, 'distinct_article_urls': len(urls), 'publisher_labels': len(category_publishers[name]), 'mapped_signals': point_categories[name]}
                       for name, urls in sorted(category_articles.items(), key=lambda kv: (-len(kv[1]), kv[0]))],
        'locations': [{'name': name, 'distinct_article_urls': len(urls), 'publisher_labels': len(location_publishers[name])}
                      for name, urls in sorted(location_articles.items(), key=lambda kv: (-len(kv[1]), kv[0]))],
        'source_diversity': {
            'top_publishers_by_distinct_mapped_urls': [{'publisher': name, 'distinct_article_urls': count} for name, count in biggest],
            'top_10_url_share': round(sum(n for _, n in biggest) / len(unique), 4) if unique else 0,
            'warning': 'Publisher labels are not canonical ownership groups. Syndicated reporting may appear under several publishers; publisher count does not establish independent corroboration.'
        },
        'story_groups': {
            'count': len(clusters),
            'statuses': dict(sorted(cluster_status.items())),
            'groups': [{'id': c.get('tracking_id') or c.get('id'), 'label': c.get('label'), 'location': c.get('location'),
                        'publisher_count': c.get('publisher_count'), 'article_count': c.get('article_count'),
                        'coverage_status': c.get('coverage_status'), 'new_publishers_since_previous_observation': c.get('new_publishers_since_previous_observation', 0)}
                       for c in clusters if isinstance(c, dict)],
            'warning': 'Conservative headline groups; not canonical verified events. Coverage status compares sampled publishers seen in recent collection runs.'
        },
        'cross_border': {'count': len(links), 'types': dict(sorted(relationships.items())),
                         'warning': 'Headline-derived bilateral candidates, not verified diplomatic relationships or physical routes.'},
        'feed_health': {'status': news.get('status'), 'successful_queries': success, 'attempted_queries': attempts,
                        'reported_errors': len(news.get('errors') or {}), 'sample_is_partial': news.get('status') != 'ok'},
        'limitations': [
            'This is a sample of collected RSS headlines, not all news or real-world event counts.',
            'Only mapped published preview URLs are included in article totals; browse-only records are excluded.',
            'A URL is counted once globally, but can occur in multiple categories or locations; category/location totals need not sum to the global count.',
            'Geographic names are subjects, not verified incident coordinates.',
            'Article-URL deduplication does not guarantee removal of syndicated copies at different URLs.',
            'No claim of event severity, source political bias, truthfulness, or global news representativeness is made.'
        ]
    }

def main():
    source = ROOT / 'data/news.json'
    if not source.is_file():
        raise SystemExit('Missing data/news.json. Run the existing collector first.')
    news = json.loads(source.read_text(encoding='utf8'))
    output = analyze(news)
    dest = ROOT / 'data/global-pulse.json'
    dest.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
    print(f"WorldPulse Global Pulse F.5.1: {output['overview']['distinct_mapped_preview_urls']} unique URL previews, {output['overview']['multi_publisher_story_groups']} groups, {output['overview']['cross_border_relationship_candidates']} bilateral candidates")
    print(f'Updated {dest}')

if __name__ == '__main__':
    main()
