#!/usr/bin/env python3
"""Mutation tests that reject premature 1.1 approval and dishonest review totals."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1047 import audit

def test(root,gates,previous,ledger,fixture=False):
    if not audit(root,gates,previous,ledger,fixture)['target_1_1_blocked']:raise AssertionError('Base release improperly approved')
    baseline=json.loads(Path(gates).read_text('utf8'))
    changes=[
      ('incorrect_review_count',lambda d:next(x for x in d['gates'] if x['id']=='draft_semantics').__setitem__('reviewed_offline',181)),
      ('fake_windows_test',lambda d:next(x for x in d['gates'] if x['id']=='windows_runtime').__setitem__('native_gameplay_tested',True)),
      ('close_shared_her',lambda d:next(x for x in d['gates'] if x['id']=='pronoun_contexts').__setitem__('shared_her_conflict_open',False)),
      ('pretend_getter_repaired',lambda d:next(x for x in d['gates'] if x['id']=='pronoun_contexts').__setitem__('unresolved_count',0)),
      ('mark_numeric_complete',lambda d:next(x for x in d['gates'] if x['id']=='api_numeric_1047').__setitem__('status','completed')),
      ('remove_release_gate',lambda d:d['gates'].pop()),
    ]
    with tempfile.TemporaryDirectory(prefix='st1047_gates_') as t:
        p=Path(t)/'gates.json'
        for name,fun in changes:
            d=copy.deepcopy(baseline);fun(d);p.write_text(json.dumps(d)+'\n')
            try:audit(root,p,previous,ledger,fixture)
            except (ValueError,AssertionError,KeyError):pass
            else:raise AssertionError('Gate incorrectly accepted '+name)
    return {'release':'1.0.47','negative_release_gate_mutations_rejected':len(changes),
            'review_count':180,'windows_gameplay_verified':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--ledger',type=Path,required=True);p.add_argument("--fixture",action="store_true");a=p.parse_args()
    print(json.dumps(test(a.worktree,a.gates,a.previous,a.ledger,a.fixture),indent=2))
