#!/usr/bin/env python3
"""Package Windows v1.0.66 and enforce review, CRC and noncommercial distribution."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1066 import check

def preflight(root:Path)->dict:
 v=check(root)
 if v['historical_api_unreviewed']!=2927 or v['gameplay_testing']!='after_1_1_release':
  raise ValueError('Incomplete API review backlog or incorrect gameplay test policy')
 if (v['historical_api_reviews_total'],v['new_unique_historical_reviews'],v['mapped_class_scoped_literals'],v['corrected_ui_fragments'],v['rendered_combinations'],v['unchanged_game_data_files'])!=(731,114,205,9,60,870):
  raise ValueError('Incorrect 1.0.66 release contract')
 return v

def package(root:Path,out:Path)->dict:
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError('ZIP cannot be overwritten')
 preflight(root)
 exe=(root/'Starsector_PL_Instalator.exe').read_bytes()
 if not exe.startswith(b'MZ') or len(exe)<30_000_000:raise ValueError('Invalid x64 Windows installer')
 for name,inside in [('api_windows.exe','api.bin'),('obf_windows.exe','obf.bin')]:
  child=(root/name).read_bytes();embed=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/inside).read_bytes()
  if not child.startswith(b'MZ') or len(child)<1_000_000 or child!=embed or exe.count(child)!=1:
   raise ValueError(('Expected identical embedded patcher exactly once',name))
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for f in sorted(x for x in (root/'mod').rglob('*') if x.is_file()):
   z.write(f,'Starsector_PL_ASCII/'+f.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  entries=z.namelist()
  if len(entries)!=873 or len(set(entries))!=873 or z.testzip() is not None:raise ValueError('Incomplete/damaged distribution')
  if sum(x.startswith('Starsector_PL_ASCII/data/') for x in entries)!=870:raise ValueError('Missing localizable game data')
  if any(x.lower().endswith('.jar') for x in entries):raise ValueError('Commercial game JAR included')
  if json.loads(z.read('Starsector_PL_ASCII/mod_info.json'))['version']!='1.0.66':raise ValueError('Incorrect mod version')
 return {'release':'1.0.66','filename':out.name,'bytes':out.stat().st_size,
   'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'zip_entries':873,'data_files':870,
   'native_windows_gameplay_tested':False,'original_commercial_jar_included':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();print(json.dumps(package(a.worktree,a.out),indent=2))
