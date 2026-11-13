#!/usr/bin/env python3
"""Validate and package minimal Windows 1.0.55; no proprietary game code shipped."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1055 import check
sha=lambda b:hashlib.sha256(b).hexdigest()
def preflight(root):
 """Assert this packager's output schema and its matching map before building EXEs."""
 validation=check(root)
 if (validation['rows_api'],validation['effective_api_literals'])!=(5298,5296):
  raise ValueError('Wrong v1.0.55 map/package validator contract')
 return validation

def package(root,out):
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError(out)
 validation=preflight(root)
 ins=(root/'Starsector_PL_Instalator.exe').read_bytes()
 if not ins.startswith(b'MZ') or len(ins)<30_000_000:raise ValueError('Invalid Windows PE installer')
 for binary,embedded in [('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')]:
  exe=(root/binary).read_bytes()
  if not exe.startswith(b'MZ') or len(exe)<1_000_000 or exe!=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/embedded).read_bytes() or ins.count(exe)!=1:
   raise ValueError(('Embedded Windows patcher mismatch',binary))
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in sorted(f for f in (root/'mod').rglob('*') if f.is_file()):
   z.write(p,'Starsector_PL_ASCII/'+p.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  entries=z.namelist()
  if len(entries)!=873 or len(set(entries))!=873 or z.testzip() is not None:raise ValueError('ZIP content invalid')
  if sum(x.startswith('Starsector_PL_ASCII/data/') for x in entries)!=870:raise ValueError('Missing any of 870 game data files')
  if any(x.endswith('.jar') for x in entries):raise ValueError('Commercial game-owned JAR leakage')
  if json.loads(z.read('Starsector_PL_ASCII/mod_info.json'))['version']!='1.0.55':raise ValueError('Wrong version metadata')
  if z.read('Starsector_PL_ASCII/Starsector_PL_Instalator.exe')!=ins:raise ValueError('Truncated installer')
 return {'version':'1.0.55','zip_filename':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),
  'zip_entries':len(entries),'data_files':870,'windows_patchers_embedded_exactly_once':True,'commercial_original_JARs_included':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();print(json.dumps(package(a.worktree,a.out),indent=2))