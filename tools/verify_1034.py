#!/usr/bin/env python3
"""Strict independent delta and reverse reconstruction for Starsector PL 1.0.34."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path
from apply_1034 import PATCHES,ALLOWED_FIELDS,SOURCE,OLD_SHA,NEW_SHA,rows_with_spans,translate_bytes

EXPECTED = {'changed_rows':27,'edits':62,'removed_variable_references':75,'rows':11107}
OTHER_869_MANIFEST='5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1'
OBF_GO_SHA='f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc'
API_GO_SHA='f7c790b9a24004ae1a3349a9cf7c020b035546ee05290d7ba11245e375d0a486'
OBF_MAP_SHA='f2ffdb534d870a49fce81dea47b4ebbac8fdccc218b79d5bed0f3752485cd484'
API_MAP_SHA='77f6f2350c920aa1c0d9867cb90ecb3eb4dcf723579dc1bff5ec846c32d86421'


def sha(b):return hashlib.sha256(b).hexdigest()

def revert(data):
 spans=rows_with_spans(data);index={row[0]:(start,end,row) for start,end,row in spans}
 pieces=[];cursor=0
 for key,(start,end,_) in sorted(((name,index[name]) for name in PATCHES),key=lambda t:t[1][0]):
  block=data[start:end]
  for before,after in reversed(PATCHES[key]):
   old=after.encode('ascii');new=before.encode('ascii')
   if block.count(old)!=1:raise AssertionError((key,'inverse must be unique',after,block.count(old)))
   block=block.replace(old,new,1)
  pieces.extend([data[cursor:start],block]);cursor=end
 pieces.append(data[cursor:]);return b''.join(pieces)

def check(root,previous_zip=None):
 mod=root/'mod';data=mod/'data';p=mod/SOURCE
 final=p.read_bytes();assert sha(final)==NEW_SHA
 prior=revert(final);assert sha(prior)==OLD_SHA
 expected,summary=translate_bytes(prior);assert expected==final
 for key,val in EXPECTED.items():assert summary[key]==val,(key,summary[key])
 rows_old={r['id']:r for r in csv.DictReader(io.StringIO(prior.decode('ascii'),newline=''))}
 rows_new={r['id']:r for r in csv.DictReader(io.StringIO(final.decode('ascii'),newline=''))}
 assert len(rows_new)==len(rows_old) and len(rows_new)>10000
 assert set(rows_new)==set(rows_old)
 for name in PATCHES:
  diffs={field for field in rows_new[name] if rows_new[name][field]!=rows_old[name][field]}
  assert diffs==ALLOWED_FIELDS[name],(name,diffs)
  assert not re.search(r'\$(?:gaTJ|gaFC_KBA|lpt|locrlf)_[A-Za-z]*(?:HeOrShe|heOrShe|HimOrHer|himOrHer|HisOrHer|hisOrHer|manOrWoman)|\$(?:HisOrHer|hisOrHer|HeOrShe|heOrShe)\b',
     ' '.join(rows_new[name][field] for field in diffs)),name
 meta=json.loads((mod/'mod_info.json').read_text(encoding='utf8'))
 assert meta['version']=='1.0.34' and meta['gameVersion']=='0.98a-RC8'
 assert len(meta['replace'])==len(set(meta['replace']))==41
 assert '1.0.34' in (mod/'CZYTAJ.txt').read_text('utf8')
 assert 'const edition = "1.0.34"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 obf=root/'buildtools/NARZEDZIA_OBF';api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 # A data-only release: both JAR maps and Go patchers retain 1.0.33 state.
 assert 'const currentPatchState = "patched 10133"' in (obf/'main.go').read_text('utf8')
 assert 'const version = "1033"' in (api/'main.go').read_text('utf8')
 assert (obf/'TLUMACZENIA_OBF_10133.csv').exists()
 assert (api/'translations/TLUMACZENIA_JAR_1033.csv').exists()
 assert sha((obf/'main.go').read_bytes())==OBF_GO_SHA
 assert sha((api/'main.go').read_bytes())==API_GO_SHA
 assert sha((obf/'TLUMACZENIA_OBF_10133.csv').read_bytes())==OBF_MAP_SHA
 assert sha((api/'translations/TLUMACZENIA_JAR_1033.csv').read_bytes())==API_MAP_SHA
 datafiles=sorted(p for p in data.rglob('*') if p.is_file())
 assert len(datafiles)==870 and all(f.read_bytes().isascii() for f in datafiles)
 others=b''.join(f.relative_to(data).as_posix().encode('ascii')+b'\0'+hashlib.sha256(f.read_bytes()).digest() for f in datafiles if f!=p)
 assert sha(others)==OTHER_869_MANIFEST,'Unexpected changes to other 869 data files'
 from importlib.util import spec_from_file_location,module_from_spec
 checker=root/'maintenance/check_rules_options.py'
 spec=spec_from_file_location('valid_options_1034',checker);m=module_from_spec(spec);spec.loader.exec_module(m)
 count,errors=m.audit(final);assert count==7371 and not errors,(count,errors[:2])
 if previous_zip:
  with zipfile.ZipFile(previous_zip) as z:
   assert z.testzip() is None
   prefix='Starsector_PL_ASCII/data/'
   prev={name[len(prefix):]:z.read(name) for name in z.namelist() if name.startswith(prefix) and not name.endswith('/')}
  assert len(prev)==870
  for f in datafiles:
   rel=f.relative_to(data).as_posix()
   if rel==SOURCE[len('data/'):]:assert f.read_bytes()!=prev[rel]
   else:assert f.read_bytes()==prev[rel],rel
 return {'release':'1.0.34','corrected_dialogue_rows':27,'exact_replacements':62,
         'unrendered_gender_placeholders':75,'rules_lines':11107,'rules_options':7371,
         'byte_identical_unaffected_data_files':869,
         'obf_api_maps':'identical_to_1.0.33','rules_sha256':sha(final)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.previous_zip),indent=2))
