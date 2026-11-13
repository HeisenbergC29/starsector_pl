#!/usr/bin/env python3
"""Mutation/regression checks for only approved rules.csv text edits."""
import argparse,json
from pathlib import Path
from apply_1043 import patch_bytes,sha,PREV_SHA,PATCHES,rows_with_spans
from verify_1043 import check,reverse_bytes

def must_fail(call,label):
    try:call()
    except (AssertionError,ValueError,KeyError):return
    raise AssertionError('Accepted prohibited change: '+label)

def run(root):
    root=Path(root)
    installed=(root/'mod/data/campaign/rules.csv').read_bytes();prior=reverse_bytes(installed)
    assert sha(prior)==PREV_SHA and patch_bytes(prior)[0]==installed
    assert check(root)['modified_rows']==31
    tests=[]
    def reject(label,call):must_fail(call,label);tests.append(label)
    reject('source modified unrelated field',lambda:patch_bytes(prior.replace(b'defaultLeave,',b'defaultLeaveHACK,',1)))
    reject('source truncated',lambda:patch_bytes(prior[:-100]))
    reject('source forced nonASCII',lambda:patch_bytes(prior+b'\xc4'))
    reject('source wrong newline',lambda:patch_bytes(prior.replace(b'\r\n',b'\n',1),check_sha=False))
    duplicate=next(prior[a:b] for a,b,row in rows_with_spans(prior)[1:] if row[0]=='TTmarketPostWeirdHMbegin')
    reject('duplicate target row ID',lambda:patch_bytes(prior+b'\r\n'+duplicate,check_sha=False))
    reject('missing expected phrase',lambda:patch_bytes(prior.replace(b'$HisOrHer spojrzenie',b'jego spojrzenie',1),check_sha=False))
    reject('wrong letter case in target',lambda:patch_bytes(prior.replace(b'ktory sklada $hisOrHer dlonie w powitaniu.',b'ktory sklada $hisOrher dlonie w powitaniu.',1),check_sha=False))
    reject('injected duplicate target phrase',lambda:patch_bytes(prior.replace(b'$HisOrHer spojrzenie',b'$HisOrHer spojrzenie $HisOrHer spojrzenie',1),check_sha=False))
    reject('modified installed CSV',lambda:reverse_bytes(installed.replace(b'Spojrzenie rozmowcy',b'Spojrzenie osoby',1)))
    reject('modified CSV option',lambda:reverse_bytes(installed.replace(b'defaultLeave:Odejdz',b'defaultLeave:Odejdz:bad',1)))
    reject('removed accepted new phrase',lambda:reverse_bytes(installed.replace(b'Kropla potu splywa po twarzy oficera',b'Kropla potu splywa',1)))
    reject('mutated installed entire file',lambda:reverse_bytes(installed+b'x'))
    return {'positive_round_trip':True,'mutations_rejected':len(tests),'rejected_scenarios':tests}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
