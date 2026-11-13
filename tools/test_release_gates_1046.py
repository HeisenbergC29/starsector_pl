#!/usr/bin/env python3
"""Negative tests for release-gate tampering. Never simulate Windows gameplay success."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1046 import validate

def run(root,gates,prior,ledger,strict_go=True):
    source=json.loads(Path(gates).read_text())
    assert validate(root,gates,prior,ledger,strict_go=strict_go)['release_1_1_blocked']
    mutants=[]
    def mut(key,field,value):
        x=copy.deepcopy(source)
        next(g for g in x['gates'] if g['id']==key)[field]=value
        mutants.append(x)
    mut('draft_semantics','reviewed_offline',3658)
    mut('draft_semantics','unresolved_count',0)
    mut('pronoun_contexts','unresolved_count',0)
    mut('pronoun_contexts','shared_her_conflict_open',False)
    mut('api_contexts_1046','pending_windows_ui',0)
    mut('story_contexts','pending_windows_ui',0)
    mut('windows_runtime','native_gameplay_tested',True)
    mut('text_completeness','status','completed')
    mutants.append({**source,'gates':[g for g in source['gates'] if g['id']!='api_contexts_1046']})
    passes=0
    with tempfile.TemporaryDirectory() as d:
        file=Path(d)/'gates.json'
        for x in mutants:
            file.write_text(json.dumps(x))
            try:validate(root,file,prior,ledger,strict_go=strict_go)
            except (ValueError,AssertionError):passes+=1
            else:raise AssertionError('Invalid release state accepted')
    return {'negative_gate_cases':len(mutants),'blocked_cases':passes,'native_gameplay_tested':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--ledger',type=Path,required=True);p.add_argument('--fixture',action='store_true')
    a=p.parse_args()
    print(json.dumps(run(a.worktree,a.gates,a.previous,a.ledger,strict_go=not a.fixture),indent=2))
