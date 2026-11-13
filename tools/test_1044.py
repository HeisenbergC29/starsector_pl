#!/usr/bin/env python3
"""Regression and fail-closed mutations for controlled 1.0.44 dialogue delta."""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
from apply_1044 import PATCHES,patch_bytes,sha
from verify_1044 import check,reverse_bytes,FINAL_SHA
from apply_1034 import rows_with_spans

def test(root):
    root=Path(root);original=reverse_bytes((root/'mod/data/campaign/rules.csv').read_bytes())
    applied,stats,ledger=patch_bytes(original)
    if applied!=(root/'mod/data/campaign/rules.csv').read_bytes():raise ValueError('Non-reproducible 1.0.44 bytes')
    old=rows_with_spans(original);new=rows_with_spans(applied)
    if len(old)!=len(new):raise ValueError('CSV records changed')
    different=[]
    for (_,_,r),(_,_,s) in zip(old,new):
        if r!=s:
            changed=[i for i in range(7) if r[i]!=s[i]]
            if changed!=[4] or r[0] not in PATCHES:raise ValueError(('Wrong field changed',r[0],changed))
            different.append(r[0])
    if set(different)!=set(PATCHES):raise ValueError('Missing or repeated patch')
    if original.count(b'\r\n')!=applied.count(b'\r\n'):raise ValueError('CRLF count changed')
    # Negative cases: tampered version, non-ASCII, LF, stale edited phrase, broken CSV row, missing target row.
    cases=[original+b' ', original.replace(b'\r\n',b'\n',1),original.replace(b'GAKA_TTStart',b'GAKA_TTStara',1),original.replace(b'podchodzi do ciebie $manOrWoman',b'podchodzi do ciebie $manOrXoman',1), original.replace(b'GAKA_TTStart',b'GAKA_TTStart,',1),original+b'\xff']
    rejected=0
    for case in cases:
        try:patch_bytes(case)
        except (ValueError,AssertionError,csv.Error):rejected+=1
        else:raise ValueError('Negative case accepted')
    assert rejected==len(cases)
    assert check(root)['rows_changed']==25
    return {'version':'1.0.44','changed_rows':len(different),'exact_replacements':stats['fragments_changed'],'removed_placeholders':stats['gender_references_removed'],'negative_tests_passed':rejected,'only_text_fields_changed':True,'reconstructed_prior_sha':sha(original)}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);v=a.parse_args();print(json.dumps(test(v.worktree),indent=2))