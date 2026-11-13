#!/usr/bin/env python3
"""Tamper tests: no premature 1.1 declaration allowed in v1.0.54."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1054 import audit

def test(root,gates,previous,ledger):
 base=json.loads(Path(gates).read_text('utf8'));rejected={}
 def must_reject(name,fn):
  obj=copy.deepcopy(base);fn(obj);p=None
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'gates.json';p.write_text(json.dumps(obj),encoding='utf8')
   try:audit(root,p,previous,ledger)
   except (ValueError,KeyError):rejected[name]='REJECTED'
   else:raise AssertionError(('Invalid 1.1 state accepted',name))
 def edit(obj,key,field,value):next(x for x in obj['gates'] if x['id']==key)[field]=value
 must_reject('mark all 1.1 stages completed',lambda d:d['gates'][0].update(status='completed'))
 must_reject('fake reviewed 3658',lambda d:edit(d,'draft_semantics','reviewed_offline',3658))
 must_reject('fake remaining zero',lambda d:edit(d,'draft_semantics','unresolved_count',0))
 must_reject('claim Windows gameplay',lambda d:edit(d,'windows_runtime','native_gameplay_tested',True))
 must_reject('claim no pronoun issues',lambda d:edit(d,'pronoun_contexts','unresolved_count',0))
 must_reject('invent map entries',lambda d:edit(d,'api_dynamic_fragments_1054','new_api_rows',70))
 must_reject('invent JVM class count',lambda d:edit(d,'api_dynamic_fragments_1054','changed_classes',10))
 must_reject('erase prior OBF proof',lambda d:edit(d,'obf_recovery_1053','new_obf_entries',0))
 must_reject('delete current gate',lambda d:d['gates'].pop())
 if len(rejected)!=9:raise AssertionError('Negative gate inventory changed')
 audit(root,gates,previous,ledger)
 return {'version':'1.0.54','negative_fake_1_1_states_rejected':len(rejected),'checks':rejected,'real_1_1_status':'BLOCKED'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);a=p.parse_args()
 print(json.dumps(test(a.worktree,a.gates,a.previous,a.ledger),indent=2))
