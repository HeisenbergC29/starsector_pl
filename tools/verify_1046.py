#!/usr/bin/env python3
"""Independently check 1.0.46 exact API map and immutable 1.0.45 player data."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from apply_1046 import BASE,NEW,BASE_SHA,CHANGES,ADDITIONS,ADD_STATUS,load,plan,sha
from audit_1046_jvm import check as check_jvm

FINAL_MAP_SHA='8c09fa12c41199e92008551cf89e86a30e59329531ad6ba40731c9d697a73a93'
DATA_RULES_SHA='e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a'
DATA_OTHERS_TREE_SHA='5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1'
GO_1042_SHA='b40409dd3731093de7c77f765536ffa3382ddaa7a051825ac2e6ef40fec9c575'
OBF_MAIN_SHA='f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc'

REVERSES=[('const version = "1046"','const version = "1042"'),
 ('const exeVersion = "1.0.46"','const exeVersion = "1.0.42"'),
 ('"1038", "1040", "1041", "1042", version}', '"1038", "1040", "1041", version}'),
 ('PL ASCII patch up to 1.0.46','PL ASCII patch up to 1.0.42')]

def tree_digest(base):
    h=hashlib.sha256();num=0
    for p in sorted(base.rglob('*')):
        if not p.is_file() or p.relative_to(base).as_posix()=='campaign/rules.csv':continue
        h.update(p.relative_to(base).as_posix().encode()+b'\0'+hashlib.sha256(p.read_bytes()).digest());num+=1
    return h.hexdigest(),num

def check(root,previous_zip=None,original_api=None,strict_go=True):
    root=Path(root)
    directory=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    old_file=directory/BASE;new_file=directory/NEW
    if sha(old_file.read_bytes())!=BASE_SHA:raise ValueError('Old API map changed')
    if sha(new_file.read_bytes())!=FINAL_MAP_SHA:raise ValueError('Unexpected new API map SHA')
    old=load(old_file);new=load(new_file)
    if len(old)!=5257 or len(new)!=5260:raise ValueError('Map count drift')
    head=new[:5257];tail=new[5257:]
    expected_tail=[dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=ADD_STATUS) for (cl,en),pl in ADDITIONS.items()]
    if tail!=expected_tail:raise ValueError('Missing or invalid three dynamic tooltip fragments')
    delta=plan(old);nchanges=0;classes=set();statuses={}
    for a,b in zip(old,head):
        for col in ('source_class','english_literal','status'):
            if a[col]!=b[col]:raise ValueError(('Non-text mapping field changed',col,a['source_class']))
        key=a['source_class'],a['english_literal']
        want=CHANGES[key][1] if key in CHANGES else a['polish_ascii_draft']
        if b['polish_ascii_draft']!=want:raise ValueError(('Unexpected translation',key))
        if key in CHANGES:
            classes.add(key[0]);nchanges+=1;statuses[a['status']]=statuses.get(a['status'],0)+1
    if nchanges!=13 or len(delta)!=13 or len(classes)!=8:raise ValueError('Wrong delta counts')
    if set((r['source_class'],r['english_literal']) for r in head)&set(ADDITIONS):
        raise ValueError('Already mapped new keys in previous map')
    metadata=json.loads((root/'mod/mod_info.json').read_text(encoding='utf8'))
    if metadata['version']!='1.0.46' or metadata['gameVersion']!='0.98a-RC8' or len(metadata['replace'])!=41:
        raise ValueError('Wrong mod metadata')
    if not (root/'mod/CZYTAJ.txt').read_text(encoding='utf8').startswith('STARSECTOR PL ASCII 1.0.46'):
        raise ValueError('Wrong player instructions')
    main=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text(encoding='utf8')
    for translated,original in REVERSES:
        if main.count(translated)!=1:raise ValueError(('Unexpected Go source version',translated))
        main=main.replace(translated,original)
    if strict_go and sha(main.encode())!=GO_1042_SHA:raise ValueError('API patcher Go source changed beyond four approved strings')
    if 'const edition = "1.0.46"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text(encoding='utf8'):
        raise ValueError('Installer not updated')
    obf=root/'buildtools/NARZEDZIA_OBF/main.go'
    if strict_go and sha(obf.read_bytes())!=OBF_MAIN_SHA:raise ValueError('OBF patcher modified')
    data=root/'mod/data';files=[p for p in data.rglob('*') if p.is_file()]
    if len(files)!=870:raise ValueError('Player data count changed')
    if sha((data/'campaign/rules.csv').read_bytes())!=DATA_RULES_SHA:raise ValueError('Rules 1.0.45 not preserved')
    others,count=tree_digest(data)
    if count!=869 or others!=DATA_OTHERS_TREE_SHA:raise ValueError('Other data files changed')
    if previous_zip:
        with zipfile.ZipFile(previous_zip) as z:
            prefix='Starsector_PL_ASCII/'
            expected={n[len(prefix):]:z.read(n) for n in z.namelist() if n.startswith(prefix+'data/')}
        if set(expected)!={p.relative_to(root/'mod').as_posix() for p in files}:
            raise ValueError('Data file paths changed')
        for p in files:
            if expected[p.relative_to(root/'mod').as_posix()]!=p.read_bytes():raise ValueError(('Changed data bytes',p))
    if original_api:
        proof=check_jvm(original_api)
        if proof['checked_class_scoped_literals']!=16:raise ValueError('Not enough original JVM constants')
    return {'version':'1.0.46','corrected_api_map_rows':nchanges,'new_api_map_rows':len(ADDITIONS),
            'changed_java_classes':len(classes),
            'api_map_rows':len(new),'new_api_map_sha256':FINAL_MAP_SHA,'unchanged_game_data_files':870,
            'all_source_identifiers_and_statuses_preserved':True,'original_java_literals_verified':bool(original_api),
            'native_windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--previous-zip',type=Path);p.add_argument('--original-api',type=Path)
    p.add_argument('--fixture',action='store_true',help='Skip strict Go source comparison for local stripped-source fixture')
    a=p.parse_args()
    print(json.dumps(check(a.worktree,a.previous_zip,a.original_api,strict_go=not a.fixture),indent=2))
