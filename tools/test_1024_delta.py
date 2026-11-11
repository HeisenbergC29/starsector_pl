#!/usr/bin/env python3
"""Negative regression fixtures: reject modified historical mappings and technical IDs."""
import tempfile,csv
from pathlib import Path
from apply_1024 import OBF,API
from verify_1024_ui import rows,check

FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def save(p,r):
    with p.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(r)

def fail(fn):
    try:fn()
    except AssertionError:return
    raise AssertionError('failed to reject deliberately corrupted translation map')

def run(root):
    obf=root/'buildtools/NARZEDZIA_OBF';a=obf/'TLUMACZENIA_OBF_10123.csv';b=obf/'TLUMACZENIA_OBF_10124.csv'
    old,new=rows(a),rows(b)
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)
        mutate=[r.copy() for r in new];mutate[0]['polish_ascii_draft']='BROKEN-OLD'
        p=t/'changed_old.csv';save(p,mutate)
        fail(lambda:check(a,p,OBF,3185))
        mutate=[r.copy() for r in new];mutate[-1]['polish_ascii_draft']='BROKEN-NEW'
        p=t/'changed_new.csv';save(p,mutate)
        fail(lambda:check(a,p,OBF,3185))
        mutate=[r.copy() for r in new];mutate.append(mutate[-1].copy())
        p=t/'duplicate.csv';save(p,mutate)
        fail(lambda:check(a,p,OBF,3185))
        assert not any(k in API['com.fs.starfarer.api.campaign.FleetAssignment'] for k in ('FOLLOW','HOLD','ATTACK_LOCATION'))
    print('NEGATIVE TESTS PASS: historical text mutation, unapproved new translation and duplicate mapping rejected; enum IDs untouched')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);run(p.parse_args().worktree)