#!/usr/bin/env python3
"""Minimal player zip 1.0.39: 870 localized data files, metadata and Windows installer."""
from __future__ import annotations
import argparse,hashlib,json,zipfile,csv
from pathlib import Path
from verify_1039 import verify

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def package(root,out,previous=None):
    assert not out.exists()
    proven=verify(root,previous)
    mod=root/'mod';info=json.loads((mod/'mod_info.json').read_text('utf8'))
    assert info['version']=='1.0.39'
    for name in ('obf_windows.exe','api_windows.exe','Starsector_PL_Instalator.exe'):
        exe=root/name;data=exe.read_bytes();assert data[:2]==b'MZ' and len(data)>30000,name
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in sorted((p for p in mod.rglob('*') if p.is_file()),key=lambda p:p.as_posix()):
            z.write(p,'Starsector_PL_ASCII/'+p.relative_to(mod).as_posix())
        z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
    with zipfile.ZipFile(out) as z:
        names=z.namelist();assert z.testzip() is None
        assert len(names)==len(set(names))==873
        assert sum(name.startswith('Starsector_PL_ASCII/data/') for name in names)==870
        assert not any(name.endswith('.jar') or '/src/' in name for name in names)
    return {'version':'1.0.39','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'entries':873,'data_files':870,'updated_data_files':1,'dialogue_rows_edited':62}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--worktree',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--previous',type=Path);r=a.parse_args();print(json.dumps(package(r.worktree,r.out,r.previous),indent=2))
