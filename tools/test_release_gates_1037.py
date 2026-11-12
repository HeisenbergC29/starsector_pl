#!/usr/bin/env python3
"""Reject premature 1.1 release declarations and stale semantic-review ledgers."""
import copy,json,tempfile
from pathlib import Path
from check_release_gates_1037 import check

def reject(fn):
 try:fn()
 except (AssertionError,KeyError,ValueError):return
 raise AssertionError('1.1 gate accepted invalid evidence')

def run(root,gates,old,new):
 assert check(root,gates,old,new)['release_allowed'] is False
 template=json.loads(gates.read_text('utf8'));tests=0
 with tempfile.TemporaryDirectory() as td:
  file=Path(td)/'gates.json'
  def mutate(fn):
   obj=copy.deepcopy(template);fn({r['id']:r for r in obj['gates']},obj)
   file.write_text(json.dumps(obj)+'\n',encoding='utf8')
   reject(lambda:check(root,file,old,new))
  cases=[
   lambda d,o:d['story_contexts'].update(pending_windows_ui=80),
   lambda d,o:d['pronoun_contexts'].update(unresolved_count=211),
   lambda d,o:d['pronoun_contexts'].update(pending_windows_ui_java_getter_calls=218),
   lambda d,o:d['pronoun_contexts'].update(shared_her_conflict_open=False),
   lambda d,o:d['draft_semantics'].update(unresolved_count=3574),
   lambda d,o:d['draft_semantics'].update(gameplay_unverified_count=3683),
   lambda d,o:d['draft_semantics'].update(reviewed_offline=84),
   lambda d,o:d['windows_runtime'].update(status='completed'),
   lambda d,o:o.update(target_version='1.0.37')]
  for fn in cases:mutate(fn);tests+=1
  broken=json.loads(new.read_text('utf8'));broken['reviewed'][-1]['row_sha256']='0'*64
  f=Path(td)/'badledger.json';f.write_text(json.dumps(broken));reject(lambda:check(root,gates,old,f));tests+=1
 return {'rejected_premature_gates':tests,'native_gameplay':False}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path);p.add_argument('--prior-ledger',required=True,type=Path);p.add_argument('--ledger',required=True,type=Path)
 a=p.parse_args();print(json.dumps(run(a.worktree,a.gates,a.prior_ledger,a.ledger),indent=2))
