#!/usr/bin/env python3
"""Minimal Windows v1.0.51 ZIP, exact embedded patcher-byte verification."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1051 import check
sha=lambda b:hashlib.sha256(b).hexdigest()
def package(root,out,previous_zip=None):
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError(out)
 validation=check(root,previous_zip=previous_zip)
 metadata=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if metadata['version']!='1.0.51' or validation['intentional_ldc_operand_changes']!=2:raise ValueError('Invalid release metadata')
 exe=(root/'Starsector_PL_Instalator.exe').read_bytes()
 if not exe.startswith(b'MZ') or len(exe)<30_000_000:raise ValueError('Bad Windows x64 installer')
 for pathname,embedded in [('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')]:
  patcher=(root/pathname).read_bytes()
  if not patcher.startswith(b'MZ') or len(patcher)<1_000_000 or patcher!=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/embedded).read_bytes():
   raise ValueError(('Out-of-date patcher',pathname))
  if exe.count(patcher)!=1:raise ValueError(('Patcher not embedded exactly once',pathname))
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for path in sorted(p for p in (root/'mod').rglob('*') if p.is_file()):
   z.write(path,'Starsector_PL_ASCII/'+path.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  files=z.namelist()
  if len(files)!=873 or len(set(files))!=873 or z.testzip() is not None:raise ValueError('Bad CRC or duplicate ZIP members')
  if sum(x.startswith('Starsector_PL_ASCII/data/') for x in files)!=870:raise ValueError('Missing game data')
  if any(x.endswith('.jar') for x in files):raise ValueError('Original commercial game JAR included')
  if z.read('Starsector_PL_ASCII/Starsector_PL_Instalator.exe')!=exe:raise ValueError('Damaged installer after packaging')
 return {'version':'1.0.51','filename':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),
         'entries':873,'data_files':870,'verified_windows_patcher_embedding':True,
         'jvm_display_ldc_operand_exception_count':2}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--previous-zip',type=Path)
 a=p.parse_args();print(json.dumps(package(a.worktree,a.out,a.previous_zip),indent=2))
