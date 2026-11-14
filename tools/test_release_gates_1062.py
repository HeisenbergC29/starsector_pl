#!/usr/bin/env python3
"""Adversarial v1.1 release-gate false completion tests for 1.0.62."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1062 import metadata,audit,GATE

def test(root:Path,current:Path,previous:Path,old_semantic:Path,new_semantic:Path)->dict:
 base=json.loads(current.read_text('utf8'));bad={}
 def gate(x,key):return next(a for a in x['gates'] if a['id']==key)
 def reject(name,fn):
  mutated=copy.deepcopy(base);fn(mutated)
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'gates.json';p.write_text(json.dumps(mutated),'utf8')
   try:metadata(p,previous)
   except (ValueError,KeyError):bad[name]='REJECTED'
   else:raise AssertionError(('Bad fake release gate passed',name))
 reject('claim 1.1 completed',lambda x:gate(x,GATE).update(status='completed'))
 reject('invent Windows gameplay test',lambda x:gate(x,'windows_runtime').update(native_gameplay_tested=True))
 reject('remove unresolved API entries',lambda x:gate(x,'draft_semantics').update(unresolved_count=0))
 reject('inflate reviewed API count',lambda x:gate(x,'draft_semantics').update(reviewed_offline=450))
 reject('double count new original JVM literals',lambda x:gate(x,GATE).update(new_historical_reviews=33))
 reject('erase 416 previous history',lambda x:gate(x,GATE).update(previous_historical_reviews=0))
 reject('inflate 42 confirmed JVM calls',lambda x:gate(x,GATE).update(original_jvm_ldc_verified=50))
 reject('pretend technical category correction absent',lambda x:gate(x,GATE).update(restored_technical_category_strings=0))
 reject('fabricate 100 compositional tests',lambda x:gate(x,GATE).update(tested_render_variants=100))
 reject('erase pending getter review',lambda x:gate(x,'pronoun_contexts').update(unresolved_count=0))
 reject('delete previous gate',lambda x:x['gates'].pop(4))
 reject('duplicate gate',lambda x:x['gates'].append(copy.deepcopy(x['gates'][0])))
 reject('accept executable JVM modifications',lambda x:gate(x,GATE).update(changed_jvm_executable_instructions=1))
 reject('lie about native UI testing',lambda x:gate(x,GATE).update(native_windows_gameplay_tested=True))
 audit(root,current,previous,old_semantic,new_semantic)
 if len(bad)!=14:raise AssertionError('Wrong number of false release tests')
 return {'release':'1.0.62','false_release_states_rejected':len(bad),'cases':bad}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 p.add_argument('--prior-semantic',required=True,type=Path);p.add_argument('--semantic',required=True,type=Path)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
