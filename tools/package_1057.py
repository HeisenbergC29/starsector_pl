#!/usr/bin/env python3
"""Package and verify the Windows v1.0.57 installer without commercial JARs."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1057 import check

def preflight(root:Path)->dict:
 result=check(root)
 if (result['corrected_dialogue_rows'],result['corrected_grammar_fragments'],result['removed_gender_placeholders'],
     result['remaining_gender_placeholders'],result['api_map_entries_unchanged'],result['other_game_data_files_byte_identical'])!=(70,74,76,2089,5298,869):
  raise ValueError('Unexpected v1.0.57 source/translation contract')
 return result

def package(root:Path,out:Path)->dict:
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError(out)
 preflight(root)
 installer=(root/'Starsector_PL_Instalator.exe').read_bytes()
 if not installer.startswith(b'MZ') or len(installer)<30_000_000:raise ValueError('Incomplete Windows installer EXE')
 for name,embed in [('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')]:
  exe=(root/name).read_bytes()
  if not exe.startswith(b'MZ') or len(exe)<1_000_000 or exe!=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/embed).read_bytes() or installer.count(exe)!=1:
   raise ValueError(('Windows patcher absent, malformed or embedded more than once',name))
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for file in sorted(p for p in (root/'mod').rglob('*') if p.is_file()):
   z.write(file,'Starsector_PL_ASCII/'+file.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  names=z.namelist()
  if len(names)!=873 or len(set(names))!=873 or z.testzip() is not None:raise ValueError('Invalid ZIP / CRC')
  if sum(x.startswith('Starsector_PL_ASCII/data/') for x in names)!=870:raise ValueError('Missing localized data files')
  if any(x.lower().endswith('.jar') for x in names):raise ValueError('Commercial game JAR included')
  if json.loads(z.read('Starsector_PL_ASCII/mod_info.json'))['version']!='1.0.57':
   raise ValueError('Wrong release metadata')
 return {'release':'1.0.57','filename':out.name,'bytes':out.stat().st_size,
  'sha256':hashlib.sha256(out.read_bytes()).hexdigest(), 'zip_entries':873,
  'data_files':870, 'api_mapping_unchanged':True,'obf_mapping_unchanged':True,
  'native_windows_gameplay_tested':False,'windows_patchers_embedded_once':True,
  'original_commercial_JAR_included':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();print(json.dumps(package(a.worktree,a.out),indent=2))
