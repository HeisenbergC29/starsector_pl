#!/usr/bin/env python3
"""Strict one-file data delta and status-map integrity for 1.0.31."""
from __future__ import annotations
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
from apply_1031 import SOURCE,BEFORE,AFTER,OLD_SHA,NEW_SHA,translate_text

ORIGINAL_DATA_AGG='da8d09e99246e937d02a4f92209e832c09749aefb1cb996b68da84392a013e71'
UPDATED_DATA_AGG='afca45b81cf95dc87c29a0067bf3a67f84786d471b7563cf9e9731745a455286'

def digest_data(root):
    h=hashlib.sha256()
    files=sorted(p for p in root.rglob('*') if p.is_file())
    for p in files:
        path=p.relative_to(root).as_posix().encode('utf8');h.update(len(path).to_bytes(4,'big'))
        h.update(path);h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest(),len(files)

def verify(worktree:Path,prior=None):
    mod=worktree/'mod';source=(mod/SOURCE).read_bytes()
    assert hashlib.sha256(source).hexdigest()==NEW_SHA
    assert AFTER in source and BEFORE not in source
    assert source.count(b'\r\n')==86 and source.count(b'\n')==86
    old=source.replace(AFTER,BEFORE,1)
    assert hashlib.sha256(old).hexdigest()==OLD_SHA and translate_text(old)==source
    digest,count=digest_data(mod/'data')
    assert count==870 and digest==UPDATED_DATA_AGG,(count,digest)
    assert all(p.read_bytes().isascii() for p in (mod/'data').rglob('*') if p.is_file())
    meta=json.loads((mod/'mod_info.json').read_text('utf8'))
    assert meta['version']=='1.0.31' and meta['gameVersion']=='0.98a-RC8'
    assert len(meta['replace'])==len(set(meta['replace']))==41
    assert SOURCE not in meta['replace']
    assert 'STARSECTOR PL ASCII 1.0.31' in (mod/'CZYTAJ.txt').read_text('utf8')
    assert 'const edition = "1.0.31"' in (worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
    obf=worktree/'buildtools/NARZEDZIA_OBF/TLUMACZENIA_OBF_10130.csv'
    api=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1030.csv'
    assert len(list(csv.DictReader(obf.open(newline='',encoding='utf8'))))==3510
    assert len(list(csv.DictReader(api.open(newline='',encoding='utf8'))))==5219
    # Existing Go patchers remain frozen: 1.0.31 ONLY changes a Java source UI string.
    assert 'const currentPatchState = "patched 10130"' in (worktree/'buildtools/NARZEDZIA_OBF/main.go').read_text('utf8')
    assert 'const version = "1030"' in (worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
    if prior:
        with zipfile.ZipFile(prior) as z:
            data={name.removeprefix('Starsector_PL_ASCII/'):z.read(name) for name in z.namelist()
                  if name.startswith('Starsector_PL_ASCII/data/') and not name.endswith('/')}
        assert len(data)==870
        now={p.relative_to(mod).as_posix():p.read_bytes() for p in (mod/'data').rglob('*') if p.is_file()}
        diffs={k for k in now if data.get(k)!=now[k]}
        assert diffs=={SOURCE},diffs
        assert hashlib.sha256(data[SOURCE]).hexdigest()==OLD_SHA
    return {'mod_version':'1.0.31','data_files':870,'changed_data_files':1,
            'java_source_old_sha256':OLD_SHA,'java_source_new_sha256':NEW_SHA,
            'data_aggregate_sha256':UPDATED_DATA_AGG,'jar_patchers':'unchanged from 1.0.30',
            'native_gameplay_tested':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
    a=p.parse_args();print(json.dumps(verify(a.worktree,a.previous_zip),indent=2))
if __name__=='__main__':main()
