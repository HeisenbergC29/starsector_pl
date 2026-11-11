#!/usr/bin/env python3
"""Verify 1.0.22 changes affect ONLY allowed visible names and release metadata.

For independent proof of differences to 1.0.21 pass --previous-zip. CI can
verify identical immutable 867-file tree via the anchored digest alone.
No original copyrighted game assets need be committed to GitHub.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from apply_1022 import BASELINE_SHA, EXPECT, NAME_RE, NAMES, TOKEN_RE, only_text_columns

UNCHANGED_DATA_SHA='246f37f17cb5494e083dbd72d02cd5e47da723b31b39b8580e8331e1e7ae7782'
NEW_SHA = {
 'campaign/rules.csv':'c24d09cb29da3cccd01b40e2b8d318988000ebb132ad0de105fdf916e7b00e38',
 'strings/descriptions.csv':'2de5df22af176879cab2c1623253d66e60a549f48ae5e2cf2335d251d625f1b3',
 'missions/coralnebula/mission_text.txt':'c4885f05f35aef74e2b798f811cde31c497579e91d735fccd0892ad4d514675b',
}

def checksum(s):return hashlib.sha256(s).hexdigest()

def check(root,previous_zip=None):
 data=root/'mod/data'
 files=sorted(p for p in data.rglob('*') if p.is_file())
 assert len(files)==870
 assert all(p.read_bytes().isascii() for p in files)
 assert set(NEW_SHA)<= {p.relative_to(data).as_posix() for p in files}
 h=hashlib.sha256()
 for p in files:
  name=p.relative_to(data).as_posix()
  if name not in NEW_SHA:
   h.update(name.encode('utf8')+b'\0'+hashlib.sha256(p.read_bytes()).digest())
 assert h.hexdigest()==UNCHANGED_DATA_SHA,(h.hexdigest(),'867 unchanged data files changed')
 for name,expected in NEW_SHA.items():
  p=data/name
  assert checksum(p.read_bytes())==expected,(name,'unapproved change')
 for p in files:
  if p.suffix in {'.txt','.java','.csv','.json'}:
   assert not NAME_RE.search(p.read_bytes()),('legacy faction name persists',p)
 if previous_zip:
  with zipfile.ZipFile(previous_zip) as z:
   before={n.removeprefix('Starsector_PL_ASCII/data/'):z.read(n) for n in z.namelist()
           if n.startswith('Starsector_PL_ASCII/data/') and not n.endswith('/')}
  assert len(before)==870
  changed=[];total=0
  for p in files:
   name=p.relative_to(data).as_posix();old=before[name];new=p.read_bytes()
   if old==new:continue
   changed.append(name)
   assert 'mod/data/'+name in EXPECT,('not approved file',name)
   assert checksum(old)==BASELINE_SHA['mod/data/'+name]
   source_occurrences=list(NAME_RE.finditer(old))
   assert len(source_occurrences)==EXPECT['mod/data/'+name]
   transformed=NAME_RE.sub(lambda m:NAMES[m.group(1)],old)
   assert transformed==new,(name,'non-name text changed')
   assert TOKEN_RE.findall(old)==TOKEN_RE.findall(new)
   if name.endswith('rules.csv'):only_text_columns(old,new,name,{'text'})
   if name.endswith('descriptions.csv'):only_text_columns(old,new,name,{'text1','text2','text3','text4','text5'})
   total+=len(source_occurrences)
  assert set(changed)==set(NEW_SHA)
  assert total==65
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.22' and meta['gameVersion']=='0.98a-RC8'
 assert len(meta['replace'])==41 and len(set(meta['replace']))==41
 assert 'const edition = "1.0.22"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 assert 'const version = "1021"' in (root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
 assert 'loadTranslations("TLUMACZENIA_OBF_10121.csv")' in (root/'buildtools/NARZEDZIA_OBF/main.go').read_text('utf8')
 print('1.0.22 NAME CHECK PASS: 65 corrections; exactly 3 approved data files; unchanged 867 files verified by SHA-256')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path);ap.add_argument('--previous-zip',type=Path)
 args=ap.parse_args();check(args.worktree,args.previous_zip)