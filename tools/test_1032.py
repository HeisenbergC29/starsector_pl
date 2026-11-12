#!/usr/bin/env python3
"""Offline deterministic regressions 1.0.32, including 8 fail-closed cases."""
from __future__ import annotations
import argparse,csv,copy,hashlib,json,tempfile,shutil
from pathlib import Path
from verify_1032 import check,readrows
from apply_1032 import CORRECTIONS,NEW

def assert_fails(fn):
 try:fn()
 except (AssertionError,ValueError,KeyError,FileNotFoundError):return
 raise AssertionError('Unexpectedly accepted malformed payload')

def main(root:Path):
 base=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readrows(base/'TLUMACZENIA_JAR_1030.csv')
 new=readrows(base/'TLUMACZENIA_JAR_1032.csv')
 assert len(old)+6==len(new)
 check(root)
 tests=0
 with tempfile.TemporaryDirectory() as d:
  temp=Path(d);mapfile=temp/'TLUMACZENIA_JAR_1032.csv'
  def check_bad(index,change):
   rows=copy.deepcopy(new);change(rows[index]);
   with mapfile.open('w',encoding='utf8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(new[0]),lineterminator='\r\n');w.writeheader();w.writerows(rows)
   shutil.copy2(mapfile,base/'TLUMACZENIA_JAR_1032.csv')
   try:assert_fails(lambda:check(root))
   finally:
    with (base/'TLUMACZENIA_JAR_1032.csv').open('w',encoding='utf8',newline='') as f:
     w=csv.DictWriter(f,fieldnames=list(new[0]),lineterminator='\r\n');w.writeheader();w.writerows(new)
  # Do not rewrite actual source version map when a regression fails.
  original_bytes=(base/'TLUMACZENIA_JAR_1032.csv').read_bytes()
  try:
   keys={ (x['source_class'],x['english_literal']):i for i,x in enumerate(new)}
   first_cl=next(iter(CORRECTIONS));first_en=next(iter(CORRECTIONS[first_cl]));i=keys[first_cl,first_en]
   tests+=1;check_bad(i,lambda r:r.__setitem__('polish_ascii_draft','bad'))
   tests+=1;check_bad(i,lambda r:r.__setitem__('status','NOT_APPROVED'))
   k=keys[next(iter(NEW)),"year's"]
   tests+=1;check_bad(k,lambda r:r.__setitem__('polish_ascii_draft','1 lat'))
   tests+=1;check_bad(k,lambda r:r.__setitem__('english_literal','UNEXPECTED'))
   tests+=1;check_bad(k,lambda r:r.__setitem__('status','DRAFT_ONLY_NOT_INSTALLED'))
   tests+=1;check_bad(0,lambda r:r.__setitem__('polish_ascii_draft','unapproved earlier revision'))
   tests+=1;check_bad(0,lambda r:r.__setitem__('source_class','arbitrary.ID'))
   tests+=1;check_bad(len(old)-1,lambda r:r.__setitem__('status','INVALID'))
  finally:(base/'TLUMACZENIA_JAR_1032.csv').write_bytes(original_bytes)
 check(root)
 print(json.dumps({'positive':'PASS','negative_cases':tests,'unchanged_history':len(old),'new_entries':6,'context_corrected':25}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);main(p.parse_args().worktree)
