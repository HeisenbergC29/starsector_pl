#!/usr/bin/env python3
"""1.0.53 Windows x64 minimal release with both exact embedded patchers."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1053 import check
sha=lambda b:hashlib.sha256(b).hexdigest()

def package(root,out):
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError('Refuse to overwrite existing release')
 if check(root)['new_recovery_ui_entries']!=3:raise ValueError('Missing new translated OBF UI fragments')
 installer=(root/'Starsector_PL_Instalator.exe').read_bytes()
 if not installer.startswith(b'MZ') or len(installer)<30_000_000:raise ValueError('Installer is not a valid expected PE32+ exe')
 for path,embedded in (('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')):
  binary=(root/path).read_bytes();bundled=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/embedded).read_bytes()
  if not binary.startswith(b'MZ') or len(binary)<1_000_000 or binary!=bundled or installer.count(binary)!=1:
   raise ValueError(('Windows x64 patcher was not embedded exactly once',path))
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for f in sorted(p for p in (root/'mod').rglob('*') if p.is_file()):
   z.write(f,'Starsector_PL_ASCII/'+f.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  files=z.namelist()
  if len(files)!=873 or len(files)!=len(set(files)) or z.testzip() is not None:raise ValueError('Bad ZIP CRC/entries')
  if sum(x.startswith('Starsector_PL_ASCII/data/') for x in files)!=870:raise ValueError('Missing game data files')
  if any(x.endswith('.jar') for x in files):raise ValueError('Commercial original JAR leaked into release')
  if json.loads(z.read('Starsector_PL_ASCII/mod_info.json'))['version']!='1.0.53':raise ValueError('Incorrect mod release')
  if z.read('Starsector_PL_ASCII/Starsector_PL_Instalator.exe')!=installer:raise ValueError('Corrupt embedded installer')
 return {'version':'1.0.53','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),
  'zip_entries':873,'data_files':870,'obf_recovery_ui_fragments_fixed':3,
  'two_windows_patchers_embedded_exactly_once':True,'no_commercial_JAR':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();print(json.dumps(package(a.worktree,a.out),indent=2))
