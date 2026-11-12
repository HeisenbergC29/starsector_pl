#!/usr/bin/env python3
"""Guard against faked completion of the 1.1 release gates."""
import importlib.util,json,sys,tempfile,shutil
from pathlib import Path
from check_release_gates_1034 import check

def main(root,repo_root):
 g=repo_root/'docs/RELEASE_GATES_11.json'
 old=repo_root/'docs/API_SEMANTIC_REVIEW_1032.json'
 ledger=repo_root/'docs/API_SEMANTIC_REVIEW_1033.json'
 rules=repo_root/'docs/RULES_PRONOUN_REVIEW_1034.json'
 assert check(root,g,old,ledger,rules)['release_11_allowed'] is False
 refused=0
 def reject(gates=None,rules_ledger=None,strict=False):
  nonlocal refused
  try:check(root,gates or g,old,ledger,rules_ledger or rules,strict)
  except (AssertionError,ValueError,RuntimeError):refused+=1;return
  raise AssertionError('Incomplete 1.1 was erroneously accepted')
 reject(strict=True)
 with tempfile.TemporaryDirectory() as t:
  temp=Path(t)
  for k,new in [('pronoun_contexts',218),('story_contexts',1),('draft_semantics',3599)]:
   j=json.loads(g.read_text('utf8'));next(x for x in j['gates'] if x['id']==k)['unresolved_count']=new
   p=temp/(k+'.json');p.write_text(json.dumps(j));reject(gates=p)
  for k in ['reviewed_rules_rows_offline','removed_visible_gender_variable_refs','pending_windows_ui_rules_rows']:
   j=json.loads(g.read_text('utf8'));next(x for x in j['gates'] if x['id']=='pronoun_contexts')[k]+=1
   p=temp/(k+'.json');p.write_text(json.dumps(j));reject(gates=p)
  j=json.loads(rules.read_text('utf8'));j['reviewed'][0]['after_sha256']='0'*64
  p=temp/'bad_rules.json';p.write_text(json.dumps(j));reject(rules_ledger=p)
  j=json.loads(rules.read_text('utf8'));j['pending_windows_ui_rows']=0
  p=temp/'fake_windows.json';p.write_text(json.dumps(j));reject(rules_ledger=p)
 print(json.dumps({'negative_release_gate_tests':refused,'strict_1_1_refused':True},indent=2))

if __name__=='__main__':main(Path(sys.argv[1]),Path(sys.argv[2]))
