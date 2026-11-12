#!/usr/bin/env python3
"""Negative tests: no fabricated 1.1 completion or review count decreases."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1038 import check

def run(root,gates,prior,ledger):
 good=json.loads(gates.read_text('utf8'))
 assert check(root,gates,prior,ledger)['release_allowed'] is False
 def assert_fail(mutate):
  d=copy.deepcopy(good);mutate({x['id']:x for x in d['gates']})
  with tempfile.TemporaryDirectory() as tmp:
   f=Path(tmp)/'gates.json';f.write_text(json.dumps(d)+'\n')
   try:check(root,f,prior,ledger)
   except (AssertionError,KeyError,ValueError):return
   raise AssertionError('Falsely completed release gate accepted')
 tests=[
  lambda g:g['windows_runtime'].update(status='completed'),
  lambda g:g['text_completeness'].update(status='completed'),
  lambda g:g['story_contexts'].update(pending_windows_ui=0),
  lambda g:g['story_contexts'].update(reviewed_offline=80),
  lambda g:g['pronoun_contexts'].update(unresolved_count=197),
  lambda g:g['pronoun_contexts'].update(reviewed_historian_getter_calls_offline=15),
  lambda g:g['pronoun_contexts'].update(pending_windows_ui_java_getter_calls=0),
  lambda g:g['pronoun_contexts'].update(shared_her_conflict_open=False),
  lambda g:g['pronoun_contexts'].update(reviewed_rules_rows_offline=92),
  lambda g:g['draft_semantics'].update(reviewed_offline=105),
  lambda g:g['draft_semantics'].update(unresolved_count=3553),
  lambda g:g['draft_semantics'].update(gameplay_unverified_count=0),
  lambda g:g['draft_semantics'].update(new_literal_count=34),
 ]
 for mutate in tests:assert_fail(mutate)
 return {'negative_release_gate_cases':len(tests),'release_allowed':False}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);a.add_argument('--gates',type=Path,required=True)
 a.add_argument('--prior-ledger',type=Path,required=True);a.add_argument('--ledger',type=Path,required=True)
 p=a.parse_args();print(json.dumps(run(p.worktree,p.gates,p.prior_ledger,p.ledger),indent=2))
