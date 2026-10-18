#!/usr/bin/env python3
"""WorldPulse 2.1A: compact, bounded, timestamped RSS observation archive.

Add-only integration with the existing collector. The full news.json and other
analytics/archives are never overwritten. Stdlib only.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
RETENTION_DAYS = 90
MAX_ARTICLES = 12
MAX_LOCATIONS = 45
MAX_STORIES = 12
MAX_PAIRS = 24
UTC = dt.timezone.utc


def parse_date(value):
    if not isinstance(value, str):
        raise ValueError('Snapshot missing updated_at timestamp')
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('Invalid snapshot timestamp') from exc
    if parsed.tzinfo is None:
        raise ValueError('Snapshot timestamp must include UTC offset')
    return parsed.astimezone(UTC)


def text(value, limit=150):
    return re.sub(r'\s+', ' ', value).strip()[:limit] if isinstance(value, str) else ''


def valid_url(value):
    if not isinstance(value, str) or len(value) > 2500:
        return False
    parsed = urlsplit(value)
    return parsed.scheme in ('https', 'http') and bool(parsed.netloc)


def compact(news):
    """Create an honest observation, not a claim of real-world event counts."""
    if not isinstance(news, dict) or not isinstance(news.get('points'), list):
        raise ValueError('Expected news.json with points array')
    timestamp = parse_date(news.get('updated_at'))
    if news.get('status') == 'stale' or int(news.get('query_successes') or 0) <= 0:
        raise ValueError('Stale or failed news feed must not be archived')
    points = [p for p in news['points'] if isinstance(p, dict)]
    counts = Counter()
    locations = {}
    articles = {}
    for point in points:
        category = text(point.get('category'), 40) or 'unknown'
        name = text(point.get('name'), 100) or 'Unspecified'
        row_articles = point.get('articles', [])
        if not isinstance(row_articles, list):
            row_articles = []
        counts[category] += max(0, int(point.get('count') or 0))
        key = (name, category)
        loc = locations.setdefault(key, {'name':name, 'category':category,
            'lat':point.get('lat'), 'lng':point.get('lng'), 'accuracy':text(point.get('accuracy'), 24),
            'sampled_article_count':0})
        loc['sampled_article_count'] += max(0, int(point.get('count') or 0))
        for item in row_articles:
            if not isinstance(item, dict) or not valid_url(item.get('url')):
                continue
            url = item['url']
            published = text(item.get('published_at'), 40)
            if url not in articles:
                articles[url] = {'title':text(item.get('title'), 175), 'url':url,
                    'publisher':text(item.get('publisher'), 80), 'published_at':published,
                    'subject':name, 'category':category}
    cross = news.get('cross_border') if isinstance(news.get('cross_border'), dict) else {}
    links = cross.get('links', []) if isinstance(cross.get('links', []), list) else []
    cross_types = Counter(text(c.get('relationship'), 45) or 'other' for c in links if isinstance(c,dict))
    pairs=[]
    for link in links[:MAX_PAIRS]:
        if not isinstance(link, dict): continue
        countries = link.get('countries') or link.get('pair') or []
        if isinstance(countries, list):
            countries = [text(x.get('name') if isinstance(x,dict) else x,60) for x in countries[:2]]
        else: countries=[]
        pairs.append({'countries':countries,'relationship':text(link.get('relationship'),45),
            'label':text(link.get('relationship_label') or link.get('label'),95)})
    clusters=news.get('story_clusters',[])
    if not isinstance(clusters,list):clusters=[]
    stories=[{'id':text(c.get('tracking_id') or c.get('id'),80),
              'label':text(c.get('label'),165),
              'publisher_count':c.get('publisher_count'),
              'coverage_status':text(c.get('coverage_status'),40)} for c in clusters[:MAX_STORIES] if isinstance(c,dict)]
    most_recent=sorted(articles.values(),key=lambda a:a.get('published_at',''),reverse=True)[:MAX_ARTICLES]
    return {'at':timestamp.isoformat(timespec='seconds'),
        'feed_status':text(news.get('status'),24),
        'feeds_ok':news.get('query_successes'), 'feeds_attempted':news.get('query_attempts'),
        'mapped_signals':len(points),'reported_distinct_mapped_articles':news.get('distinct_mapped_articles'),
        'sampled_article_previews':len(articles),
        'category_signal_article_counts':dict(sorted(counts.items())),
        'locations':sorted(locations.values(),key=lambda p:(-p['sampled_article_count'],p['name']))[:MAX_LOCATIONS],
        'recent_article_examples':most_recent,
        'story_groups':stories,
        'cross_border':{'candidate_count':len(links),'types':dict(sorted(cross_types.items())),'pairs':pairs}}


def write_json_atomic(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=path.parent,delete=False) as f:
        temp=Path(f.name)
        json.dump(obj,f,ensure_ascii=False,separators=(',',':'))
        f.write('\n')
    os.replace(temp,path)


def archive(news, directory, *, retention_days=RETENTION_DAYS, today=None):
    observation=compact(news)
    timestamp=parse_date(observation['at'])
    today = today or dt.datetime.now(UTC).date()
    if timestamp.date() > today + dt.timedelta(days=1):
        raise ValueError('Feed timestamp is in the future')
    if timestamp.date() < today - dt.timedelta(days=retention_days-1):
        raise ValueError('Feed snapshot is outside archive retention window')
    day=timestamp.date().isoformat()
    directory.mkdir(parents=True,exist_ok=True)
    daily=directory / (day+'.json')
    if daily.exists():
        existing=json.loads(daily.read_text(encoding='utf8'))
        if existing.get('schema')!=1 or existing.get('day')!=day or not isinstance(existing.get('snapshots'),list):
            raise ValueError(f'Invalid archive day file {daily}')
        history=existing['snapshots']
    else:
        history=[]
    new=not any(row.get('at')==observation['at'] for row in history)
    if new:
        history.append(observation)
        history.sort(key=lambda row:row['at'])
        write_json_atomic(daily,{'schema':1,'day':day,'snapshots':history})
    cutoff=today-dt.timedelta(days=retention_days-1)
    for item in directory.glob('????-??-??.json'):
        try: fileday=dt.date.fromisoformat(item.stem)
        except ValueError:continue
        if fileday < cutoff:
            item.unlink()
    days=[]
    for item in sorted(directory.glob('????-??-??.json'),reverse=True):
        try:
            fileday=dt.date.fromisoformat(item.stem)
            content=json.loads(item.read_text(encoding='utf8'))
            rows=content['snapshots']
            if not isinstance(rows,list):raise ValueError('not an array')
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
            raise ValueError(f'Invalid archive file: {item}') from exc
        if not rows:continue
        days.append({'date':fileday.isoformat(),'file':'data/archive/'+item.name,
            'snapshot_count':len(rows), 'first_at':rows[0]['at'],'last_at':rows[-1]['at']})
    index={'schema':1,'version':'2.1A.1','retention_days':retention_days,
        'description':'Historical RSS collection observations; not world event counts or complete news coverage',
        'days':days,'snapshots_total':sum(x['snapshot_count'] for x in days),
        'latest_snapshot_at':days[0]['last_at'] if days else None,
        'limitations':['Historical counts are rolling RSS samples and overlap across collection runs.',
            'Locations are news subjects, not verified incident sites.',
            'Article examples are capped; full headlines are not retained in this archive.',
            'Cross-border pairings are headline-derived candidates.']}
    index_path=directory/'index.json'
    if not index_path.exists() or json.loads(index_path.read_text(encoding='utf8'))!=index:
        write_json_atomic(index_path,index)
    return new, index


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--news',type=Path,default=ROOT/'data/news.json')
    parser.add_argument('--output',type=Path,default=ROOT/'data/archive')
    args=parser.parse_args()
    news=json.loads(args.news.read_text(encoding='utf8'))
    new,index=archive(news,args.output)
    print(f"WorldPulse 2.1A: {'archived' if new else 'skipped duplicate'}; {index['snapshots_total']} observations over {len(index['days'])} days")

if __name__=='__main__':
    main()
