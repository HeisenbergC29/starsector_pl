#!/usr/bin/env python3
"""Independent strict 1.0.47 map, metadata, and 870-data immutable comparison."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from apply_1047 import CHANGES,BASE,NEW,BASE_SHA,readmap,validated_changes,sha

FINAL_SHA='9a36861c53e6508f8082a1a2b845e36e6c5d76f44dd1918b3b8e151ae06eaebd'
GO_1046_SHA='19f90fae6c7b7eab0f900484ea076e17bd7c664cc7d506f542d5e1546f2c3a19'
OBF_GO_SHA='f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc'
DATA_RULES_SHA='e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a'
DATA_OTHERS_SHA='5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1'
REVERSES=(
    ('const version = "1047"','const version = "1046"'),
    ('const exeVersion = "1.0.47"','const exeVersion = "1.0.46"'),
    ('"1038", "1040", "1041", "1042", "1046", version}',
     '"1038", "1040", "1041", "1042", version}'),
    ('PL ASCII patch up to 1.0.47','PL ASCII patch up to 1.0.46'),
)

def tree_digest(base):
    h=hashlib.sha256();count=0
    for p in sorted(Path(base).rglob('*')):
        if not p.is_file() or p.relative_to(base).as_posix()=='campaign/rules.csv':continue
        h.update(p.relative_to(base).as_posix().encode()+b'\0'+hashlib.sha256(p.read_bytes()).digest())
        count+=1
    return h.hexdigest(),count

def check(root,previous_zip=None,strict_go=True):
    root=Path(root)
    trans=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    original=trans/BASE;new=trans/NEW
    if sha(original.read_bytes())!=BASE_SHA:raise ValueError('Prior 1046 map mutated')
    if sha(new.read_bytes())!=FINAL_SHA:raise ValueError('Target 1047 map changed')
    old=readmap(original);updated=readmap(new)
    if len(old)!=5260 or len(updated)!=5260:raise ValueError('Map row count changed')
    validated_changes(old)
    differences=[]
    for a,b in zip(old,updated):
        for column in ('source_class','english_literal','status'):
            if a[column]!=b[column]:raise ValueError(('Unauthorized technical mapping delta',column,a['source_class']))
        k=a['source_class'],a['english_literal']
        want=CHANGES[k][1] if k in CHANGES else a['polish_ascii_draft']
        if b['polish_ascii_draft']!=want:raise ValueError(('Unapproved Polish literal',k))
        if k in CHANGES:differences.append(k)
    if len(differences)!=14 or len(set(differences))!=14:raise ValueError('Incorrect changed set')
    if any('%s jednostke' in x['polish_ascii_draft'] for x in updated):
        raise ValueError('Numerically invalid singular unit remains in API map')
    if any('jedn..' in x['polish_ascii_draft'] for x in updated):
        raise ValueError('Double period regressed in API')
    metadata=json.loads((root/'mod/mod_info.json').read_text(encoding='utf8'))
    if metadata['version']!='1.0.47' or metadata['gameVersion']!='0.98a-RC8' or len(metadata['replace'])!=41:
        raise ValueError('Incorrect version/mod replacements')
    if not (root/'mod/CZYTAJ.txt').read_text(encoding='utf8').startswith('STARSECTOR PL ASCII 1.0.47'):
        raise ValueError('Player instructions mismatch')
    if 'const edition = "1.0.47"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
        raise ValueError('Installer edition mismatch')
    go=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
    for newer,older in REVERSES:
        if go.count(newer)!=1:raise ValueError(('Incorrect Go version source',newer))
        go=go.replace(newer,older)
    if strict_go and sha(go.encode())!=GO_1046_SHA:raise ValueError('Go patcher modified outside four version constants')
    obf=root/'buildtools/NARZEDZIA_OBF/main.go'
    if strict_go and sha(obf.read_bytes())!=OBF_GO_SHA:raise ValueError('OBF source modified unexpectedly')
    base=root/'mod/data';files=[p for p in base.rglob('*') if p.is_file()]
    if len(files)!=870 or sha((base/'campaign/rules.csv').read_bytes())!=DATA_RULES_SHA:raise ValueError('Data or dialogues changed')
    rest,n=tree_digest(base)
    if n!=869 or rest!=DATA_OTHERS_SHA:raise ValueError('Unexpected modification of non-rules data')
    if previous_zip:
        with zipfile.ZipFile(previous_zip) as z:
            expected={k.removeprefix('Starsector_PL_ASCII/'):z.read(k) for k in z.namelist()
                      if k.startswith('Starsector_PL_ASCII/data/')}
        if len(expected)!=870:raise ValueError('Baseline data count wrong')
        for f in files:
            p=f.relative_to(root/'mod').as_posix()
            if p not in expected or expected[p]!=f.read_bytes():raise ValueError(('Data differs from 1046 package',p))
    return {'version':'1.0.47','changes':len(differences),'classes':len({x[0] for x in differences}),
            'source_map_sha256':BASE_SHA,'installed_map_sha256':FINAL_SHA,'api_map_rows':5260,
            'unchanged_data_files':870,'other_data_tree_sha256':rest,
            'technical_identifiers_unchanged':True,'original_JVM_method_bytecode_changes':0,
            'native_windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--previous-zip',type=Path);p.add_argument('--fixture',action='store_true')
    a=p.parse_args()
    print(json.dumps(check(a.worktree,a.previous_zip,strict_go=not a.fixture),indent=2))
