#!/usr/bin/env python3
"""Build and CRC-verify 1.0.60 Windows distribution (without commercial JAR)."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1060 import check

def preflight(root:Path)->dict:
 report=check(root)
 required=(report['added_literals'],report['corrected_literals'],report['new_api_map_rows'],report['unchanged_data_files'],report['rendered_combinations'])
 if required!=(5,2,5309,870,16):raise ValueError('Source state inconsistent with release 1.0.60')
 return report

def package(root:Path,out:Path)->dict:
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError(out)
 preflight(root)
 exe=(root/'Starsector_PL_Instalator.exe').read_bytes()
 if not exe.startswith(b'MZ') or len(exe)<30_000_000:raise ValueError('Invalid compiled Windows installer')
 for name,inner in [('api_windows.exe','api.bin'),('obf_windows.exe','obf.bin')]:
  child=(root/name).read_bytes(); embedded=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/inner).read_bytes()
  if not child.startswith(b'MZ') or len(child)<1_000_000 or child!=embedded or exe.count(child)!=1:
   raise ValueError(('Windows patcher not correctly embedded',name))
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for path in sorted(f for f in (root/'mod').rglob('*') if f.is_file()):
   z.write(path,'Starsector_PL_ASCII/'+path.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  names=z.namelist()
  if len(names)!=873 or len(set(names))!=873 or z.testzip() is not None:raise ValueError('Damaged or incomplete Windows ZIP')
  if sum(n.startswith('Starsector_PL_ASCII/data/') for n in names)!=870:raise ValueError('Missing game data')
  if any(n.lower().endswith('.jar') for n in names):raise ValueError('Original commercial JAR in distribution')
  if json.loads(z.read('Starsector_PL_ASCII/mod_info.json')).get('version')!='1.0.60':raise ValueError('Wrong mod version')
 return {'release':'1.0.60','file':out.name,'bytes':out.stat().st_size,
  'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'zip_entries':873,'game_data_files':870,
  'windows_patchers_embedded_once':True,'original_commercial_JAR_included':False,
  'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();print(json.dumps(package(a.worktree,a.out),indent=2))
