#!/usr/bin/env python3
"""Exact text-only 1.0.34 -> 1.0.35 delta; reversible, CRC, columns, game IDs."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,zipfile
from pathlib import Path
from apply_1034 import rows_with_spans
from apply_1035 import PATCHES,OPTION_IDS,SOURCE,OLD_SHA,NEW_SHA,PRONOUN,patch_bytes,sha

OBF_GO_SHA='f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc'
API_GO_SHA='f7c790b9a24004ae1a3349a9cf7c020b035546ee05290d7ba11245e375d0a486'
OBF_MAP_SHA='f2ffdb534d870a49fce81dea47b4ebbac8fdccc218b79d5bed0f3752485cd484'
API_MAP_SHA='77f6f2350c920aa1c0d9867cb90ecb3eb4dcf723579dc1bff5ec846c32d86421'

def revert(data):
 if sha(data)!=NEW_SHA:raise ValueError('Incorrect 1.0.35 checksum')
 spans=rows_with_spans(data); fragments=[];cursor=0;found=set()
 for start,end,row in spans[1:]:
  key=row[0]
  if key not in PATCHES:continue
  if key in found:raise ValueError(('duplicate',key))
  found.add(key);block=data[start:end]
  for before,after in reversed(PATCHES[key]):
   a,b=after.encode('ascii'),before.encode('ascii')
   if block.count(a)!=1:raise ValueError(('nonreversible',key,after,block.count(a)))
   block=block.replace(a,b,1)
  fragments.extend([data[cursor:start],block]);cursor=end
 fragments.append(data[cursor:]);prior=b''.join(fragments)
 assert found==set(PATCHES) and sha(prior)==OLD_SHA
 return prior

def rows(b):
 with io.StringIO(b.decode('ascii'),newline='') as f:
  data=list(csv.DictReader(f));assert len(data)==11107
  return {r['id']:r for r in data}

def check(root,previous=None):
 mod=root/'mod';p=mod/SOURCE;current=p.read_bytes()
 assert sha(current)==NEW_SHA and current.isascii()
 prior=revert(current);new,stat=patch_bytes(prior)
 assert new==current
 assert stat['changed_rows']==64 and stat['exact_replacements']==93 and stat['gender_variables_removed']==108
 assert stat['remaining_variables_in_changed_rows']==0
 before=rows(prior);after=rows(current)
 assert len(before)==len(after) and set(before)==set(after)
 for name in before:
  diff={field for field in before[name] if before[name][field]!=after[name][field]}
  expected={'text','options'} if name in OPTION_IDS else {'text'} if name in PATCHES else set()
  assert diff==expected,(name,diff,expected)
  if name in PATCHES:
   assert PRONOUN.search((after[name]['text']+' '+after[name]['options']).encode('ascii')) is None,name
   if name in OPTION_IDS:
    oldid=[ln.split(':',1)[0] for ln in before[name]['options'].splitlines()]
    newid=[ln.split(':',1)[0] for ln in after[name]['options'].splitlines()]
    assert oldid==newid and len(oldid)==1
 data=sorted(p for p in (mod/'data').rglob('*') if p.is_file())
 assert len(data)==870 and all(x.read_bytes().isascii() for x in data)
 if previous:
  with zipfile.ZipFile(previous) as z:
   assert z.testzip() is None
   original={n.removeprefix('Starsector_PL_ASCII/data/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  assert len(original)==870
  diff=sorted(x.relative_to(mod/'data').as_posix() for x in data if x.read_bytes()!=original[x.relative_to(mod/'data').as_posix()])
  assert diff==['campaign/rules.csv'],diff
  assert original['campaign/rules.csv']==prior
 info=json.loads((mod/'mod_info.json').read_text('utf8'))
 assert info['version']=='1.0.35' and info['gameVersion']=='0.98a-RC8'
 assert len(info['replace'])==len(set(info['replace']))==41
 assert all((mod/rel).exists() for rel in info['replace'])
 assert 'STARSECTOR PL ASCII 1.0.35' in (mod/'CZYTAJ.txt').read_text('utf8')
 obf=root/'buildtools/NARZEDZIA_OBF';api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 assert 'const currentPatchState = "patched 10133"' in (obf/'main.go').read_text('utf8')
 assert 'const version = "1033"' in (api/'main.go').read_text('utf8')
 assert sha((obf/'main.go').read_bytes())==OBF_GO_SHA
 assert sha((api/'main.go').read_bytes())==API_GO_SHA
 assert sha((obf/'TLUMACZENIA_OBF_10133.csv').read_bytes())==OBF_MAP_SHA
 assert sha((api/'translations/TLUMACZENIA_JAR_1033.csv').read_bytes())==API_MAP_SHA
 assert 'const edition = "1.0.35"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 # runtime parser regression - 7371 options, no invalid triplets/colons.
 import importlib.util
 spec=importlib.util.spec_from_file_location('options_checker',root/'maintenance/check_rules_options.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 count,errs=m.audit(current)
 assert count==7371 and not errs,(count,errs[:3])
 return {**stat,'rows_in_rules_csv':len(before),'valid_options':count,'unchanged_other_data_files':869,'obf_and_api_maps':'identical_to_1.0.34','revert_sha256':sha(prior)}

if __name__=='__main__':
 arg=argparse.ArgumentParser();arg.add_argument('worktree',type=Path)
 arg.add_argument('--previous-zip',type=Path);a=arg.parse_args()
 print(json.dumps(check(a.worktree,a.previous_zip),indent=2))
