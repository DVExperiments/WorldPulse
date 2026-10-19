import sys, pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from geo_integrity_d12 import isolate, summarize

def test_domain_stripping():
    a={'description':'Markets in Asia discussed - Vietnam.vn','publisher':'Vietnam.vn','source_url':'https://vietnam.vn'}
    clean,removed=isolate(a)
    assert 'Vietnam.vn' not in clean and removed

def test_preserves_genuine_context():
    a={'description':'A flood in Vietnam damaged roads. Vietnam.vn','publisher':'Vietnam.vn','source_url':'https://vietnam.vn'}
    clean,_=isolate(a)
    assert 'in Vietnam damaged roads' in clean

def test_not_strip_other_domains():
    a={'description':'An article cites example.org and Vietnam.vn','publisher':'Vietnam.vn','source_url':'https://vietnam.vn'}
    clean,_=isolate(a)
    assert 'example.org' in clean and 'Vietnam.vn' not in clean

def test_summary_dedup():
    row={'url':'https://example.org/a','current_place':'Vietnam','classification':'lost_after_isolation','title':'A'}
    d=summarize([row,row]);assert d['distinct_url_location_pairs_checked']==1

def test_other_publishers():
    a={'description':'City transport update - Kenya Times','publisher':'Kenya Times','source_url':'https://kenyatimes.co.ke'}
    clean,removed=isolate(a)
    assert 'Kenya Times' not in clean and removed
