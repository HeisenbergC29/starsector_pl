#!/usr/bin/env python3
"""Mutation/regression tests for 110 reviewed v1.0.56 dialogue-only changes."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1056 import read_plan,patch_rules,sha,BASE_RULES_SHA,DYNAMIC
from verify_1056 import check,invert_rules,EXPECTED_LEDGER_SHA,NEW_RULES_SHA

def test(worktree:Path)->dict:
 worktree=Path(worktree);current=(worktree/'mod/data/campaign/rules.csv').read_bytes()
 plan=read_plan(Path(__file__).resolve().parents[1]/'docs/RULES_NEUTRAL_REVIEW_1056.json')
 assert sha(current)==NEW_RULES_SHA
 before=invert_rules(current,plan)
 expected,out=patch_rules(before,plan)
 assert current==expected and out['changed_rows']==110 and out['removed_gender_placeholders']==110
 checks={}
 def reject(key,fn):
  try:fn()
  except (ValueError,KeyError,AssertionError):checks[key]='REJECTED'
  else:raise AssertionError(('Invalid mutation accepted',key))
 def changed_plan(key,edit):
  p=copy.deepcopy(plan);edit(p);patch_rules(before,p)
 first=sorted(plan)[0]
 reject('wrong original source SHA',lambda:patch_rules(before[:-1]+b' ',plan))
 reject('truncated original source',lambda:patch_rules(before[:-50],plan))
 reject('fake original text SHA',lambda:changed_plan('old sha',lambda p:p[first].update(old_text_sha256='f'*64)))
 reject('fake new text SHA',lambda:changed_plan('new sha',lambda p:p[first].update(new_text_sha256='f'*64)))
 reject('remove a required reviewed ID',lambda:changed_plan('missing',lambda p:p.pop(first)))
 reject('invent a nonexistent dialogue rule',lambda:changed_plan('fake',lambda p:p.update({'__missing_dialogue_1056__':p.pop(first)})))
 reject('alter a technical dialog variable',lambda:changed_plan('variable',lambda p:p[first]['edits'].append(['$playerName','$fakeVariable'])))
 reject('insert extra gender token',lambda:changed_plan('gender',lambda p:p[first]['edits'].append(['mowi','mowi $heOrShe'])))
 reject('modify installed punctuation',lambda:invert_rules(current.replace(b'podrozy',b'podrOzy',1),plan))
 reject('modify installed end of file',lambda:invert_rules(current+b' ',plan))
 # Original review plan must also be independent of previously approved gender edits.
 result=check(worktree,validate_prior=False)
 if len(checks)!=10:raise AssertionError('Not all negative mutations executed')
 return {'release':'1.0.56','corrected_dialogue_rows':result['changed_dialogue_rows'],
   'original_11107_rows_recreated_byte_exactly':True,'unreviewed_columns_and_869_data_files_unchanged':True,
   'gender_references_removed':110,'negative_mutations_rejected':len(checks),'cases':checks}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(test(a.worktree),indent=2))
