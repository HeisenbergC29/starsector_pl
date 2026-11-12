#!/usr/bin/env python3
"""Negative regressions: never silently corrupt a historical translation row."""
import copy,csv,json,shutil,tempfile
from pathlib import Path
from apply_1037 import CORRECT,NEW
from verify_1037 import mapdiff,phrases

def must_fail(fn):
 try:fn()
 except (AssertionError,ValueError,KeyError,FileNotFoundError):return
 raise AssertionError('Unsafe mapping accepted')

def run(root):
 assert len(phrases()['male'])==len(phrases()['female'])==6
 assert mapdiff(root)['api_map_rows']==5245
 with tempfile.TemporaryDirectory() as td:
  f=Path(td);(f/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations').mkdir(parents=True)
  a=f/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';o=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
  for n in ('TLUMACZENIA_JAR_1036.csv','TLUMACZENIA_JAR_1037.csv'):
   shutil.copy2(o/'translations'/n,a/'translations'/n)
  shutil.copy2(o/'main.go',a/'main.go')
  i=f/'buildtools/NARZEDZIA_INSTALATOR';i.mkdir(parents=True);shutil.copy2(root/'buildtools/NARZEDZIA_INSTALATOR/main.go',i/'main.go')
  m=f/'mod';m.mkdir();shutil.copy2(root/'mod/mod_info.json',m/'mod_info.json');(m/'data').symlink_to(root.resolve()/'mod/data',target_is_directory=True)
  path=a/'translations/TLUMACZENIA_JAR_1037.csv'
  with path.open(encoding='utf8',newline='') as handle:read=csv.DictReader(handle);baseline=list(read);fields=read.fieldnames
  def attempt(fix):
   rr=copy.deepcopy(baseline);fix(rr)
   with path.open('w',encoding='utf8',newline='') as h:
    w=csv.DictWriter(h,fieldnames=fields,lineterminator='\r\n');w.writeheader();w.writerows(rr)
   must_fail(lambda:mapdiff(f))
  def tamper_original(r):r[0]['polish_ascii_draft']='BAD'
  def tamper_last(r):r[-1]['polish_ascii_draft']='says'
  def wrong_key(r):r[-1]['english_literal']=' says.'
  def remove_last(r):r.pop()
  def duplicate_last(r):r.append(copy.deepcopy(r[-1]))
  def modify_status(r):r[-1]['status']='DRAFT_ONLY_NOT_INSTALLED'
  def patch_her(r):r.append({'source_class':'com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson','english_literal':'her','polish_ascii_draft':'jej','status':'VERIFIED'})
  def corrupt_corrected(r):
   cl,en=next((cl,en) for cl,groups in CORRECT.items() for en in groups)
   next(q for q in r if q['source_class']==cl and q['english_literal']==en)['polish_ascii_draft']='OLD'
  for q in (tamper_original,tamper_last,wrong_key,remove_last,duplicate_last,modify_status,patch_her,corrupt_corrected):attempt(q)
  shutil.copy2(o/'translations/TLUMACZENIA_JAR_1037.csv',path)
  assert mapdiff(f)['corrected_existing_api']==5
  meta=m/'mod_info.json';x=json.loads(meta.read_text());x['version']='1.1';meta.write_text(json.dumps(x));must_fail(lambda:mapdiff(f))
 return {'rejected_invalid_maps':9,'composed_variants':12}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(run(p.parse_args().worktree),indent=2))
