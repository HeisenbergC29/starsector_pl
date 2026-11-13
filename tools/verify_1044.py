#!/usr/bin/env python3
"""Independent reversible audit of the 1.0.44 text-only delta."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from apply_1034 import rows_with_spans
from apply_1044 import PATCHES,PREVIOUS_SHA,sha,patch_bytes

FINAL_SHA='cf1e35899c5cebd42430cf45242662a6c59389e3330c493c6b667bf2eafb918b'
API_MAP='buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1042.csv'
API_SHA='abaa3521fb8906e9686603ea38252cde5e4b00745761ccb11a7588a410bbb9e9'

def reverse_bytes(cur:bytes):
    if sha(cur)!=FINAL_SHA:raise ValueError('Wrong final release hash')
    rows=rows_with_spans(cur);seen=set();parts=[]
    for start,end,row in rows[1:]:
        key=row[0]
        if key not in PATCHES:continue
        if key in seen:raise ValueError('Duplicate dialogue identifier')
        seen.add(key);block=cur[start:end]
        for old,new in reversed(PATCHES[key]):
            x=new.replace('"','""').encode('ascii');y=old.replace('"','""').encode('ascii')
            if block.count(x)!=1:raise ValueError(('Reverse occurrence',key))
            block=block.replace(x,y,1)
        rec=list(csv.reader(block.decode('ascii').splitlines(keepends=True)))
        if len(rec)!=1 or len(rec[0])!=7 or rec[0][:4]!=row[:4] or rec[0][5:]!=row[5:]:raise ValueError(('Non-text reverse delta',key))
        parts.append((start,end,block))
    if seen!=set(PATCHES):raise ValueError('Inconsistent patch plan')
    result=bytearray();last=0
    for a,b,v in parts:result.extend(cur[last:a]);result.extend(v);last=b
    result.extend(cur[last:]);result=bytes(result)
    if sha(result)!=PREVIOUS_SHA:raise ValueError('Earlier release was not reproduced byte-for-byte')
    return result

def check(root,reference_zip=None):
    root=Path(root);data=(root/'mod/data/campaign/rules.csv').read_bytes()
    before=reverse_bytes(data);reapplied,stats,ledger=patch_bytes(before)
    if reapplied!=data or (stats['rows_changed'],stats['fragments_changed'],stats['gender_references_removed'])!=(25,30,31):raise ValueError('Expected changes not reproduced')
    info=json.loads((root/'mod/mod_info.json').read_text('utf8'))
    if info['version']!='1.0.44' or info['gameVersion']!='0.98a-RC8' or len(info['replace'])!=41:raise ValueError('Invalid metadata')
    if not (root/'mod/CZYTAJ.txt').read_text('utf8').startswith('STARSECTOR PL ASCII 1.0.44'):raise ValueError('Bad readme')
    if 'const edition = "1.0.44"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):raise ValueError('Bad installer')
    amap=root/API_MAP
    if amap.exists() and sha(amap.read_bytes())!=API_SHA:raise ValueError('Unexpected Java API mapping delta')
    files={p.relative_to(root/'mod').as_posix():p.read_bytes() for p in (root/'mod/data').rglob('*') if p.is_file()}
    if len(files)!=870 or any(not b.isascii() for b in files.values()):raise ValueError('Unexpected data set')
    if reference_zip is not None:
        import zipfile
        with zipfile.ZipFile(reference_zip) as z:
            old={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
        if old.keys()!=files.keys() or [k for k in files if old[k]!=files[k]]!=['data/campaign/rules.csv'] or old['data/campaign/rules.csv']!=before:raise ValueError('Data changes outside rules.csv')
    return {**stats,'base_sha256_reproduced':sha(before),'unchanged_data_files':869,'data_files':870,'java_api_map_unmodified':True}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);a.add_argument('--previous',type=Path);v=a.parse_args()
    print(json.dumps(check(v.worktree,v.previous),indent=2))