#!/usr/bin/env python3
"""Negative tests: fabricated 1.1 acceptance must never be permitted."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1035 import check
from verify_review_1035 import check as review_check

def main(root,repo):
 gates=repo/'docs/RELEASE_GATES_11.json'
 api_old=repo/'docs/API_SEMANTIC_REVIEW_1032.json'
 api_new=repo/'docs/API_SEMANTIC_REVIEW_1033.json'
 rules_old=repo/'docs/RULES_PRONOUN_REVIEW_1034.json'
 rules_new=repo/'docs/RULES_PRONOUN_REVIEW_1035.json'
 def go(g=gates,rl=rules_new,strict=False):return check(root,g,api_old,api_new,rules_old,rl,strict)
 assert go()['release_11_allowed'] is False
 negative=[]
 def expect(label,fn):
  try:fn()
  except (AssertionError,ValueError,RuntimeError,KeyError):negative.append(label);return
  raise AssertionError('Gate accepted invalid claim '+label)
 expect('force final 1.1 while blocked',lambda:go(strict=True))
 with tempfile.TemporaryDirectory() as d:
  temp=Path(d)
  original=json.loads(gates.read_text('utf8'))
  for key,new in [('pronoun_contexts',218),('story_contexts',1),('draft_semantics',3599)]:
   j=copy.deepcopy(original);next(g for g in j['gates'] if g['id']==key)['unresolved_count']=new
   path=temp/f'{key}.json';path.write_text(json.dumps(j));expect('fabricate unresolved '+key,lambda p=path:go(g=p))
  for key,new in [('reviewed_rules_rows_offline',90),('removed_visible_gender_variable_refs',184),('pending_windows_ui_rules_rows',0)]:
   j=copy.deepcopy(original);next(g for g in j['gates'] if g['id']=='pronoun_contexts')[key]=new
   path=temp/f'{key}.json';path.write_text(json.dumps(j));expect('fabricate rules count '+key,lambda p=path:go(g=p))
  current=json.loads(rules_new.read_text('utf8'))
  for key,value in [('reviewed_rows',63),('cumulative_removed_references',182),('pending_windows_ui_rows',0),('java_getter_calls_untouched',0)]:
   j=copy.deepcopy(current);j[key]=value;path=temp/f'ledger_{key}.json';path.write_text(json.dumps(j))
   expect('fake ledger '+key,lambda p=path:go(rl=p))
  j=copy.deepcopy(current);j['reviewed'][0]['after_sha256']['text']='0'*64
  path=temp/'fake_row_hash.json';path.write_text(json.dumps(j))
  expect('corrupt reviewed phrase hash',lambda:go(rl=path))
  j=copy.deepcopy(current);j['reviewed'][0]['windows_gameplay']='passed'
  path=temp/'fake_game_test.json';path.write_text(json.dumps(j))
  expect('fabricated Windows test',lambda:go(rl=path))
 print(json.dumps({'negative_release_gate_tests':len(negative),'negative_cases':negative,'final_1_1_refused':True},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('repo',type=Path)
 a=p.parse_args();main(a.worktree,a.repo)
