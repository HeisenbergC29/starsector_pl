#!/usr/bin/env python3
"""Negative 1.1 gate tests: prevent exaggerating audited her or completing release."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1052 import audit

def test(root,gates,previous,ledger):
 original=json.loads(Path(gates).read_text('utf8'));checks={}
 def try_bad(label,func):
  data=copy.deepcopy(original);func(data)
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'mutated_gates.json';file.write_text(json.dumps(data),encoding='utf8')
   try:audit(root,file,previous,ledger)
   except (ValueError,KeyError,AssertionError):checks[label]='REJECTED'
   else:raise AssertionError(('Invalid release gate accepted',label))
 def item(src,id):return next(x for x in src['gates'] if x['id']==id)
 try_bad('mark native Windows gameplay tested',lambda s:item(s,'windows_runtime').update(native_gameplay_tested=True))
 try_bad('complete release 1.1 unverified',lambda s:item(s,'draft_semantics').update(status='completed'))
 try_bad('close 186 getter callsite backlog',lambda s:item(s,'pronoun_contexts').update(unresolved_count=0))
 try_bad('drop pending Windows review of shared her',lambda s:item(s,'pronoun_contexts').update(shared_her_pending_native_windows_validation=False))
 try_bad('invent fully reviewed all get-call contexts',lambda s:item(s,'pronoun_contexts').update(base_bar_gender_getter_callsites_reviewed_1052=219))
 try_bad('remove class-scoped mapping evidence',lambda s:item(s,'bar_shared_her_1052').update(new_api_rows=0))
 try_bad('claim bytecode changed instead of constant pool',lambda s:item(s,'bar_shared_her_1052').update(new_executable_java_bytecode_changes=4))
 try_bad('change previous personality authorized exception',lambda s:item(s,'personality_ui_1051').update(jvm_ldc_operand_changes=0))
 try_bad('pretend all history reviewed',lambda s:item(s,'draft_semantics').update(reviewed_offline=3658,unresolved_count=0))
 try_bad('forget original Windows pending',lambda s:item(s,'bar_shared_her_1052').update(pending_windows_ui=0))
 if len(checks)!=10:raise AssertionError('Unexpected mutation count')
 return {'release':'1.0.52','negative_release_gates_rejected':10,'cases':checks,
  'current_gates_still_block_full_1_1':audit(root,gates,previous,ledger)['target_1_1_blocked']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 args=p.parse_args();print(json.dumps(test(args.worktree,args.gates,args.previous,args.ledger),indent=2))
