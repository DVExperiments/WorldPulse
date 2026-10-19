import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geo_activation_d18 import simulate,load_approvals

def fixtures(tmp_path):
    url='https://example.org/news';p=[{'name':'Lagos','category':'environment','count':2,'articles':[{'url':url,'title':'Los lagos de Chile'}, {'url':'https://example.org/true','title':'Lagos flood'}]}]
    r=[{'url':url,'selected_place':'Lagos','eligible_for_future_pilot':True,'candidate_action':'eligible_shadow_withhold'}]
    m=tmp_path/'approvals.json';return url,p,r,m

def test_default_off(tmp_path):
    url,p,r,m=fixtures(tmp_path)
    out,a=simulate(p,r,m,enabled=False)
    assert out is p and a['actual_removed_entries']==0

def test_cannot_enable_without_manifest(tmp_path):
    url,p,r,m=fixtures(tmp_path)
    out,a=simulate(p,r,m,enabled=True)
    assert not a['corrections_active'] and out is p

def test_manifest_approval_and_gate(tmp_path):
    url,p,r,m=fixtures(tmp_path)
    m.write_text(json.dumps({'schema':1,'enable_live_corrections':True,'approved':[{'url':url,'place':'Lagos','manual_article_review':True,'rule':'spanish_lagos_lakes'}]}))
    out,a=simulate(p,r,m,enabled=True)
    assert a['actual_removed_entries']==1 and out[0]['count']==1 and len(out[0]['articles'])==1 and len(p[0]['articles'])==2

def test_unmatched_approved_not_removed(tmp_path):
    url,p,r,m=fixtures(tmp_path)
    m.write_text(json.dumps({'schema':1,'enable_live_corrections':True,'approved':[{'url':'https://example.org/other','place':'Lagos','manual_article_review':True,'rule':'spanish_lagos_lakes'}]}))
    out,a=simulate(p,r,m,enabled=True)
    assert a['actual_removed_entries']==0 and not a['corrections_active']

def test_wrong_rule_fails_closed(tmp_path):
    url,p,r,m=fixtures(tmp_path)
    m.write_text(json.dumps({'schema':1,'enable_live_corrections':True,'approved':[{'url':url,'place':'Lagos','manual_article_review':True,'rule':'spanish_reunion_meeting'}]}))
    assert not load_approvals(m)[0]

def test_unreviewed_approval_fails_closed(tmp_path):
    url,p,r,m=fixtures(tmp_path)
    m.write_text(json.dumps({'schema':1,'enable_live_corrections':True,'approved':[{'url':url,'place':'Lagos','manual_article_review':False,'rule':'spanish_lagos_lakes'}]}))
    assert not load_approvals(m)[0]
