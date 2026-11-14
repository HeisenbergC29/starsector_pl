#!/usr/bin/env python3
"""Reject adversarial false-completion states of cumulative 1.1 release gates."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1063 import metadata,audit,GATE

def run(root:Path,current:Path,previous:Path,old_semantic:Path,new_semantic:Path)->dict:
 base=json.loads(current.read_text('utf8'));negative={}
 def g(data,key):return next(x for x in data['gates'] if x['id']==key)
 def reject(name,fn):
  obj=copy.deepcopy(base);fn(obj)
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'gates.json';path.write_text(json.dumps(obj),'utf8')
   try:metadata(path,previous)
   except (ValueError,KeyError):negative[name]='REJECTED'
   else:raise AssertionError(('Falsified release status accepted',name))
 reject('fabricated 1.1 completion',lambda x:g(x,GATE).update(status='completed'))
 reject('invent native Windows gameplay',lambda x:g(x,'windows_runtime').update(native_gameplay_tested=True))
 reject('pretend all API reviewed',lambda x:g(x,'draft_semantics').update(unresolved_count=0))
 reject('reviewed history double-counted',lambda x:g(x,'draft_semantics').update(reviewed_offline=500))
 reject('lie about old 447 fingerprints',lambda x:g(x,GATE).update(previous_historical_reviews=0))
 reject('inflate 35 new reviews',lambda x:g(x,GATE).update(new_historical_reviews=100))
 reject('inflate JVM ldc audit',lambda x:g(x,GATE).update(original_jvm_ldc_uses=999))
 reject('inflate 60 composed texts',lambda x:g(x,GATE).update(rendered_dynamic_variants=900))
 reject('erase technical key restoration',lambda x:g(x,GATE).update(technical_category_keys_restored=0))
 reject('claim 1000 data files changed',lambda x:g(x,GATE).update(game_data_changed=1000))
 reject('allow JVM opcode change',lambda x:g(x,GATE).update(new_jvm_instruction_changes=1))
 reject('erase 186 pending getters',lambda x:g(x,'pronoun_contexts').update(unresolved_count=0))
 reject('delete prior release gate',lambda x:x['gates'].pop(7))
 reject('duplicate gate identifier',lambda x:x['gates'].append(dict(x['gates'][0])))
 report=audit(root,current,previous,old_semantic,new_semantic)
 if len(negative)!=14:raise ValueError('Not all fabricated release states rejected')
 return {'release':'1.0.63','false_release_gate_states_rejected':len(negative),
  'cases':negative,'legitimate_release_check':report}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 p.add_argument('--prior-semantic',required=True,type=Path);p.add_argument('--semantic',required=True,type=Path)
 a=p.parse_args();print(json.dumps(run(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
