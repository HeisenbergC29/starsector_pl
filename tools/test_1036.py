#!/usr/bin/env python3
"""Negative tests: reject unapproved class, map, getter or data changes."""
from __future__ import annotations
import csv,copy,json,shutil,tempfile
from pathlib import Path
from apply_1036 import main,NEW,CORRECT,BASE,EVENT
from verify_1036 import mapdiff,phrase
from verify_review_1036 import check as review

def must_fail(fn,reason):
 try:fn()
 except (AssertionError,ValueError,KeyError,FileExistsError):return
 raise AssertionError('bad input accepted: '+reason)

def run(root,prior,current):
 assert mapdiff(root)['new_api_rows']==5244
 assert phrase('male')!=phrase('female')
 assert ' niz on,' in phrase('male') and ' niz ona,' in phrase('female')
 assert review(root,prior,current)['total_offline_reviewed']==78
 tests=0
 # Only copy the one active map for 7 isolated negative corruptions.
 with tempfile.TemporaryDirectory() as t:
  fake=Path(t);(fake/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations').mkdir(parents=True)
  a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
  dst=fake/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
  for name in ('TLUMACZENIA_JAR_1033.csv','TLUMACZENIA_JAR_1036.csv'):shutil.copy2(a/name,dst/name)
  shutil.copytree(root/'mod',fake/'mod')
  out=fake/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
  shutil.copy2(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go',out/'main.go')
  inst=fake/'buildtools/NARZEDZIA_INSTALATOR';inst.mkdir()
  shutil.copy2(root/'buildtools/NARZEDZIA_INSTALATOR/main.go',inst/'main.go')
  path=dst/'TLUMACZENIA_JAR_1036.csv'
  with path.open(newline='',encoding='utf8') as f:
   rdr=csv.DictReader(f);base_rows=list(rdr);fields=rdr.fieldnames
  def attempt(change):
   rr=copy.deepcopy(base_rows);change(rr)
   with path.open('w',newline='',encoding='utf8') as f:
    w=csv.DictWriter(f,fieldnames=fields,lineterminator='\r\n');w.writeheader();w.writerows(rr)
   must_fail(lambda:mapdiff(fake),change.__name__)
  def remove_reflexive(rr):rr.pop()
  def wrong_reflexive(rr):rr[-1]['polish_ascii_draft']='jego'
  def duplicate_existing(rr):rr[-1]['english_literal']='he'
  def tamper_historical(rr):rr[0]['polish_ascii_draft']='ZARAZA'
  def tamper_context(rr):
   target=next(r for r in rr if r['source_class']==EVENT and r['english_literal']=='stride as ')
   target['polish_ascii_draft']=' kiedys '
  def tamper_status(rr):rr[-2]['status']='DRAFT_ONLY_NOT_INSTALLED'
  def patch_shared_her(rr):rr.append({'source_class':BASE,'english_literal':'her','polish_ascii_draft':'jej','status':'PATCH'})
  for fn in (remove_reflexive,wrong_reflexive,duplicate_existing,tamper_historical,tamper_context,tamper_status,patch_shared_her):
   attempt(fn);tests+=1
  # Rebuild exact pristine active CSV from original and verify it is immutable.
  shutil.copy2(a/'TLUMACZENIA_JAR_1036.csv',path)
  assert mapdiff(fake)['added_api']==2
  # A regenerated overlay must fail: duplicate active CSV and mismatched source version.
  must_fail(lambda:main(fake),'no overwrite active map');tests+=1
  src=fake/'mod/mod_info.json';meta=json.loads(src.read_text('utf8'));meta['version']='1.1';src.write_text(json.dumps(meta)+'\n')
  must_fail(lambda:mapdiff(fake),'premature version');tests+=1
 assert tests==9
 return {'negative_tests_passed':tests,'male_and_female_assembled_phrases':2}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--prior-ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1033.json'))
 p.add_argument('--ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1036.json'))
 a=p.parse_args();print(json.dumps(run(a.worktree,a.prior_ledger,a.ledger),indent=2))
