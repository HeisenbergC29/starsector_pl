#!/usr/bin/env python3
"""Negative tests: the real verifier must reject five unauthorized changes."""
import csv, shutil, tempfile
from pathlib import Path
from verify_1026_ui import validate


def test(root):
 files=[
  'buildtools/NARZEDZIA_OBF/TLUMACZENIA_OBF_10125.csv',
  'buildtools/NARZEDZIA_OBF/TLUMACZENIA_OBF_10126.csv',
  'buildtools/NARZEDZIA_OBF/main.go',
  'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1025.csv',
  'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1026.csv',
  'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go',
  'buildtools/NARZEDZIA_INSTALATOR/main.go',
 ]
 with tempfile.TemporaryDirectory() as tmp:
  work=Path(tmp);(work/'mod').symlink_to((root/'mod').resolve(),target_is_directory=True)
  for f in files:
   dest=work/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/f,dest)
  assert validate(work)['new_obf_literals']==86
  target=work/'buildtools/NARZEDZIA_OBF/TLUMACZENIA_OBF_10126.csv'
  with target.open('r',encoding='utf8',newline='') as f:
   reader=csv.DictReader(f);fieldnames=reader.fieldnames;old=list(reader)
  def mutate(name,index,field,value):
   rows=[r.copy() for r in old];rows[index][field]=value
   with target.open('w',encoding='utf8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fieldnames,lineterminator='\r\n');w.writeheader();w.writerows(rows)
   failed=False
   try:validate(work)
   except AssertionError:failed=True
   assert failed,(name,'unauthorized mapping was not detected')
  mutate('historical_change',0,'polish_ascii_draft','Nieautoryzowana zmiana')
  mutate('current_change',-1,'polish_ascii_draft','Bledna etykieta')
  mutate('class_id_change',-1,'source_class','com.fs.fake.Invalid')
  mutate('protected_enum',-1,'english_literal','HOLD')
  shutil.copyfile(root/'buildtools/NARZEDZIA_OBF/TLUMACZENIA_OBF_10126.csv',target)
  api=work/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1026.csv';api.write_bytes(api.read_bytes()+b'\n')
  failed=False
  try:validate(work)
  except AssertionError:failed=True
  assert failed, 'Unauthorized API map delta was not rejected'
 print('PASS: 5 real negative verifier tests and original positive fixture')
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);args=p.parse_args();test(args.worktree)