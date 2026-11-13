#!/usr/bin/env python3
"""Mutational checks for 1.0.48 incomplete-release gates and review ledger."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1048 import audit

def test(root,gates,previous,ledger):
    root=Path(root);gates=Path(gates);previous=Path(previous);ledger=Path(ledger)
    source=json.loads(gates.read_text('utf8'));cases=[]
    def attempt(name,mut):
        item=copy.deepcopy(source);mut(item)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'gates.json';p.write_text(json.dumps(item),encoding='utf8')
            try:audit(root,p,previous,ledger)
            except (ValueError,KeyError,TypeError):cases.append(name)
            else:raise AssertionError(('Invalid release claim accepted',name))
    by=lambda x,key:next(y for y in x['gates'] if y['id']==key)
    attempt('premature windows completion',lambda x:by(x,'windows_runtime').update(status='completed',native_gameplay_tested=True))
    attempt('premature API 1.1 release',lambda x:by(x,'draft_semantics').update(status='completed',unresolved_count=0))
    attempt('forged pronoun count',lambda x:by(x,'pronoun_contexts').update(unresolved_count=0))
    attempt('concealed shared her',lambda x:by(x,'pronoun_contexts').update(shared_her_conflict_open=False))
    attempt('extra recensions invented',lambda x:by(x,'draft_semantics').update(reviewed_offline=209,unresolved_count=3449))
    attempt('old review rewritten',lambda x:by(x,'api_numeric_1047').update(corrected_api_rows=15))
    attempt('reduced current batch',lambda x:by(x,'api_numeric_1048').update(corrected_api_rows=28))
    attempt('missing gate',lambda x:x['gates'].pop())
    if len(cases)!=8:raise ValueError(('Incomplete negative tests',cases))
    return {'negative_release_claims_rejected':len(cases),'cases':cases}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path)
    p.add_argument('--previous',required=True,type=Path);p.add_argument('--ledger',required=True,type=Path)
    a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.previous,a.ledger),indent=2))
