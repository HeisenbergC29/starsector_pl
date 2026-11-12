#!/usr/bin/env python3
"""Reject premature 1.1 gate completion or fabricated review counts."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1040 import verify

def run(root,gates,prior,ledger):
 ref=json.loads(gates.read_text('utf8'))
 assert verify(root,gates,prior,ledger)['release_11_allowed'] is False
 def mutate(js,idx,field,val):
  item=next(x for x in js['gates'] if x['id']==idx);item[field]=val
 tests=[
  lambda d:mutate(d,'pronoun_contexts','unresolved_count',0),
  lambda d:mutate(d,'pronoun_contexts','unresolved_count',185),
  lambda d:mutate(d,'pronoun_contexts','reviewed_base_get_commodity_man_or_woman_calls_offline',13),
  lambda d:mutate(d,'pronoun_contexts','pending_windows_ui_java_getter_calls',0),
  lambda d:mutate(d,'pronoun_contexts','shared_her_conflict_open',False),
  lambda d:mutate(d,'pronoun_contexts','reviewed_rules_rows_offline',220),
  lambda d:mutate(d,'story_contexts','pending_windows_ui',0),
  lambda d:mutate(d,'draft_semantics','reviewed_offline',1220),
  lambda d:mutate(d,'draft_semantics','unresolved_count',0),
  lambda d:mutate(d,'draft_semantics','gameplay_unverified_count',0),
  lambda d:mutate(d,'windows_runtime','status','completed'),
  lambda d:d.update(target_version='1.0.40'),
 ]
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'gate.json'
  for fn in tests:
   d=copy.deepcopy(ref);fn(d);p.write_text(json.dumps(d))
   try:verify(root,p,prior,ledger)
   except (AssertionError,ValueError,KeyError,FileNotFoundError):continue
   raise AssertionError('Incorrect gate change accepted')
 return {'negative_release_gate_cases':len(tests),'release_allowed':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True);p.add_argument('--prior-ledger',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);a=p.parse_args()
 print(json.dumps(run(a.worktree,a.gates,a.prior_ledger,a.ledger),indent=2))
