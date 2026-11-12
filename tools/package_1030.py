#!/usr/bin/env python3
"""Create a minimal self-contained Windows mod installer, never game JARs."""
import argparse,csv,hashlib,json,zipfile
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def package(root,out,previous):
 mod=root/'mod';data=mod/'data'
 files=sorted(p for p in data.rglob('*') if p.is_file())
 assert len(files)==870 and all(p.read_bytes().isascii() for p in files)
 if previous:
  with zipfile.ZipFile(previous) as z:
   prev={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  now={p.relative_to(mod).as_posix():p.read_bytes() for p in files}
  assert prev==now,'Unapproved data change'
 meta=json.loads((mod/'mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.30' and meta['gameVersion']=='0.98a-RC8'
 assert len(meta['replace'])==len(set(meta['replace']))==41
 assert all((mod/f).is_file() for f in meta['replace'])
 with (data/'campaign/rules.csv').open(newline='',encoding='ascii') as f:
  assert len(list(csv.DictReader(f)))==11107
 for f in ('obf_windows.exe','api_windows.exe','Starsector_PL_Instalator.exe'):
  assert (root/f).read_bytes()[:2]==b'MZ',f
 assert not out.exists(),out
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in sorted((f for f in mod.rglob('*') if f.is_file()),key=lambda p:p.as_posix()):
   z.write(p,'Starsector_PL_ASCII/'+p.relative_to(mod).as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  names=z.namelist();assert len(names)==len(set(names))==873
  assert sum(n.startswith('Starsector_PL_ASCII/data/') for n in names)==870
  assert not any(n.endswith('.jar') or '/src/' in n for n in names)
 result={'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'entries':873,'data_files':870}
 print(json.dumps(result,indent=2));return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--previous',type=Path)
 a=p.parse_args();package(a.worktree,a.out,a.previous)
