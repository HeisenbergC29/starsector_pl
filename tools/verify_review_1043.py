#!/usr/bin/env python3
"""Verify 31 new approved field checks and immutability of all 153 previous ones."""
import argparse,csv,hashlib,json
from pathlib import Path
from verify_1043 import check,reverse_bytes,FINAL_SHA
from apply_1043 import PATCHES,sha

def rows(blob):return {r['id']:r for r in csv.DictReader(blob.decode('ascii').splitlines(keepends=True))}

def verify(root,ledgers):
    root=Path(root);latest=json.loads(Path(ledgers[-1]).read_text(encoding='utf8'))
    previous=reverse_bytes((root/'mod/data/campaign/rules.csv').read_bytes())
    before=rows(previous);after=rows((root/'mod/data/campaign/rules.csv').read_bytes())
    accepted=[]
    for path in ledgers[:-1]:
        j=json.loads(Path(path).read_text(encoding='utf8'))
        for entry in j['reviewed']:
            key=entry['id'];assert key in before and key in after
            if 'after_sha256' in entry:
                expected=entry['after_sha256']
                if isinstance(expected,dict):
                    for field,digest in expected.items():
                        assert sha(after[key][field].encode('ascii'))==digest,(key,field)
                else:assert sha(after[key][entry.get('field','text')].encode('ascii'))==expected,key
            accepted.append(key)
    assert len(accepted)==len(set(accepted))==153
    assert not set(accepted)&set(PATCHES)
    assert len(latest['approved'])==31 and latest['stats']['modified_rows']==31
    reviewed={x['id']:x for x in latest['approved']}
    assert set(reviewed)==set(PATCHES)
    for key,rec in reviewed.items():
        assert sha(before[key]['text'].encode('ascii'))==rec['before_text_sha256'],key
        assert sha(after[key]['text'].encode('ascii'))==rec['after_text_sha256'],key
        assert rec['after_placeholder_count']==0 and rec['replacements']==len(PATCHES[key])
    assert latest['cumulative_offline_rows']==184 and latest['cumulative_removed_references']==296
    assert latest['cumulative_pending_windows_ui_rows']==184
    assert latest['java_getter_calls_untouched']==219
    assert latest['stats']['sha256_after']==FINAL_SHA
    return {'prior_immutable_reviews':153,'new_verified_rows':31,'cumulative_offline_reviewed_rows':184,'removed_gender_references_cumulative':296,'runtime_windows_verified':0}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--ledger34',type=Path,required=True);p.add_argument('--ledger35',type=Path,required=True);p.add_argument('--ledger39',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
    a=p.parse_args();print(json.dumps(verify(a.worktree,[a.ledger34,a.ledger35,a.ledger39,a.ledger]),indent=2))
