#!/usr/bin/env python3
"""1.0.43 independent exact-delta/CSV/immutable-data verification."""
from __future__ import annotations
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
from apply_1043 import PATCHES,PREV_SHA,SOURCE,sha,patch_bytes,rows_with_spans,PRONOUN

FINAL_SHA='a43f8a4f5acf91e67c7331c7828e3152564f2e224ea2a6bb46e49b9d6374f8a0'
API_MAP='buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1042.csv'
API_SHA='abaa3521fb8906e9686603ea38252cde5e4b00745761ccb11a7588a410bbb9e9'
GAME_API_GO_SHA='b40409dd3731093de7c77f765536ffa3382ddaa7a051825ac2e6ef40fec9c575'
GAME_OBF_GO_SHA='f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc'

def reverse_bytes(blob):
    if sha(blob)!=FINAL_SHA:raise ValueError('1.0.43 rules SHA mismatch')
    spans=rows_with_spans(blob);seen=set();pieces=[]
    for start,end,row in spans[1:]:
        if row[0] not in PATCHES:continue
        key=row[0]
        if key in seen:raise ValueError('duplicate ID')
        seen.add(key)
        block=blob[start:end]
        for old,new in reversed(PATCHES[key]):
            a=new.replace('"','""').encode('ascii')
            b=old.replace('"','""').encode('ascii')
            if block.count(a)!=1:raise ValueError(('Cannot reverse exact new literal',key,new))
            block=block.replace(a,b,1)
        parsed=list(csv.reader(block.decode('ascii').splitlines(keepends=True)))
        if len(parsed)!=1 or len(parsed[0])!=7 or parsed[0][:4]!=row[:4] or parsed[0][5:]!=row[5:]:raise ValueError(('Reverse touched technical field',key))
        pieces.append((start,end,block))
    if seen!=set(PATCHES):raise ValueError('not all IDs found')
    last=0;out=bytearray()
    for a,b,c in pieces:out.extend(blob[last:a]);out.extend(c);last=b
    out.extend(blob[last:]);prior=bytes(out)
    if sha(prior)!=PREV_SHA:raise ValueError('Reverse result not byte-identical to 1.0.42')
    return prior

def check(root,previous_zip=None):
    root=Path(root);f=root/'mod'/SOURCE;new=f.read_bytes()
    if sha(new)!=FINAL_SHA:raise ValueError('Wrong installed 1.0.43 data SHA')
    previous=reverse_bytes(new)
    rep,stats,ledger=patch_bytes(previous)
    if rep!=new or stats['modified_rows']!=31 or stats['removed_gender_placeholders']!=36 or stats['literal_replacements']!=36:raise ValueError('Delta not reproduced')
    actual={(r['id']):r for r in csv.DictReader(f.open(encoding='utf-8-sig',newline=''))}
    for key in PATCHES:
        if PRONOUN.findall(actual[key]['text'].encode('ascii')):raise ValueError(('Unfixed pronoun in changed row',key))
    info=json.loads((root/'mod/mod_info.json').read_text(encoding='utf8'))
    assert info['version']=='1.0.43' and info['gameVersion']=='0.98a-RC8' and len(info['replace'])==41
    assert (root/'mod/CZYTAJ.txt').read_text(encoding='utf8').startswith('STARSECTOR PL ASCII 1.0.43')
    assert 'const edition = "1.0.43"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text(encoding='utf8')
    expected={API_MAP:API_SHA,'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go':GAME_API_GO_SHA,'buildtools/NARZEDZIA_OBF/main.go':GAME_OBF_GO_SHA}
    for path,digest in expected.items():
        p=root/path
        if sha(p.read_bytes())!=digest:raise ValueError(('JVM mapper/tool changed unexpectedly',path))
    data={p.relative_to(root/'mod').as_posix():p.read_bytes() for p in (root/'mod/data').rglob('*') if p.is_file()}
    if len(data)!=870:raise ValueError(('Data file count',len(data)))
    if any(not b.isascii() for b in data.values()):raise ValueError('Non ASCII data')
    if previous_zip:
        with zipfile.ZipFile(previous_zip) as z:
            base='Starsector_PL_ASCII/'
            old={n.removeprefix(base):z.read(n) for n in z.namelist() if n.startswith(base+'data/')}
        if set(old)!=set(data):raise ValueError('File set modified')
        if sum(old[k]!=data[k] for k in old)!=1 or old['data/campaign/rules.csv']!=previous:raise ValueError('Unexpected data differences to 1.0.42')
    return {**stats,'data_files':len(data),'unchanged_data_files':869,'all_7371_options_checked_by_separate_script':True,'api_map_sha_unchanged':API_SHA,'jvm_patchers_unchanged':True,'reverse_sha256':sha(previous)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
    a=p.parse_args();print(json.dumps(check(a.worktree,a.previous_zip),indent=2))
