#!/usr/bin/env python3
"""CRC-verified minimal Windows Starsector PL 1.0.49 distribution (no original proprietary JARs)."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1049 import check
sha=lambda b:hashlib.sha256(b).hexdigest()
def package(root,out,previous_zip=None):
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError(out)
 verified=check(root,previous_zip)
 if verified['new_map_rows']!=5261:raise ValueError('Unexpected API mapping count')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if meta['version']!='1.0.49':raise ValueError('Unexpected mod version')
 installer=(root/'Starsector_PL_Instalator.exe').read_bytes()
 if not installer.startswith(b'MZ') or len(installer)<30_000_000:raise ValueError('Missing compiled Windows installer')
 for exe,embedded in (('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')):
  b=(root/exe).read_bytes()
  if not b.startswith(b'MZ') or len(b)<1_000_000 or b!=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/embedded).read_bytes():
   raise ValueError(('Windows patcher stale or missing from embedded installer',exe))
  if installer.count(b)!=1:raise ValueError(('Actual executable not embedded exactly once',exe))
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for f in sorted(p for p in (root/'mod').rglob('*') if p.is_file()):
   z.write(f,'Starsector_PL_ASCII/'+f.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  names=z.namelist()
  if len(names)!=873 or len(set(names))!=873 or z.testzip() is not None:raise ValueError('ZIP CRC or file-list mismatch')
  if sum(n.startswith('Starsector_PL_ASCII/data/') for n in names)!=870:raise ValueError('Missing localized data')
  if any(n.endswith('.jar') for n in names):raise ValueError('Proprietary JAR present in distributable')
  if z.read('Starsector_PL_ASCII/Starsector_PL_Instalator.exe')!=installer:raise ValueError('Installer changed during packaging')
 return {'release':'1.0.49','package':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),
  'entries':873,'data_files':870,'api_strings_modified':13,'new_class_scoped_plural_suffix_rule':1,
  'win64_installer_contains_exact_built_patchers':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--prior-zip',type=Path)
 a=p.parse_args();print(json.dumps(package(a.worktree,a.out,a.prior_zip),indent=2))
