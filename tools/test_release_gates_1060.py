#!/usr/bin/env python3
"""Reject fabricated target-1.1 completion after 1.0.60 class-scoped UI fixes."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1060 import metadata,audit,GATE

def test(root:Path,current:Path,previous:Path)->dict:
 base=json.loads(current.read_text('utf8'));rejected={}
 def get(d,n):return next(x for x in d['gates'] if x['id']==n)
 def reject(name,fn):
  d=copy.deepcopy(base);fn(d)
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'gates.json';p.write_text(json.dumps(d),encoding='utf8')
   try:metadata(p,previous)
   except (ValueError,KeyError):rejected[name]='REJECTED'
   else:raise AssertionError(('Invalid release completion accepted',name))
 reject('falsely mark 1.1 complete',lambda d:get(d,GATE).update(status='completed'))
 reject('claim native game tested',lambda d:get(d,'windows_runtime').update(native_gameplay_tested=True))
 reject('invent completion of API history',lambda d:get(d,'draft_semantics').update(unresolved_count=0))
 reject('double count new rows as historical',lambda d:get(d,'draft_semantics').update(reviewed_offline=396))
 reject('erase 186 getter calls',lambda d:get(d,'pronoun_contexts').update(unresolved_count=0))
 reject('fake additional localized data',lambda d:get(d,GATE).update(mod_data_changed=1))
 reject('pretend Java bytecode modified',lambda d:get(d,GATE).update(new_executable_java_instruction_changes=2))
 reject('falsify original JVM offsets',lambda d:get(d,GATE).update(original_jvm_ldc_callsites=50))
 reject('falsify dynamic render variants',lambda d:get(d,GATE).update(composed_sentences_tested=50))
 reject('drop previous gate',lambda d:d['gates'].pop(1))
 reject('duplicate previous ID',lambda d:d['gates'].append(dict(d['gates'][0])))
 if len(rejected)!=11:raise AssertionError('Missing invalid release mutations')
 audit(root,current,previous)
 return {'release':'1.0.60','invalid_release_states_rejected':len(rejected),'cases':rejected}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.previous),indent=2))
