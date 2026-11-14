#!/usr/bin/env python3
"""Twelve adversarial false-completion mutations against v1.1 release gates."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1061 import metadata,audit,GATE

def run(root:Path,gates:Path,previous:Path,prior_semantic:Path,semantic:Path)->dict:
 base=json.loads(gates.read_text('utf8'));rejected={}
 def gate(d,name):return next(x for x in d['gates'] if x['id']==name)
 def reject(label,change):
  obj=copy.deepcopy(base);change(obj)
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'gates.json';f.write_text(json.dumps(obj),'utf8')
   try:metadata(f,previous)
   except (ValueError,KeyError):rejected[label]='REJECTED'
   else:raise AssertionError(('False 1.1 gate accepted',label))
 reject('Mark target 1.1 completed',lambda d:gate(d,GATE).update(status='completed'))
 reject('Fabricate Windows gameplay',lambda d:gate(d,'windows_runtime').update(native_gameplay_tested=True))
 reject('Fabricate completed API review',lambda d:gate(d,'draft_semantics').update(unresolved_count=0))
 reject('Inflate historical reviews',lambda d:gate(d,'draft_semantics').update(reviewed_offline=500))
 reject('Double count new day/day-plural mappings',lambda d:gate(d,GATE).update(new_historical_reviews=28))
 reject('Hide previously approved 391',lambda d:gate(d,GATE).update(previous_historical_reviews=0))
 reject('Fake 93 as 300 phrase tests',lambda d:gate(d,GATE).update(tested_render_variants=300))
 reject('Invent original JVM getter review',lambda d:gate(d,'pronoun_contexts').update(unresolved_count=0))
 reject('Delete a prior gate',lambda d:d['gates'].pop(5))
 reject('Duplicate a release gate',lambda d:d['gates'].append(copy.deepcopy(d['gates'][0])))
 reject('Lie about unchanged scripts',lambda d:gate(d,GATE).update(changed_jvm_executable_instructions=2))
 reject('Declare one native Windows run',lambda d:gate(d,GATE).update(native_windows_gameplay_tested=True))
 if len(rejected)!=12:raise AssertionError('Not all negative gate tests executed')
 audit(root,gates,previous,prior_semantic,semantic)
 return {'release':'1.0.61','negative_fake_gate_mutations_rejected':len(rejected),'cases':rejected}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 p.add_argument('--prior-semantic',type=Path,required=True);p.add_argument('--semantic',type=Path,required=True)
 a=p.parse_args();print(json.dumps(run(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
