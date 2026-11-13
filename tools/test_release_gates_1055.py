#!/usr/bin/env python3
"""Explicitly reject fake v1.1 completion and false documentation counts."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1055 import audit

def run(root,gates,previous,ledger):
 base=json.loads(Path(gates).read_text('utf8'));rejections={}
 def alter(case,change):
  g=copy.deepcopy(base);change(g)
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'gates.json';f.write_text(json.dumps(g))
   try:audit(root,f,previous,ledger)
   except (ValueError,KeyError):rejections[case]='REJECTED'
   else:raise AssertionError(('Illegal 1.1 state accepted',case))
 def item(doc,key):return next(x for x in doc['gates'] if x['id']==key)
 alter('mark section completed',lambda d:item(d,'api_blockade_duration_1055').update(status='completed'))
 alter('erase missing API reviews',lambda d:item(d,'draft_semantics').update(unresolved_count=0))
 alter('invent reviewed historical entries',lambda d:item(d,'draft_semantics').update(reviewed_offline=3658))
 alter('fake Windows completion',lambda d:item(d,'windows_runtime').update(native_gameplay_tested=True))
 alter('fake gender callsite count',lambda d:item(d,'pronoun_contexts').update(unresolved_count=0))
 alter('fake source literal additions',lambda d:item(d,'api_blockade_duration_1055').update(added_api_rows=80))
 alter('fake changed JVM class count',lambda d:item(d,'api_blockade_duration_1055').update(changed_classes=1))
 alter('erase prior version evidence',lambda d:item(d,'personality_ui_1051').update(jvm_ldc_operand_changes=0))
 alter('remove open gate',lambda d:d['gates'].pop())
 alter('duplicate gate',lambda d:d['gates'].append(copy.deepcopy(d['gates'][0])))
 if len(rejections)!=10:raise AssertionError('Missing negative checks')
 audit(root,gates,previous,ledger)
 return {'release':'1.0.55','false_release_states_rejected':len(rejections),'cases':rejections}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 for k in ('gates','previous','ledger'):p.add_argument('--'+k,required=True,type=Path)
 a=p.parse_args();print(json.dumps(run(a.worktree,a.gates,a.previous,a.ledger),indent=2))
