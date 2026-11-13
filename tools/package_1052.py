#!/usr/bin/env python3
"""1.0.52 minimal Windows release; verify embedded patcher binaries and all CRCs."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1052 import check
sha=lambda b:hashlib.sha256(b).hexdigest()

def package(root,out,previous_zip=None):
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError('Refusing to overwrite existing release')
 ver=check(root,previous_zip)
 if ver['map_rows']!=5283 or ver['new_java_bytecode_edits']!=0:raise ValueError('Unexpected API translation scope')
 exe=(root/'Starsector_PL_Instalator.exe').read_bytes()
 if not exe.startswith(b'MZ') or len(exe)<30_000_000:raise ValueError('Invalid Windows installer EXE')
 for name,inner in [('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')]:
  binary=(root/name).read_bytes();bundled=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/inner).read_bytes()
  if not binary.startswith(b'MZ') or len(binary)<1_000_000 or binary!=bundled or exe.count(binary)!=1:
   raise ValueError(('Wrong/missing exactly embedded Windows x64 patcher',name))
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for f in sorted(p for p in (root/'mod').rglob('*') if p.is_file()):
   z.write(f,'Starsector_PL_ASCII/'+f.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  members=z.namelist()
  if len(members)!=873 or len(set(members))!=873 or z.testzip() is not None:
   raise ValueError('Package CRC/member test failed')
  if sum(x.startswith('Starsector_PL_ASCII/data/') for x in members)!=870:
   raise ValueError('Some original source data missing')
  if any(x.endswith('.jar') for x in members):raise ValueError('Original proprietary JAR was included')
  info=json.loads(z.read('Starsector_PL_ASCII/mod_info.json').decode())
  if info['version']!='1.0.52':raise ValueError('Incorrect ZIP metadata version')
 return {'version':'1.0.52','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),
   'zip_entries':873,'localized_data_files':870,'new_class_scoped_literals':14,'corrected_existing_phrases':10,
   'patcher_windows_exe_embedded_exactly_once':True,'original_commercial_jar_present':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--previous-zip',type=Path)
 a=p.parse_args();print(json.dumps(package(a.worktree,a.out,a.previous_zip),indent=2))
