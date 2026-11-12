#!/usr/bin/env python3
"""Ensure all 62 newly-reviewed dialogue rows are exact and older 91 remain."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from verify_1039 import revert,parse
from apply_1039 import SOURCE,NEW_SHA,PATCHES,PRONOUN

def digest(s):return hashlib.sha256(s.encode('ascii')).hexdigest()

def verify(root,old34,old35,ledger):
    a,b,c=[json.loads(p.read_text('utf8')) for p in (old34,old35,ledger)]
    assert a['reviewed_rows']==27 and b['reviewed_rows']==64 and c['reviewed_rows']==62
    assert a['removed_visible_pronoun_placeholders']==75 and b['removed_visible_pronoun_placeholders']==108 and c['removed_visible_pronoun_placeholders']==77
    prev34={r['id'] for r in a['reviewed']};prev35={r['id'] for r in b['reviewed']}
    cur={r['id'] for r in c['reviewed']}
    assert len(prev34)==27 and len(prev35)==64 and len(cur)==62
    assert not (prev34 & prev35 or prev34 & cur or prev35 & cur)
    assert cur==set(PATCHES)
    assert c['rules_sha256_before']==b['rules_sha256_after']
    assert c['rules_sha256_after']==NEW_SHA
    assert c['cumulative_offline_rows']==153 and c['cumulative_removed_references']==260
    assert c['cumulative_pending_windows_ui_rows']==153
    data=(root/'mod'/SOURCE).read_bytes()
    old={r['id']:r for r in parse(revert(data))};new={r['id']:r for r in parse(data)}
    for entry in c['reviewed']:
        key=entry['id'];assert key in old and key in new
        assert entry['before_sha256']==digest(old[key]['text'])
        assert entry['after_sha256']==digest(new[key]['text'])
        assert entry['exact_edits']==len(PATCHES[key])
        assert entry['removed_variable_references']==len(PRONOUN.findall(old[key]['text'].encode('ascii')))
        assert not PRONOUN.search(new[key]['text'].encode('ascii'))
        assert entry['windows_gameplay']=='not_tested'
    for group in (a,b):
        for entry in group['reviewed']:
            key=entry['id'];field=entry.get('field','text');fields=entry.get('fields',[field])
            for field in fields:
                h=entry['after_sha256'] if isinstance(entry['after_sha256'],str) else entry['after_sha256'][field]
                assert digest(new[key][field])==h,('Prior reviewed dialogue drift',key,field)
    return {'new_reviewed_rows':62,'old_reviewed_rows_preserved':91,'cumulative_reviewed_rows':153,'new_gender_variables_removed':77,'cumulative_removed':260,'pending_windows_ui_rows':153}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--ledger34',type=Path,required=True);p.add_argument('--ledger35',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
    a=p.parse_args();print(json.dumps(verify(a.worktree,a.ledger34,a.ledger35,a.ledger),indent=2))
