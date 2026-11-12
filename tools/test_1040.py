#!/usr/bin/env python3
"""Fail-closed regressions for 1.0.40 exact mappings and male/female snippets."""
from __future__ import annotations
import argparse,csv,copy,json,shutil,tempfile
from pathlib import Path
from apply_1040 import B
from verify_1040 import validate_map,composed

def reject(fn):
 try:fn()
 except (AssertionError,KeyError,ValueError,FileNotFoundError):return
 raise AssertionError('Unsafe change accepted')

def run(root):
 assert validate_map(root)['api_map_rows']==5257
 assert composed(root)['gendered_snippets']==24
 src=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 with tempfile.TemporaryDirectory() as d:
  path=Path(d);td=path/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations';td.mkdir(parents=True)
  for name in ('TLUMACZENIA_JAR_1038.csv','TLUMACZENIA_JAR_1040.csv'):shutil.copyfile(src/'translations'/name,td/name)
  shutil.copyfile(src/'main.go',td.parent/'main.go')
  inst=path/'buildtools/NARZEDZIA_INSTALATOR';inst.mkdir();shutil.copyfile(root/'buildtools/NARZEDZIA_INSTALATOR/main.go',inst/'main.go')
  mod=path/'mod';mod.mkdir();shutil.copyfile(root/'mod/mod_info.json',mod/'mod_info.json')
  (mod/'data').symlink_to((root/'mod/data').resolve(),target_is_directory=True)
  f=td/'TLUMACZENIA_JAR_1040.csv'
  with f.open(encoding='utf8',newline='') as inp:
   r=csv.DictReader(inp);base=list(r);fields=r.fieldnames
  def change(fn):
   rows=copy.deepcopy(base);fn(rows)
   with f.open('w',encoding='utf8',newline='') as out:
    w=csv.DictWriter(out,fieldnames=fields,lineterminator='\r\n');w.writeheader();w.writerows(rows)
   reject(lambda:validate_map(path))
  def get(rr,cl,en):return next(r for r in rr if r['source_class']==B+cl and r['english_literal']==en)
  tests=[
   lambda rr:get(rr,'BaseGetCommodityBarEvent','man').update(polish_ascii_draft='czlowiek'),
   lambda rr:get(rr,'BaseGetCommodityBarEvent','woman').update(polish_ascii_draft='osoba'),
   lambda rr:get(rr,'BaseGetCommodityBarEvent','man').update(status='DRAFT_ONLY_NOT_INSTALLED'),
   lambda rr:get(rr,'CorruptPLClerkSuppliesBarEvent','A ').update(polish_ascii_draft='A '),
   lambda rr:get(rr,'LuddicFarmerBarEvent','A weathered-looking ').update(polish_ascii_draft='Sterany zyciem '),
   lambda rr:get(rr,'TriTachLoanBarEvent',"'s smile freezes in place as you launch into a sophisticated ").update(polish_ascii_draft='blad'),
   lambda rr:rr.append(dict(rr[-1])),
   lambda rr:rr.pop(),
   lambda rr:rr[0].update(polish_ascii_draft='BLAD'),
   lambda rr:get(rr,'BaseGetCommodityBarEvent','man').update(source_class=B+'BaseBarEventWithPerson'),
   lambda rr:get(rr,'BaseGetCommodityBarEvent','woman').update(polish_ascii_draft='kobietą'),
   lambda rr:get(rr,'LuddicCraftBarEvent','A tough looking ').update(status='VERIFIED_JVM_CALLSITE'),
  ]
  for mutate in tests:change(mutate)
  shutil.copyfile(src/'translations/TLUMACZENIA_JAR_1040.csv',f)

  assert validate_map(path)['corrected_api']==18
  metadata=mod/'mod_info.json';old=json.loads(metadata.read_text());old['version']='1.1';metadata.write_text(json.dumps(old))
  reject(lambda:validate_map(path))
 return {'negative_map_cases':13,'gendered_fragments':24}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);print(json.dumps(run(a.parse_args().worktree),indent=2))
