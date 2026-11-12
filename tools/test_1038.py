#!/usr/bin/env python3
"""Reject unsafe historical edits, wrong grammatical cases and false release IDs."""
from __future__ import annotations
import argparse,copy,csv,json,shutil,tempfile
from pathlib import Path
from apply_1038 import BAR,DATA,DONATION,CORRECT,NEW
from verify_1038 import validate_map,phrases

def reject(func):
 try:func()
 except (AssertionError,KeyError,ValueError,FileNotFoundError):return
 raise AssertionError('Unsafe mapping alteration was not rejected')

def run(root):
 assert validate_map(root)['api_map_rows']==5254
 assert len(phrases(root)['male'])==len(phrases(root)['female'])==9
 with tempfile.TemporaryDirectory() as tmp:
  w=Path(tmp); src=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
  dest=w/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';(dest/'translations').mkdir(parents=True)
  for name in ('TLUMACZENIA_JAR_1037.csv','TLUMACZENIA_JAR_1038.csv'):
   shutil.copyfile(src/'translations'/name,dest/'translations'/name)
  shutil.copyfile(src/'main.go',dest/'main.go')
  install=w/'buildtools/NARZEDZIA_INSTALATOR';install.mkdir();shutil.copyfile(root/'buildtools/NARZEDZIA_INSTALATOR/main.go',install/'main.go')
  mod=w/'mod';mod.mkdir();shutil.copyfile(root/'mod/mod_info.json',mod/'mod_info.json')
  (mod/'data').symlink_to((root/'mod/data').resolve(),target_is_directory=True)
  f=dest/'translations/TLUMACZENIA_JAR_1038.csv'
  with f.open(encoding='utf8',newline='') as h:
   r=csv.DictReader(h);base=list(r);fields=r.fieldnames
  def edit(func):
   rows=copy.deepcopy(base);func(rows)
   with f.open('w',encoding='utf8',newline='') as h:
    r=csv.DictWriter(h,fieldnames=fields,lineterminator='\r\n');r.writeheader();r.writerows(rows)
   reject(lambda:validate_map(w))
  def find(rr,cl,en):return next(r for r in rr if r['source_class']==cl and r['english_literal']==en)
  tests=[
   lambda rr:rr[0].update(polish_ascii_draft='UNREVIEWED'),
   lambda rr:find(rr,DATA,'her').update(polish_ascii_draft='ja'),
   lambda rr:find(rr,DATA,'him').update(polish_ascii_draft='go'),
   lambda rr:find(rr,DATA,'man').update(polish_ascii_draft='czlowiek'),
   lambda rr:find(rr,DATA,'her').update(status='DRAFT_ONLY_NOT_INSTALLED'),
   lambda rr:rr.append(copy.deepcopy(rr[-1])),
   lambda rr:rr.pop(),
   lambda rr:find(rr,DATA,'her').update(source_class='com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson'),
   lambda rr:find(rr,BAR,' leans in as if conspiring, "').update(polish_ascii_draft=' nachyla sie: "'),
   lambda rr:find(rr,BAR,'know for sure where I\'ll end up in a couple of months."').update(polish_ascii_draft='nie nie wiem, gdzie bede.'),
   lambda rr:find(rr,DONATION,' pursue').update(polish_ascii_draft=' examine'),
   lambda rr:find(rr,DONATION,'... some promising leads that a ').update(polish_ascii_draft='bad'),
  ]
  for test in tests:edit(test)
  shutil.copyfile(src/'translations/TLUMACZENIA_JAR_1038.csv',f)
  assert validate_map(w)['corrected_api']==12
  metadata=mod/'mod_info.json';data=json.loads(metadata.read_text('utf8'));data['version']='1.1';metadata.write_text(json.dumps(data))
  reject(lambda:validate_map(w))
 return {'negative_map_cases':13,'gendered_phrase_variants':18}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(run(p.parse_args().worktree),indent=2))
