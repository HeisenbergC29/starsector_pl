#!/usr/bin/env python3
"""Independent offline verification of the 1.0.45 data-only change set."""
from __future__ import annotations
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
from apply_1034 import rows_with_spans
from apply_1045 import PATCHES,PREVIOUS_SHA,patch_bytes,sha,GENDER

FINAL_SHA='e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a'
API_MAP='buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1042.csv'
API_SHA='abaa3521fb8906e9686603ea38252cde5e4b00745761ccb11a7588a410bbb9e9'
JAVA_MAINS={
 'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go':'b40409dd3731093de7c77f765536ffa3382ddaa7a051825ac2e6ef40fec9c575',
 'buildtools/NARZEDZIA_OBF/main.go':'f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc',
}
# All data files other than rules.csv from 1.0.44. The tree is independently
# hashed by sorted relative paths, NUL separators and raw SHA256 digests.
UNCHANGED_TREE_SHA='5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1'

def tree_digest(root):
    base=Path(root)/'mod/data';p=hashlib.sha256();ct=0
    for f in sorted(base.rglob('*')):
        if not f.is_file() or f.relative_to(base).as_posix()=='campaign/rules.csv':continue
        p.update(f.relative_to(base).as_posix().encode('utf8')+b'\0'+hashlib.sha256(f.read_bytes()).digest())
        ct+=1
    return p.hexdigest(),ct

def reverse_bytes(blob):
    if sha(blob)!=FINAL_SHA:raise ValueError('Bad 1.0.45 rules.csv SHA')
    spans=rows_with_spans(blob);chunks=[];ids=set()
    for a,b,row in spans[1:]:
        id=row[0]
        if id not in PATCHES:continue
        if id in ids:raise ValueError('duplicate ID')
        ids.add(id);block=blob[a:b]
        for before,after in reversed(PATCHES[id]):
            x=after.replace('"','""').encode('ascii');y=before.replace('"','""').encode('ascii')
            if block.count(x)!=1:raise ValueError(('unexpected translated literal',id))
            block=block.replace(x,y,1)
        parsed=list(csv.reader(block.decode('ascii').splitlines(keepends=True)))
        if len(parsed)!=1 or len(parsed[0])!=7 or parsed[0][:4]!=row[:4] or parsed[0][5:]!=row[5:]:
            raise ValueError(('invalid reversal of text-only change',id))
        chunks.append((a,b,block))
    if ids!=PATCHES.keys():raise ValueError('reversal incomplete')
    out=bytearray();last=0
    for a,b,block in chunks:out.extend(blob[last:a]);out.extend(block);last=b
    out.extend(blob[last:]);out=bytes(out)
    if sha(out)!=PREVIOUS_SHA:raise ValueError('1.0.44 not reproduced byte-for-byte')
    return out

def check(root,previous_zip=None,prior_ledgers=()):
    root=Path(root);new=(root/'mod/data/campaign/rules.csv').read_bytes()
    old=reverse_bytes(new);result,stats,entries=patch_bytes(old)
    if result!=new or stats['rows_changed']!=44 or stats['fragments_changed']!=80 or stats['gender_references_removed']!=93:
        raise ValueError('Patch plan is not reproducible')
    info=json.loads((root/'mod/mod_info.json').read_text('utf8'))
    if info['version']!='1.0.45' or info['gameVersion']!='0.98a-RC8' or len(info['replace'])!=41:
        raise ValueError('Incorrect release metadata')
    if not (root/'mod/CZYTAJ.txt').read_text('utf8').startswith('STARSECTOR PL ASCII 1.0.45'):
        raise ValueError('Incorrect player instructions')
    if 'const edition = "1.0.45"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
        raise ValueError('Incorrect installer metadata')
    for path,expected in {API_MAP:API_SHA,**JAVA_MAINS}.items():
        file=root/path
        if file.exists() and sha(file.read_bytes())!=expected:raise ValueError(('Unauthorized Java/translation mapping delta',path))
    data=list((root/'mod/data').rglob('*'));files=[f for f in data if f.is_file()]
    if len(files)!=870 or not new.isascii():raise ValueError('Data set changed')
    tree,ct=tree_digest(root)
    if ct!=869 or tree!=UNCHANGED_TREE_SHA:raise ValueError(('Unapproved original data modification',ct,tree))
    if previous_zip:
        with zipfile.ZipFile(previous_zip) as z:
            names=[n for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')]
            if len(names)!=870:raise ValueError('Wrong baseline ZIP')
            byrel={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in names}
        for f in files:
            rel=f.relative_to(root/'mod').as_posix()
            if rel not in byrel:raise ValueError(('Missing baseline file',rel))
            if rel=='data/campaign/rules.csv':
                if byrel[rel]!=old:raise ValueError('Wrong baseline rules.csv')
            elif byrel[rel]!=f.read_bytes():raise ValueError(('Changed non-target data',rel))
    allids={fields[0] for _,_,fields in rows_with_spans(new)[1:] if fields[0] in PATCHES}
    if len(allids)!=44:raise ValueError('Lost review IDs')
    for path in prior_ledgers:
        ledger=json.loads(Path(path).read_text('utf8'))
        approved=ledger.get('reviewed',ledger.get('approved'))
        if not isinstance(approved,list):raise ValueError(('Malformed previous ledger',path))
        ids={entry['id'] for entry in approved}
        if ids&allids:raise ValueError(('Double-counted an old review',path,sorted(ids&allids)))
    return {**stats,'data_files':870,'unchanged_data_files':869,'data_tree_sha256':tree,
            'prior_rules_sha256_restored':sha(old),'remaining_java_getters_for_review':186,
            'native_windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path);p.add_argument('--prior-ledger',action='append',type=Path,default=[])
    a=p.parse_args();print(json.dumps(check(a.worktree,a.previous_zip,a.prior_ledger),indent=2))
