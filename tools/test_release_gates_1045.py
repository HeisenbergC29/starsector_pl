#!/usr/bin/env python3
"""Negative release-gate mutations: no fake PASS or lost review IDs."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1045 import validate

def run(root,gates,ledger):
    root=Path(root);gates=Path(gates);ledger=Path(ledger)
    verified=validate(root,gates,ledger)
    base=json.loads(gates.read_text('utf8'))
    with tempfile.TemporaryDirectory() as d:
        tmp=Path(d);bad=tmp/'gates.json'
        for index,mutate in enumerate((
            lambda g:g['gates'][1].__setitem__('reviewed_rules_rows_offline',254),
            lambda g:g['gates'][1].__setitem__('removed_visible_gender_variable_refs',421),
            lambda g:g['gates'][1].__setitem__('shared_her_conflict_open',False),
            lambda g:g['gates'][-1].__setitem__('native_gameplay_tested',True),
            lambda g:g['gates'][2].__setitem__('unresolved_count',0),
            lambda g:g['gates'][0].__setitem__('status','completed'),
        )):
            candidate=copy.deepcopy(base);mutate(candidate)
            bad.write_text(json.dumps(candidate)+'\n',encoding='utf8')
            try:validate(root,bad,ledger)
            except ValueError:continue
            raise AssertionError('Gate mutation accepted '+str(index))
    return {'negative_release_gate_tests_passed':6,'version_1_1_still_blocked':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
    a=p.parse_args();print(json.dumps(run(a.worktree,a.gates,a.ledger),indent=2))
