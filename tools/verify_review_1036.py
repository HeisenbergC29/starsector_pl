#!/usr/bin/env python3
"""Fail-closed, append-only semantic-review ledger: 58 previous + 20 new."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from make_review_1036 import SELECT,EVENT,fp
from verify_story_1033 import class_entries,texts
DRAFT={'DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME','OPTIONAL_PATCHER_NOT_GAME_TESTED'}

def check(root,prior_path,current_path,original_jar=None,patched_jar=None):
 prior=json.loads(prior_path.read_text('utf8'));new=json.loads(current_path.read_text('utf8'))
 assert prior['installed_version']=='1.0.33' and new['installed_version']=='1.0.36'
 assert prior['schema_version']==new['schema_version']==1
 assert len(prior['reviewed'])==58 and len(new['reviewed'])==78
 assert new['reviewed'][:58]==prior['reviewed'], 'old review rewritten'
 with (root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1036.csv').open(encoding='utf8',newline='') as f:rows=list(csv.DictReader(f))
 assert len(rows)==5244
 lookup={(r['source_class'],fp(r)):r for r in rows}
 assert len(lookup)==5244
 actual=set();prev=set()
 for i,item in enumerate(new['reviewed']):
  key=(item['source_class'],item['row_sha256'])
  assert key not in prev and key in lookup,('duplicate or stale review',key)
  prev.add(key);r=lookup[key]
  assert r['status'] in DRAFT and r['polish_ascii_draft'].isascii()
  if i>=58:
   assert r['source_class']==EVENT and r['english_literal'] in SELECT
   assert item['note']==SELECT[r['english_literal']]
   assert item['evidence']=='planetary_shield_contextual_original_and_patched_jvm'
   assert item['english_key_sha256']==hashlib.sha256(r['english_literal'].encode('utf8')).hexdigest()
   actual.add(r['english_literal'])
 assert actual==set(SELECT) and len(actual)==20
 historical=[r for r in rows if r['status'] in DRAFT]
 assert len(historical)==3658
 # Original-JAR evidence is available privately and never checked into Git.
 if original_jar or patched_jar:
  assert original_jar and patched_jar
  import zipfile
  name=EVENT.replace('.','/')+'.class'
  with zipfile.ZipFile(original_jar) as a,zipfile.ZipFile(patched_jar) as b:
   en=texts(class_entries(a.read(name))[0]);pl=texts(class_entries(b.read(name))[0])
  for key in actual:
   row=next(r for r in rows if r['source_class']==EVENT and r['english_literal']==key)
   assert en[key]>=1 and pl[row['polish_ascii_draft']]>=1,('unconfirmed compiled string',key)
 return {'prior_offline_reviewed':58,'new_offline_reviewed':20,'total_offline_reviewed':78,
         'historical_api_draft_pool':3658,'pending_historical_semantic_review':3580,
         'runtime_unverified_tracked_api':3683,
         'new_reflexive_late_literals':2,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--prior-ledger',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 p.add_argument('--original-api',type=Path);p.add_argument('--patched-api',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.prior_ledger,a.ledger,a.original_api,a.patched_api),indent=2))
