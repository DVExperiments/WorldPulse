"""WorldPulse 2.0E.1: advisory geographic-subject quality audit.

Does not change any mapped place or assert that a mention is an event location.
Never treats a publisher/edition or redirect URL as evidence.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import re
import unicodedata


def fold(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(text or '').casefold()) if not unicodedata.combining(c))


def mentioned_places(text, catalogue):
    """Distinct well-formed explicit locations among E's reviewed aliases only.

    This is a *screening signal*, NOT an exhaustive gazetteer or proof of an error.
    """
    content = fold(re.sub(r'https?://\S+', ' ', str(text or '')))
    found = set()
    for name, aliases in catalogue:
        for alias in aliases:
            alias = fold(alias)
            if len(alias) < 4:
                continue
            if re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', content):
                found.add(name)
                break
    return sorted(found)


def reviewed_catalogue():
    from geo_expansion import ROWS
    # E's rows are already curated; preserve names and all distinct aliases.
    return [(row[0], row[4].split('|')) for row in ROWS]


def examine(article, catalogue):
    title = article.get('title') or ''
    description = article.get('description') or ''
    chosen = (article.get('place') or {}).get('name') or 'Unknown'
    method = article.get('geo_match') or 'unknown'
    title_names = mentioned_places(title, catalogue)
    desc_names = mentioned_places(description, catalogue)
    flags = []
    if method.startswith('description'):
        flags.append('description_only_selection')
    if method == 'url-explicit-place':
        flags.append('url_path_selection')
    if len(title_names) > 1:
        flags.append('multiple_reviewed_headline_places')
    if len(desc_names) > 1:
        flags.append('multiple_reviewed_description_places')
    if title_names and chosen not in title_names and method.startswith('description'):
        flags.append('description_overrides_named_headline_place')
    if not title_names and not desc_names:
        # Do not treat absent matches in the *limited* catalogue as proof of error.
        flags.append('not_independently_confirmed_by_e_catalogue')
    level = 'review_priority' if any(x in flags for x in ('multiple_reviewed_headline_places','description_overrides_named_headline_place')) else 'watch' if flags else 'low'
    return {'title': title[:180], 'publisher': article.get('publisher','')[:90],
            'assigned_place': chosen, 'method': method, 'risk_band': level,
            'flags': flags, 'headline_places': title_names[:8],
            'description_places': desc_names[:8], 'url': str(article.get('url',''))[:300]}


def build_audit(articles, now, sample_limit=45):
    catalogue = reviewed_catalogue()
    counts=Counter(); methods=Counter(); flags=Counter(); examples=[]
    # Per-feed article occurrences. Repeated syndicated stories remain repeated.
    for article in articles:
        result = examine(article, catalogue)
        counts[result['risk_band']]+=1
        methods[result['method']]+=1
        flags.update(result['flags'])
        if result['risk_band'] == 'review_priority' and len(examples)<sample_limit:
            examples.append(result)
    return {'schema':1, 'version':'2.0E.1', 'generated_at':now.isoformat(),
            'scope':'mapped eligible feed occurrences before deduplication',
            'mapped_occurrences_audited':sum(counts.values()),
            'risk_bands':dict(counts),'match_methods':dict(methods),
            'risk_flags':dict(flags), 'review_examples':examples,
            'policy':'Diagnostic only: existing globe pins and matching decisions are unchanged.',
            'limitations':'The reviewed alias catalogue is incomplete. A flag is not proof of an incorrect location. Named places represent possible geographic subjects, never verified event sites. Publisher and feed edition never supply location evidence.'}


def publish_audit(articles, now, data_dir):
    """Writes full audit and embeds summary in an already committed diagnostic file.

    Call AFTER embed_geo_report so E.1 fields are not accidentally overwritten.
    """
    folder=Path(data_dir)
    report=build_audit(articles,now)
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'geo-accuracy-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    target=folder/'unmatched-review.json'
    if not target.exists():
        raise RuntimeError('Cannot embed E.1 audit: unmatched-review.json missing')
    existing=json.loads(target.read_text(encoding='utf8'))
    existing['geo_accuracy_audit'] = report
    target.write_text(json.dumps(existing,ensure_ascii=False,indent=1),encoding='utf8')
    print('v2.0E.1: advisory geographic accuracy audit embedded in unmatched-review.json',flush=True)
    return report
