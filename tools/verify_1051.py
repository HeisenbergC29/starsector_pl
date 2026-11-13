#!/usr/bin/env python3
"""Strict 1.0.51 exact API map, Go source and mod/data validation.

This release deliberately changes two specific JVM ldc operands in one UI method.
Independent private original-JAR evidence is in private_jvm_1051.py.
"""
from __future__ import annotations
import argparse,json,zipfile
from pathlib import Path
from apply_1051 import OLD,NEW,OLD_SHA,CLASS,CORRECTIONS,readmap,corrected_rows,serialize,sha
from verify_1049 import tree_digest,RULES_SHA,DATA_TREE_SHA,OBF_GO_SHA
NEW_SHA='099abe6d62264e6b1d4ff66b9aba196ecb7d11845b7d2b2207aab4a8b8f66aa4'
GO_SHA='ea93eb50525724c253a6febde96ee9b07fb16ebfad9175c769088d4a287f25fc'


def check(root,previous_zip=None):
 root=Path(root);td=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 before=td/OLD;after=td/NEW
 if sha(before.read_bytes())!=OLD_SHA or sha(after.read_bytes())!=NEW_SHA:raise ValueError('Unexpected API map checksum')
 x=readmap(before);y=readmap(after)
 if len(x)!=5269 or len(y)!=5269 or serialize(corrected_rows(x))!=after.read_bytes():raise ValueError('Only 2 audited display translations may change')
 diffs=[(a['source_class'],a['english_literal']) for a,b in zip(x,y) if a!=b]
 if len(diffs)!=2 or any(k[0]!=CLASS or k[1] not in CORRECTIONS for k in diffs):raise ValueError('Wrong API translation scope')
 main=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go'
 if sha(main.read_bytes())!=GO_SHA:raise ValueError('Go patcher source has unexpected changes')
 obfgo=root/'buildtools/NARZEDZIA_OBF/main.go'
 if obfgo.exists() and sha(obfgo.read_bytes())!=OBF_GO_SHA:raise ValueError('OBF patcher modified')
 if not (root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/personality_1051_test.go').is_file():raise ValueError('Missing Go bytecode regression tests')
 info=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if info['version']!='1.0.51' or info['gameVersion']!='0.98a-RC8' or len(info['replace'])!=41:raise ValueError('Wrong release metadata')
 if 'const edition = "1.0.51"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):raise ValueError('Old installer edition')
 if not (root/'mod/CZYTAJ.txt').read_text('utf8').startswith('STARSECTOR PL ASCII 1.0.51'):raise ValueError('Old player readme')
 data=root/'mod/data';files=[p for p in data.rglob('*') if p.is_file()]
 if len(files)!=870 or sha((data/'campaign/rules.csv').read_bytes())!=RULES_SHA:raise ValueError('Changed dialogue source')
 digest,n=tree_digest(root)
 if digest!=DATA_TREE_SHA or n!=869:raise ValueError('Other non-dialogue data changed')
 if previous_zip:
  with zipfile.ZipFile(previous_zip) as z:
   previous={p.removeprefix('Starsector_PL_ASCII/'):z.read(p) for p in z.namelist() if p.startswith('Starsector_PL_ASCII/data/')}
  if len(previous)!=870:raise ValueError('Incomplete prior 1.0.50 ZIP')
  for p in files:
   rel=p.relative_to(root/'mod').as_posix()
   if previous.get(rel)!=p.read_bytes():raise ValueError(('Changed data from previous release',rel))
 return {'version':'1.0.51','api_map_rows':5269,'corrected_ui_text_rows':2,'changed_java_classes':1,
         'intentional_ldc_operand_changes':2,'other_executable_bytecode_changes':0,
         'technical_personality_ids_preserved':True,'all_870_data_files_unchanged':True,
         'source_map_sha256':OLD_SHA,'target_map_sha256':NEW_SHA,'target_go_sha256':GO_SHA,
         'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.previous_zip),indent=2))
