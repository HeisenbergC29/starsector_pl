#!/usr/bin/env python3
"""Verify 1.0.29 additions are class-scoped UI strings, without touching earlier maps."""
from __future__ import annotations
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
from apply_1029 import OBF,API,STATUS,PREV_OBF_SHA,NEW_OBF_SHA
FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def rows(p):
 with p.open('r',encoding='utf-8',newline='') as f:
  c=csv.DictReader(f);assert c.fieldnames==FIELDS
  return list(c)

def expected(mapping):
 return [dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS)
         for cl,parts in mapping.items() for en,pl in parts.items()]

def verify_delta(old,new,mapping,n):
 items=expected(mapping)
 assert len(items)==n and new[:len(old)]==old and new[len(old):]==items
 assert len({(r['source_class'],r['english_literal']) for r in new})==len(new)
 for r in items:
  en,pl=r['english_literal'],r['polish_ascii_draft']
  assert en!=pl and en.isascii() and pl.isascii()
  assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' ')
  assert en.count('\n')==pl.count('\n')

def check(root,old_zip=None):
 b=root/'buildtools';o=b/'NARZEDZIA_OBF';a=b/'NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old_o=rows(o/'TLUMACZENIA_OBF_10128.csv');new_o=rows(o/'TLUMACZENIA_OBF_10129.csv')
 old_a=rows(a/'translations/TLUMACZENIA_JAR_1028.csv');new_a=rows(a/'translations/TLUMACZENIA_JAR_1029.csv')
 assert len(old_o)==3485 and len(old_a)==5208
 verify_delta(old_o,new_o,OBF,23);verify_delta(old_a,new_a,API,7)
 go=(o/'main.go').read_text('utf-8');api=(a/'main.go').read_text('utf-8')
 for fragment in ['const currentPatchState = "patched 10129"','loadTranslations("TLUMACZENIA_OBF_10129.csv")',f'"{PREV_OBF_SHA}": "10128"']:
  assert fragment in go,fragment
 for fragment in ['const version = "1029"','const exeVersion = "1.0.29"',f'const expectedOBFPatched10129 = "{NEW_OBF_SHA}"','hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10129']:
  assert fragment in api,fragment
 assert 'const edition = "1.0.29"' in (b/'NARZEDZIA_INSTALATOR/main.go').read_text('utf-8')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf-8'))
 assert meta['version']=='1.0.29' and meta['gameVersion']=='0.98a-RC8' and len(meta['replace'])==41
 mod=root/'mod';files={p.relative_to(mod).as_posix():p.read_bytes() for p in (mod/'data').rglob('*') if p.is_file()}
 assert len(files)==870 and all(v.isascii() for v in files.values())
 if old_zip:
  with zipfile.ZipFile(old_zip) as z:
   prior={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  assert files==prior,('unexpected changes in data files',set(files)^set(prior))
 return {'OBF_added':23,'API_added':7,'OBF_total':len(new_o),'API_total_rows':len(new_a),'unchanged_data_files':870,'technical_ids_unchanged':True}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
 args=p.parse_args();print(json.dumps(check(args.worktree,args.previous_zip),indent=2))
