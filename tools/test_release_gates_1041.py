#!/usr/bin/env python3
"""Reject premature completion of any 1.1 acceptance gate after numeric edits."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1041 import validate

def run(root,gates):
 root=Path(root);raw=json.loads(Path(gates).read_text('utf8'))
 result=validate(root,gates)
 muts=[('numeric marked complete',lambda d:get(d,'numeric_quantities').__setitem__('status','passed')),
 ('numeric offline count inflated',lambda d:get(d,'numeric_quantities').__setitem__('reviewed_offline',78)),
 ('numeric Windows invented',lambda d:get(d,'numeric_quantities').__setitem__('pending_windows_ui',0)),
 ('numeric hash altered',lambda d:get(d,'numeric_quantities').__setitem__('review_sha256','false')),
 ('story prematurely passed',lambda d:get(d,'story_contexts').__setitem__('status','passed')),
 ('story Windows passes invented',lambda d:get(d,'story_contexts').__setitem__('pending_windows_ui',0)),
 ('pronoun count decremented',lambda d:get(d,'pronoun_contexts').__setitem__('unresolved_count',185)),
 ('her conflict falsely closed',lambda d:get(d,'pronoun_contexts').__setitem__('shared_her_conflict_open',False)),
 ('pronoun Windows passes invented',lambda d:get(d,'pronoun_contexts').__setitem__('pending_windows_ui_java_getter_calls',0)),
 ('dialogue Windows passes invented',lambda d:get(d,'pronoun_contexts').__setitem__('pending_windows_ui_rules_rows',0)),
 ('historical API semantic passes invented',lambda d:get(d,'draft_semantics').__setitem__('unresolved_count',3459)),
 ('historical API counts invented',lambda d:get(d,'draft_semantics').__setitem__('reviewed_offline',199)),
 ('Windows runtime passed',lambda d:get(d,'windows_runtime').__setitem__('status','passed')),
 ('Windows tested without proof',lambda d:get(d,'windows_runtime').__setitem__('native_gameplay_tested',True))]
 failures=[]
 with tempfile.TemporaryDirectory() as directory:
  test=Path(directory)/'gates.json'
  for name,mutation in muts:
   doc=copy.deepcopy(raw);mutation(doc);test.write_text(json.dumps(doc),encoding='utf8')
   try:validate(root,test)
   except (AssertionError,KeyError,ValueError):failures.append(name)
   else:raise AssertionError('Invalid gate accepted: '+name)
 assert len(failures)==14
 return {'baseline':result,'blocked_mutations':failures,'blocked_count':len(failures)}
def get(doc,name):return next(x for x in doc['gates'] if x['id']==name)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True)
 a=p.parse_args();print(json.dumps(run(a.worktree,a.gates),indent=2))
