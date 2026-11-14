#!/usr/bin/env python3
"""Build and verify minimal Windows 1.0.56; no commercial JAR shipped."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1056 import check

def preflight(root):
 v=check(root)
 if (v['unchanged_api_map_entries'],v['changed_dialogue_rows'],v['remaining_gender_tokens'],v['unchanged_other_game_data'])!=(5298,110,2165,869):
  raise ValueError('The v1.0.56 packager/source validation contract does not match')
 return v

def package(root,out):
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError(out)
 preflight(root)
 installer=(root/'Starsector_PL_Instalator.exe').read_bytes()
 if not installer.startswith(b'MZ') or len(installer)<30_000_000:raise ValueError('Invalid Windows installer executable')
 for name,embedded in [('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')]:
  exe=(root/name).read_bytes();assert exe.startswith(b'MZ') and len(exe)>1_000_000
  if exe!=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/embedded).read_bytes() or installer.count(exe)!=1:
   raise ValueError(('Embedded patcher mismatch',name))
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in sorted(f for f in (root/'mod').rglob('*') if f.is_file()):
   z.write(p,'Starsector_PL_ASCII/'+p.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  entries=z.namelist()
  if len(entries)!=873 or len(set(entries))!=873 or z.testzip()!=None:raise ValueError('Damaged or incomplete ZIP')
  if sum(p.startswith('Starsector_PL_ASCII/data/') for p in entries)!=870:raise ValueError('Incomplete game data')
  if any(p.lower().endswith('.jar') for p in entries):raise ValueError('Commercial JAR content included')
  if json.loads(z.read('Starsector_PL_ASCII/mod_info.json'))['version']!='1.0.56':raise ValueError('Wrong mod version')
 return {'release':'1.0.56','file':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'zip_entries':len(entries),'data_files':870,'api_map_unchanged':True,'obf_map_unchanged':True,
 'windows_patchers_embedded_exactly_once':True,'original_commercial_game_JAR_included':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();print(json.dumps(package(a.worktree,a.out),indent=2))
