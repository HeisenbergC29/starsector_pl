#!/usr/bin/env python3
"""Package 1.0.44 without commercial game JARs; validate actual embedded Windows patchers."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1044 import check as verify

def sha(data):return hashlib.sha256(data).hexdigest()

def package(root,out,prior=None):
 root=Path(root);out=Path(out)
 if out.exists():raise FileExistsError(out)
 validation=verify(root,reference_zip=prior)
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.44' and len(meta['replace'])==41
 inst=(root/'Starsector_PL_Instalator.exe').read_bytes()
 assert inst.startswith(b'MZ') and len(inst)>30_000_000
 for exe,name in (('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')):
  contents=(root/exe).read_bytes()
  assert contents.startswith(b'MZ') and len(contents)>1_000_000
  assert contents==(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/name).read_bytes(),('stale installer bundle',exe)
  assert inst.count(contents)==1,('stale installer embedded binary',exe)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for path in sorted((p for p in (root/'mod').rglob('*') if p.is_file()),key=lambda p:p.as_posix()):
   z.write(path,'Starsector_PL_ASCII/'+path.relative_to(root/'mod').as_posix())
  z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
 with zipfile.ZipFile(out) as z:
  names=z.namelist()
  assert len(names)==len(set(names))==873 and z.testzip() is None
  assert sum(n.startswith('Starsector_PL_ASCII/data/') for n in names)==870
  assert not any(n.endswith('.jar') or '/src/' in n for n in names)
  assert z.read('Starsector_PL_ASCII/Starsector_PL_Instalator.exe')==inst
 return {'version':'1.0.44','package':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'entries':873,'data_files':870,'modified_rules_rows':validation['rows_changed'],'win64_patchers_exactly_embedded':True,'original_jar_bundled':False}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--worktree',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--previous',type=Path)
 x=a.parse_args();print(json.dumps(package(x.worktree,x.out,x.previous),indent=2))