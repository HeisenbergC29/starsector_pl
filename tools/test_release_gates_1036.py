#!/usr/bin/env python3
"""Keep unresolved Windows/UI and shared-pronoun checks fail-closed."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1036 import check

def test(root,gates,prior_api,api,prior_rules,rules):
 d=json.loads(gates.read_text('utf8'))
 assert check(root,gates,prior_api,api,prior_rules,rules)['release_11_allowed'] is False
 bad=0
 with tempfile.TemporaryDirectory() as folder:
  p=Path(folder)/'gates.json'
  def fail(edit):
   nonlocal bad
   v=copy.deepcopy(d);g={x['id']:x for x in v['gates']}
   edit(v,g)
   p.write_text(json.dumps(v)+'\n','utf8')
   try:check(root,p,prior_api,api,prior_rules,rules)
   except (AssertionError,RuntimeError,KeyError):bad+=1;return
   raise AssertionError('unsafe release-gate mutation accepted')
  edits=[
   lambda d,g:g['pronoun_contexts'].update(unresolved_count=0),
   lambda d,g:g['pronoun_contexts'].update(total_jvm_getter_calls=218),
   lambda d,g:g['pronoun_contexts'].update(reviewed_reflexive_calls_offline=219),
   lambda d,g:g['pronoun_contexts'].update(shared_her_conflict_open=False),
   lambda d,g:g['pronoun_contexts'].update(pending_windows_ui_java_getter_calls=0),
   lambda d,g:g['pronoun_contexts'].update(reviewed_rules_rows_offline=219),
   lambda d,g:g['draft_semantics'].update(reviewed_offline=3658),
   lambda d,g:g['draft_semantics'].update(unresolved_count=0),
   lambda d,g:g['draft_semantics'].update(gameplay_unverified_count=0),
   lambda d,g:g['story_contexts'].update(pending_windows_ui=0),
   lambda d,g:g['windows_runtime'].update(status='verified'),
   lambda d,g:g['text_completeness'].update(status='verified'),
   lambda d,g:d.update(target_version='1.0.36'),
  ]
  for e in edits:fail(e)
  assert bad==len(edits)==13
  try:check(root,gates,prior_api,api,prior_rules,rules,strict=True)
  except RuntimeError:bad+=1
  else:raise AssertionError('strict premature 1.1 passed')
 return {'negative_gate_tests_passed':bad,'release_11_allowed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--prior-api-ledger',type=Path,required=True)
 p.add_argument('--api-ledger',type=Path,required=True);p.add_argument('--prior-rules-ledger',type=Path,required=True)
 p.add_argument('--rules-ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.prior_api_ledger,a.api_ledger,a.prior_rules_ledger,a.rules_ledger),indent=2))
