#!/usr/bin/env python3
"""Adversarial negative mutations for 1.0.58 dialogue-only release."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1058 import read_plan,patch_rules,sha,BASE_RULES_SHA,EXPECTED_ROWS,EXPECTED_EDITS
from verify_1058 import check,reverse_rules,NEW_RULES_SHA

def test(worktree:Path)->dict:
 worktree=Path(worktree);plan=read_plan()
 current=(worktree/'mod/data/campaign/rules.csv').read_bytes()
 baseline=reverse_rules(current,plan)
 out,result=patch_rules(baseline,plan)
 assert out==current and result['corrected_dialogues']==EXPECTED_ROWS and result['removed_gender_variables']==EXPECTED_EDITS
 denied={}
 def reject(label,fn):
  try:fn()
  except (ValueError,KeyError,AssertionError):denied[label]='REJECTED'
  else:raise AssertionError(('Invalid mutation was accepted',label))
 first=sorted(plan)[0]
 def mutation(fn):
  p=copy.deepcopy(plan);fn(p);patch_rules(baseline,p)
 reject('tampered 1.0.57 source bytes',lambda:patch_rules(baseline[:-1]+b' ',plan))
 reject('truncated original',lambda:patch_rules(baseline[:-50],plan))
 reject('incorrect original text fingerprint',lambda:mutation(lambda p:p[first].update(old_text_sha256='f'*64)))
 reject('incorrect revised text fingerprint',lambda:mutation(lambda p:p[first].update(new_text_sha256='f'*64)))
 reject('invent a nonexistent dialogue ID',lambda:mutation(lambda p:p.update({'__fake_rule__':p.pop(first)})))
 reject('delete one approved dialogue ID',lambda:mutation(lambda p:p.pop(first)))
 reject('move one edit outside approved text',lambda:mutation(lambda p:p[first]['edits'][0].update(start=999999)))
 reject('alter unrelated game variable',lambda:mutation(lambda p:p[first]['edits'][0].update(after='$personName')))
 reject('rewrite arbitrary installed dialogue bytes',lambda:reverse_rules(current.replace(b'podrozy',b'podrOzy',1),plan))
 reject('append one byte to installed file',lambda:reverse_rules(current+b' ',plan))
 if len(denied)!=10:raise AssertionError('Incomplete negative tests')
 check(worktree)
 return {'version':'1.0.58','corrected_dialogue_rows':EXPECTED_ROWS,'approved_edits':EXPECTED_EDITS,
  'prior_rules_reconstructed_byte_exactly':True,'negative_mutations_rejected':len(denied),'cases':denied}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(test(a.worktree),indent=2))
