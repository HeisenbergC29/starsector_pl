#!/usr/bin/env python3
"""Minimal v1.0.47 Windows package with byte-exact embedded patcher verification."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1047 import check
sha=lambda data:hashlib.sha256(data).hexdigest()

def package(root,out,previous_zip=None):
    root=Path(root);out=Path(out)
    if out.exists():raise FileExistsError(out)
    validate=check(root,previous_zip=previous_zip)
    meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
    if meta['version']!='1.0.47' or validate['changes']!=14:raise ValueError('Wrong release')
    installer=(root/'Starsector_PL_Instalator.exe').read_bytes()
    if not installer.startswith(b'MZ') or len(installer)<30_000_000:raise ValueError('Windows installer invalid')
    for exe,embedded in (('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')):
        b=(root/exe).read_bytes()
        if not b.startswith(b'MZ') or len(b)<1_000_000 or b!=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/embedded).read_bytes():
            raise ValueError(('Unexpected embedded patcher bytes',exe))
        if installer.count(b)!=1:raise ValueError(('Patcher not embedded exactly once',exe))
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for path in sorted(p for p in (root/'mod').rglob('*') if p.is_file()):
            z.write(path,'Starsector_PL_ASCII/'+path.relative_to(root/'mod').as_posix())
        z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
    with zipfile.ZipFile(out) as z:
        names=z.namelist()
        if len(names)!=873 or len(set(names))!=873 or z.testzip() is not None:
            raise ValueError('Package CRC/structure mismatch')
        if sum(n.startswith('Starsector_PL_ASCII/data/') for n in names)!=870:
            raise ValueError('Not all 870 data files included')
        if any(n.endswith('.jar') for n in names):raise ValueError('Commercial game-owned JAR included')
        if z.read('Starsector_PL_ASCII/Starsector_PL_Instalator.exe')!=installer:raise ValueError('Embedded installer changed')
    return {'version':'1.0.47','file':out.name,'bytes':out.stat().st_size,
            'sha256':sha(out.read_bytes()),'zip_entries':873,'localized_data_files':870,
            'numeric_api_texts_fixed':14,'windows_x64_patchers_exactly_embedded':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--previous-zip',type=Path)
    a=p.parse_args();print(json.dumps(package(a.worktree,a.out,a.previous_zip),indent=2))
