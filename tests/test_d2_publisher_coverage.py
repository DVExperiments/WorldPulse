"""Offline regression checks; no network or collector environment required."""
import ast
import html
import pathlib
import re
import types
import urllib.request
import xml.etree.ElementTree as ET
from unittest.mock import patch

SOURCE=pathlib.Path(__file__).resolve().parents[1]/'scripts'/'update.py'
s=SOURCE.read_text(encoding='utf8')
tree=ast.parse(s)
feed_func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='direct_fetch')
norm_func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='norm_title')
namespace={'urllib':types.SimpleNamespace(request=urllib.request),'html':html,'re':re,'ET':ET}
exec(compile(ast.Module(body=[norm_func,feed_func],type_ignores=[]),str(SOURCE),'exec'),namespace)
RDF=b'''<?xml version="1.0"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/"><item rdf:about="https://example.org/article"><title>Kenya: New initiative</title><link>https://example.org/article</link><dc:date>2026-10-18T12:00:00Z</dc:date><description>Research in Nairobi</description></item></rdf:RDF>'''
RSS=b'<rss><channel><item><title>Peru reports local news</title><link>https://example.org/peru</link><pubDate>Sun, 18 Oct 2026 12:00:00 GMT</pubDate></item></channel></rss>'
ATOM=b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Fiji schools</title><link rel="alternate" href="https://example.org/fiji"/><updated>2026-10-18T12:00:00Z</updated></entry></feed>'''
class Response:
 def __init__(self,payload):self.payload=payload
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def read(self,n):return self.payload
for raw,word in [(RDF,'Kenya'),(RSS,'Peru'),(ATOM,'Fiji')]:
 with patch.object(urllib.request,'urlopen',return_value=Response(raw)):
  rows=namespace['direct_fetch']('https://example.org/feed')
  assert len(rows)==1 and word in rows[0]['title'] and rows[0]['url'].startswith('https://'),rows
assert s.count("('AllAfrica ")==4
assert "publisher_by_editorial_region" in s
assert "geographic_mapping_review" in s
assert "source_region" not in s[s.index('def locate('):s.index('# Independent editorial feeds')]
print('PASS: RDF, RSS, Atom, source configuration, diagnostics and unchanged location matching')
