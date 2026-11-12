#!/usr/bin/env python3
"""Reproducible 1.0.40 player ZIP; no proprietary game JARs."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1040 import check

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def package(root,out,prior=None):
 assert not out.exists(),out
 result=check(root,prior_zip=prior)
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.40' and len(meta['replace'])==41
 for exe in ('obf_windows.exe','api_windows.exe','Starsector_PL_Instalator.exe'):
  p=root/exe;assert p.is_file() and p.read_bytes().startswith(b'MZ') and p.stat().st_size>30000,exe
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in sorted((p for p in (root/'mod').rglob('*') if p.is_file()),key=lambda x:x.as_posix()):
   z.write(p,'Starsector_PL_ASCII/'+p.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  names=z.namelist();assert len(names)==len(set(names))==873 and z.testzip() is None
  assert sum(n.startswith('Starsector_PL_ASCII/data/') for n in names)==870
  assert not any(n.endswith('.jar') or '/src/' in n for n in names)
 return {'release':'1.0.40','filename':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'entries':873,'data_files':870,'map_rows':result['api_map_rows'],'checked_gender_variants':result['gendered_snippets'],'original_game_jar_bundled':False}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--worktree',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--previous',type=Path)
 p=a.parse_args();print(json.dumps(package(p.worktree,p.out,p.previous),indent=2))
