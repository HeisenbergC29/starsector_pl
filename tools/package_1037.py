#!/usr/bin/env python3
"""Minimal Windows player ZIP; original commercial JAR files are NEVER included."""
from __future__ import annotations
import argparse,csv,hashlib,json,zipfile
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def package(root,out,previous=None):
 mod=root/'mod';data=mod/'data';files=sorted(x for x in data.rglob('*') if x.is_file())
 assert len(files)==870 and all(x.read_bytes().isascii() for x in files)
 meta=json.loads((mod/'mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.37' and meta['gameVersion']=='0.98a-RC8'
 assert len(meta['replace'])==len(set(meta['replace']))==41
 assert all((mod/x).is_file() for x in meta['replace'])
 with (data/'campaign/rules.csv').open(encoding='ascii',newline='') as f:
  assert len(list(csv.DictReader(f)))==11107
 if previous:
  with zipfile.ZipFile(previous) as p:
   prior={n.removeprefix('Starsector_PL_ASCII/'):p.read(n) for n in p.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  current={x.relative_to(mod).as_posix():x.read_bytes() for x in files}
  assert len(prior)==len(current)==870 and prior==current,'data changed since 1.0.36'
 for name in ('obf_windows.exe','api_windows.exe','Starsector_PL_Instalator.exe'):
  assert (root/name).read_bytes()[:2]==b'MZ',name
 assert not out.exists()
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for x in sorted((y for y in mod.rglob('*') if y.is_file()),key=lambda p:p.as_posix()):
   z.write(x,'Starsector_PL_ASCII/'+x.relative_to(mod).as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(set(z.namelist()))==873
  assert sum(n.startswith('Starsector_PL_ASCII/data/') for n in z.namelist())==870
  assert not any(n.endswith('.jar') or '/src/' in n for n in z.namelist())
 result={'version':'1.0.37','file':out.name,'bytes':out.stat().st_size,
 'sha256':sha(out),'entries':873,'data_files':870,'data_changes_vs_1036':0}
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--previous',type=Path)
 a=p.parse_args();package(a.worktree,a.out,a.previous)
