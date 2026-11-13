#!/usr/bin/env python3
"""Negative mutation tests of incomplete 1.1 release gates for 1.0.49."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1049 import audit
def run(root,gates,previous,ledger):
 root=Path(root);data=json.loads(Path(gates).read_text('utf8'));failures=[]
 def attempt(name,mut):
  d=copy.deepcopy(data);mut(d)
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'mutated.json';p.write_text(json.dumps(d))
   try:audit(root,p,previous,ledger)
   except (ValueError,KeyError):failures.append(name)
   else:raise AssertionError('Invalid 1.1 state accepted: '+name)
 def g(d,key):return next(x for x in d['gates'] if x['id']==key)
 attempt('pretend_gameplay_completed',lambda d:g(d,'windows_runtime').update(native_gameplay_tested=True))
 attempt('close_unfinished_her',lambda d:g(d,'pronoun_contexts').update(shared_her_conflict_open=False))
 attempt('erase_remaining_getters',lambda d:g(d,'pronoun_contexts').update(unresolved_count=0))
 attempt('invent_reviewed_API',lambda d:g(d,'draft_semantics').update(reviewed_offline=3658,unresolved_count=0))
 attempt('drop_legacy_gate',lambda d:d['gates'].pop(0))
 attempt('mark_version_1_1_ready',lambda d:g(d,'text_completeness').update(status='completed'))
 attempt('falsify_suffix_rule',lambda d:g(d,'api_grammar_1049').update(added_api_rows=0))
 attempt('change_review_ledger',lambda d:g(d,'draft_semantics').update(review_ledger='fake.json'))
 if len(failures)!=8:raise AssertionError('Incomplete negative gate tests')
 actual=audit(root,gates,previous,ledger)
 return {'negative_gate_mutations_rejected':len(failures),'cases':failures,'target_1_1_still_blocked':actual['target_1_1_blocked']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True)
 p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(run(a.worktree,a.gates,a.previous,a.ledger),indent=2))
