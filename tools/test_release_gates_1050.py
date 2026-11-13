#!/usr/bin/env python3
"""Eight negative release-gate mutations intentionally rejected by 1.0.50 verifier."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1050 import audit
def run(root,gates,previous,ledger):
 source=json.loads(Path(gates).read_text('utf8'));rejected=[]
 def get(obj,key):return next(x for x in obj['gates'] if x['id']==key)
 def attempt(name,modify):
  obj=copy.deepcopy(source);modify(obj)
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'gates.json';f.write_text(json.dumps(obj))
   try:audit(root,f,previous,ledger)
   except (ValueError,KeyError):rejected.append(name)
   else:raise AssertionError('Invalid release state accepted: '+name)
 attempt('pretend_windows_gameplay',lambda d:get(d,'windows_runtime').update(native_gameplay_tested=True))
 attempt('close_shared_her_conflict',lambda d:get(d,'pronoun_contexts').update(shared_her_conflict_open=False))
 attempt('claim_all_getters_reviewed',lambda d:get(d,'pronoun_contexts').update(unresolved_count=0))
 attempt('claim_all_api_semantics_reviewed',lambda d:get(d,'draft_semantics').update(reviewed_offline=3658,unresolved_count=0))
 attempt('drop_historical_gate',lambda d:d['gates'].pop(0))
 attempt('falsely_close_completeness',lambda d:get(d,'text_completeness').update(status='completed'))
 attempt('invent_time_fragment_counts',lambda d:get(d,'api_time_fragments_1050').update(added_api_rows=0))
 attempt('fake_semantic_ledger',lambda d:get(d,'draft_semantics').update(review_ledger='fake.json'))
 if len(rejected)!=8:raise ValueError('Incomplete negatives')
 valid=audit(root,gates,previous,ledger)
 return {'negative_release_gate_mutations_rejected':8,'cases':rejected,'target_1_1_blocked':valid['target_1_1_blocked']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True)
 p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(run(a.worktree,a.gates,a.previous,a.ledger),indent=2))
