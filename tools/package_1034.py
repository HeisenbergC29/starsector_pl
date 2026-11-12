#!/usr/bin/env python3
"""Assemble minimal 1.0.34 release from the already-verified Starsector worktree."""
import argparse,csv,hashlib,json,zipfile
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def package(root,out,previous):
 mod=root/'mod';data=mod/'data';files=sorted(p for p in data.rglob('*') if p.is_file())
 assert len(files)==870 and all(p.read_bytes().isascii() for p in files)
 info=json.loads((mod/'mod_info.json').read_text('utf8'))
 assert info['version']=='1.0.34' and info['gameVersion']=='0.98a-RC8'
 assert len(info['replace'])==len(set(info['replace']))==41
 assert all((mod/p).is_file() for p in info['replace'])
 if previous:
  with zipfile.ZipFile(previous) as z:
   prior={n.removeprefix('Starsector_PL_ASCII/data/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  assert len(prior)==870
  diff=[p.relative_to(data).as_posix() for p in files if p.read_bytes()!=prior[p.relative_to(data).as_posix()]]
  assert diff==['campaign/rules.csv'],diff
 with (data/'campaign/rules.csv').open(newline='',encoding='ascii') as f: assert len(list(csv.DictReader(f)))==11107
 for exe in ('obf_windows.exe','api_windows.exe','Starsector_PL_Instalator.exe'):
  assert (root/exe).read_bytes()[:2]==b'MZ'
 if out.exists():raise FileExistsError(out)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in sorted((x for x in mod.rglob('*') if x.is_file()),key=lambda p:p.as_posix()):
   z.write(p,'Starsector_PL_ASCII/'+p.relative_to(mod).as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(set(z.namelist()))==873
  assert sum(n.startswith('Starsector_PL_ASCII/data/') for n in z.namelist())==870
  assert not any(n.endswith('.jar') or '/src/' in n for n in z.namelist())
 result={'version':'1.0.34','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'entries':873,'data_files':870,'changed_data_files':1}
 print(json.dumps(result,indent=2));return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--worktree',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--previous',type=Path)
 a=ap.parse_args();package(a.worktree,a.out,a.previous)
