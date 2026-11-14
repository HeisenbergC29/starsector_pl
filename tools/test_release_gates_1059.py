#!/usr/bin/env python3
"""Mutation test for false 1.1 completion after 1.0.59 UI translation."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1059 import metadata,audit,NEW_ID

def test(root:Path,gates:Path,previous:Path):
 base=json.loads(Path(gates).read_text('utf8'));bad={}
 def gate(doc,id):return next(x for x in doc['gates'] if x['id']==id)
 def reject(name,fn):
  d=copy.deepcopy(base);fn(d)
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'gate.json';p.write_text(json.dumps(d),encoding='utf8')
   try:metadata(p,previous)
   except (ValueError,KeyError):bad[name]='REJECTED'
   else:raise AssertionError(('Falsified gate was accepted',name))
 reject('complete issue without gameplay',lambda d:gate(d,NEW_ID).update(status='completed'))
 reject('pretend Windows test passed',lambda d:gate(d,'windows_runtime').update(native_gameplay_tested=True))
 reject('erase API debt',lambda d:gate(d,'draft_semantics').update(unresolved_count=0))
 reject('inflate API reviews',lambda d:gate(d,'draft_semantics').update(reviewed_offline=397))
 reject('erase remaining JVM getters',lambda d:gate(d,'pronoun_contexts').update(unresolved_count=0))
 reject('fake translated data',lambda d:gate(d,NEW_ID).update(data_file_changes=1))
 reject('fake bytecode safety',lambda d:gate(d,NEW_ID).update(new_executable_bytecode_changes=2))
 reject('falsify JVM evidence',lambda d:gate(d,NEW_ID).update(jvm_callsites_verified_original=50))
 reject('drop prior review',lambda d:d['gates'].pop(3))
 reject('duplicate gate',lambda d:d['gates'].append(dict(d['gates'][0])))
 audit(root,gates,previous)
 return {'release':'1.0.59','invalid_release_states_rejected':len(bad),'details':bad}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.previous),indent=2))
