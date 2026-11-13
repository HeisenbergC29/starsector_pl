#!/usr/bin/env python3
"""Independent byte-exact validation of 29 mapped API translations for 1.0.48."""
from __future__ import annotations
import argparse,json,zipfile
from pathlib import Path
from apply_1048 import OLD,NEW,OLD_SHA,EXPECTED,EXPECTED_CLASSES,readmap,plan,sha
from verify_1047 import tree_digest,DATA_RULES_SHA,DATA_OTHERS_SHA,OBF_GO_SHA

NEW_SHA='2f85b133be0d3087321d16dd71080f5214cf9e2932cc60381ecbab521b273289'
GO_1047_SHA='377c698fd76fd3086d21e47fd8192c9c381dcf8d56d0e24c9345a0cd043165cc'
REVERSE_GO=[
 ('const version = "1048"','const version = "1047"'),
 ('const exeVersion = "1.0.48"','const exeVersion = "1.0.47"'),
 ('"1040", "1041", "1042", "1046", "1047", version}','"1040", "1041", "1042", "1046", version}'),
 ('PL ASCII patch up to 1.0.48','PL ASCII patch up to 1.0.47')]

def check(root,previous_zip=None):
    root=Path(root);f=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    old=f/OLD;new=f/NEW
    if sha(old.read_bytes())!=OLD_SHA or sha(new.read_bytes())!=NEW_SHA:
        raise ValueError('API source/target map SHA mismatch')
    base=readmap(old);updated=readmap(new)
    changed,inventory,reviewsha=plan(base)
    if len(base)!=5260 or len(updated)!=5260:raise ValueError('Mapping size changed')
    count=0
    for a,b in zip(base,updated):
        if any(a[k]!=b[k] for k in ('source_class','english_literal','status')):
            raise ValueError('Technical source fields/status modified')
        k=a['source_class'],a['english_literal'];want=changed[k][1] if k in changed else a['polish_ascii_draft']
        if b['polish_ascii_draft']!=want:raise ValueError(('Nonreviewed translation changed',k))
        count+=k in changed
    if count!=EXPECTED or len({k[0] for k in changed})!=EXPECTED_CLASSES:
        raise ValueError('Reviewed inventory changed')
    meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
    if meta['version']!='1.0.48' or meta['gameVersion']!='0.98a-RC8' or len(meta['replace'])!=41:
        raise ValueError('Unexpected mod metadata')
    if not (root/'mod/CZYTAJ.txt').read_text('utf8').startswith('STARSECTOR PL ASCII 1.0.48'):
        raise ValueError('User installation instructions not updated')
    if 'const edition = "1.0.48"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
        raise ValueError('Installer edition not updated')
    go=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
    for newer,older in REVERSE_GO:
        if go.count(newer)!=1:raise ValueError(('Unexpected Go version field',newer))
        go=go.replace(newer,older)
    if GO_1047_SHA and sha(go.encode('utf8'))!=GO_1047_SHA:
        raise ValueError('Go API patcher changed beyond release constants')
    obf=root/'buildtools/NARZEDZIA_OBF/main.go'
    if obf.exists() and sha(obf.read_bytes())!=OBF_GO_SHA:
        raise ValueError('OBF patcher changed')
    dat=root/'mod/data';files=[p for p in dat.rglob('*') if p.is_file()]
    if len(files)!=870 or sha((dat/'campaign/rules.csv').read_bytes())!=DATA_RULES_SHA:
        raise ValueError('Dialogue data changed')
    rest,n=tree_digest(dat)
    if n!=869 or rest!=DATA_OTHERS_SHA:raise ValueError('Other 869 data files changed')
    if previous_zip:
        with zipfile.ZipFile(previous_zip) as z:
            expected={name.removeprefix('Starsector_PL_ASCII/'):z.read(name) for name in z.namelist()
                      if name.startswith('Starsector_PL_ASCII/data/')}
        if len(expected)!=870:raise ValueError('Wrong previous distribution size')
        for x in files:
            rel=x.relative_to(root/'mod').as_posix()
            if expected.get(rel)!=x.read_bytes():raise ValueError(('Data differs from 1.0.47',rel))
    return {'version':'1.0.48','corrected_api_rows':count,'modified_classes':EXPECTED_CLASSES,'map_rows':5260,
            'old_api_map_sha256':OLD_SHA,'new_api_map_sha256':NEW_SHA,
            'review_inventory_sha256':reviewsha,'unchanged_data_files':870,
            'unchanged_non_dialogue_data_sha256':rest,'source_identifiers_unchanged':True,
            'original_java_bytecode_changed':False,'native_windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
    a=p.parse_args();print(json.dumps(check(a.worktree,a.previous_zip),indent=2))
