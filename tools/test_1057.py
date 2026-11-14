#!/usr/bin/env python3
"""Adversarial checks for the byte-pinned 1.0.57 dialogue rewrite."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1057 import read_plan,patch_rules,BASE_RULES_SHA,EXPECTED_ROWS,EXPECTED_PHRASES,EXPECTED_REMOVED,sha
from verify_1057 import check,reverse_rules,NEW_RULES_SHA

def run(root:Path)->dict:
 root=Path(root); plan=read_plan()
 dst=(root/'mod/data/campaign/rules.csv').read_bytes()
 baseline=reverse_rules(dst,plan)
 forward,rep=patch_rules(baseline,plan)
 assert forward==dst and rep['new_rules_sha256']==NEW_RULES_SHA
 errors={}
 def reject(k,callback):
  try:callback()
  except (ValueError,AssertionError,KeyError):errors[k]='REJECTED'
  else:raise AssertionError(('Incorrectly accepted broken dialogue plan',k))
 first=sorted(plan)[0]
 reject('tampered original source',lambda:patch_rules(baseline[:-1]+b' ',plan))
 reject('truncated original source',lambda:patch_rules(baseline[:-50],plan))
 def invalid(mod):
  p=copy.deepcopy(plan);mod(p);patch_rules(baseline,p)
 reject('wrong original text SHA',lambda:invalid(lambda p:p[first].update(old_text_sha256='f'*64)))
 reject('wrong expected new text SHA',lambda:invalid(lambda p:p[first].update(new_text_sha256='f'*64)))
 reject('new unrelated row ID',lambda:invalid(lambda p:p.update({'__not_in_game__':p.pop(first)})))
 reject('missing approved row',lambda:invalid(lambda p:p.pop(first)))
 reject('unapproved replacement target',lambda:invalid(lambda p:p[first]['edits'].append(['$personName','$FAKE'])))
 reject('inserted extra dynamic marker',lambda:invalid(lambda p:p[first]['edits'].append(['kreci','kreci $hisOrHer'])))
 reject('unexpected change to translated text',lambda:reverse_rules(dst.replace(b'podrozy',b'podrOzy',1),plan))
 reject('appended byte at EOF',lambda:reverse_rules(dst+b' ',plan))
 result=check(root)
 assert len(errors)==10
 return {'version':'1.0.57','rows':EXPECTED_ROWS,'phrases':EXPECTED_PHRASES,'removed_placeholders':EXPECTED_REMOVED,
 'reconstructed_1056_byte_exact':True,'negative_mutations_rejected':len(errors),'cases':errors,
 'unreviewed_data_unchanged':result['other_game_data_files_byte_identical']}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(run(a.worktree),indent=2))
