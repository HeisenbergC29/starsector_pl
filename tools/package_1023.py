#!/usr/bin/env python3
"""1.0.23 player ZIP: 870 unchanged game data + mod metadata + Windows installer.
Never embeds proprietary game JARs, development tools or untranslated originals.
"""
import argparse,csv,hashlib,json,zipfile
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def package(root,out,previous):
    mod=root/'mod'; data=mod/'data'; files=sorted(p for p in data.rglob('*') if p.is_file())
    assert len(files)==870
    assert all(p.read_bytes().isascii() for p in files)
    if previous:
        with zipfile.ZipFile(previous) as z:
            prior={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
        current={p.relative_to(mod).as_posix():p.read_bytes() for p in files}
        assert prior==current,('unapproved data changes between 1.0.22 and 1.0.23')
    meta=json.loads((mod/'mod_info.json').read_text('utf8'))
    assert meta['version']=='1.0.23' and meta['gameVersion']=='0.98a-RC8'
    assert len(meta['replace'])==len(set(meta['replace']))==41
    assert all((mod/f).is_file() for f in meta['replace'])
    with (data/'campaign/rules.csv').open(newline='',encoding='ascii') as f:
        assert len(list(csv.DictReader(f)))==11107
    for f in ('obf_windows.exe','api_windows.exe','Starsector_PL_Instalator.exe'):
        assert (root/f).read_bytes()[:2]==b'MZ',f
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in sorted((x for x in mod.rglob('*') if x.is_file()),key=lambda p:p.as_posix()):
            z.write(p,'Starsector_PL_ASCII/'+p.relative_to(mod).as_posix())
        z.write(root/'Starsector_PL_Instalator.exe','Starsector_PL_ASCII/Starsector_PL_Instalator.exe')
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        names=z.namelist();assert len(names)==len(set(names))==873
        assert sum(n.startswith('Starsector_PL_ASCII/data/') for n in names)==870
        assert not any(n.endswith('.jar') or '/src/' in n for n in names)
    print(json.dumps({'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'entries':873,'data':870},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--worktree',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--previous',type=Path)
    a=ap.parse_args();package(a.worktree,a.out,a.previous)