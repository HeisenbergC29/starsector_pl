#!/usr/bin/env python3
"""Release gates 1.1 must fail closed against invented runtime or inflated review counts."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1042 import validate

def get(d,name):return next(x for x in d['gates'] if x['id']==name)

def test(root,gates):
 root=Path(root);raw=json.loads(Path(gates).read_text('utf8'));out=validate(root,gates)
 changes=[
 ('punctuation marked complete',lambda d:get(d,'punctuation_regression').__setitem__('status','passed')),
 ('punctuation count inflated',lambda d:get(d,'punctuation_regression').__setitem__('reviewed_offline',16)),
 ('punctuation Windows passes invented',lambda d:get(d,'punctuation_regression').__setitem__('pending_windows_ui',0)),
 ('punctuation SHA altered',lambda d:get(d,'punctuation_regression').__setitem__('plan_sha256','fake')),
 ('numeric Windows passes invented',lambda d:get(d,'numeric_quantities').__setitem__('pending_windows_ui',0)),
 ('numeric reviews inflated',lambda d:get(d,'numeric_quantities').__setitem__('reviewed_offline',78)),
 ('story runtime passes invented',lambda d:get(d,'story_contexts').__setitem__('pending_windows_ui',0)),
 ('unreviewed getters artificially reduced',lambda d:get(d,'pronoun_contexts').__setitem__('unresolved_count',185)),
 ('her conflict falsely closed',lambda d:get(d,'pronoun_contexts').__setitem__('shared_her_conflict_open',False)),
 ('unreviewed dialogue Windows passes invented',lambda d:get(d,'pronoun_contexts').__setitem__('pending_windows_ui_rules_rows',0)),
 ('unreviewed getters Windows passes invented',lambda d:get(d,'pronoun_contexts').__setitem__('pending_windows_ui_java_getter_calls',0)),
 ('API semantic count falsely reduced',lambda d:get(d,'draft_semantics').__setitem__('unresolved_count',3535)),
 ('API semantic count falsely elevated',lambda d:get(d,'draft_semantics').__setitem__('reviewed_offline',123)),
 ('Windows runtime falsely passed',lambda d:get(d,'windows_runtime').__setitem__('native_gameplay_tested',True)),
 ]
 successes=[]
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'gates.json'
  for name,fn in changes:
   d=copy.deepcopy(raw);fn(d);p.write_text(json.dumps(d))
   try:validate(root,p)
   except (AssertionError,KeyError,ValueError):successes.append(name)
   else:raise AssertionError('Gate tamper accepted: '+name)
 assert len(successes)==14
 return {'baseline':out,'blocked_cases':len(successes),'test_names':successes}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);a.add_argument('--gates',type=Path,required=True);o=a.parse_args();print(json.dumps(test(o.worktree,o.gates),indent=2))
