#!/usr/bin/env python3
"""Package Starsector PL 1.0.45 and verify embedded Windows patcher binaries."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from verify_1045 import check as verify

def sha(b):return hashlib.sha256(b).hexdigest()
def package(root,out,previous_zip=None):
    root=Path(root);out=Path(out)
    if out.exists():raise FileExistsError(out)
    validated=verify(root,previous_zip=previous_zip)
    meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
    if meta['version']!='1.0.45':raise ValueError('Unexpected version')
    installer=(root/'Starsector_PL_Instalator.exe').read_bytes()
    if not installer.startswith(b'MZ') or len(installer)<30_000_000:raise ValueError('Unexpected Windows installer format')
    for exe,embedded in (('obf_windows.exe','obf.bin'),('api_windows.exe','api.bin')):
        b=(root/exe).read_bytes()
        if not b.startswith(b'MZ') or len(b)<1_000_000 or b!=(root/'buildtools/NARZEDZIA_INSTALATOR/bin'/embedded).read_bytes():
            raise ValueError(('Stale patcher binary',exe))
        if installer.count(b)!=1:raise ValueError(('Patcher not embedded exactly once',exe))
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for path in sorted(p for p in (root/'mod').rglob('*') if p.is_file()):
            z.write(path,'Starsector_PL_ASCII/'+path.relative_to(root/'mod').as_posix())
        z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
    with zipfile.ZipFile(out) as z:
        names=z.namelist()
        if len(names)!=873 or len(set(names))!=873 or z.testzip() is not None:raise ValueError('ZIP is damaged')
        if sum(n.startswith('Starsector_PL_ASCII/data/') for n in names)!=870:raise ValueError('Missing game data')
        if any(n.endswith('.jar') for n in names):raise ValueError('Original proprietary JAR bundled')
        if z.read('Starsector_PL_ASCII/Starsector_PL_Instalator.exe')!=installer:raise ValueError('Installer changed in package')
    return {'version':'1.0.45','package':out.name,'bytes':out.stat().st_size,
            'sha256':sha(out.read_bytes()),'entries':873,'data_files':870,
            'new_reviewed_rows':validated['rows_changed'],'built_win64_patchers_exactly_embedded':True}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worktree',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--previous-zip',type=Path)
    a=p.parse_args();print(json.dumps(package(a.worktree,a.out,a.previous_zip),indent=2))
