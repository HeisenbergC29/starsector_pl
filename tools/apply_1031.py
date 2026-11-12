#!/usr/bin/env python3
"""Reproducible data-only Starsector PL 1.0.31 overlay after apply_1030.

The API/OBF 1.0.30 JAR translations and SHA-256 values DO NOT change.
New combined installer edition simply identifies the updated mod resources.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

SOURCE='data/hullmods/SurveyingEquipment.java'
BEFORE=b'jednostek zaopatrzenia i %s jednostek ciezkiego sprzetu.'
AFTER=b'jedn. zaopatrzenia i %s jedn. ciezkich maszyn.'
OLD_SHA='ab222125daf0304b91e5d1f9bfd1a61f386635225197147e6af1c074132bf407'
NEW_SHA='3e2439b5e21fb40cf9b5daef6ad12eb3c07af0ee9ff73b23a016c5718b8de385'

def sha(data):return hashlib.sha256(data).hexdigest()

def translate_text(source):
    if sha(source)!=OLD_SHA:raise ValueError('Unexpected previous hullmod source SHA256')
    if source.count(BEFORE)!=1:raise ValueError('Missing unique UI literal')
    if not BEFORE.isascii() or not AFTER.isascii() or BEFORE.count(b'%s')!=AFTER.count(b'%s'):
        raise ValueError('Bad UI template')
    updated=source.replace(BEFORE,AFTER,1)
    if sha(updated)!=NEW_SHA:raise AssertionError('Unapproved content change')
    if (updated.count(b'\r\n'),updated.count(b'\n'))!=(source.count(b'\r\n'),source.count(b'\n')):
        raise AssertionError('CRLF changed')
    return updated

def exact(text,old,new):
    if text.count(old)!=1:raise ValueError(f'Expected exactly one anchor: {old!r}, got {text.count(old)}')
    return text.replace(old,new,1)

def apply(root:Path):
    mod=root/'mod';p=mod/SOURCE
    data=p.read_bytes();p.write_bytes(translate_text(data))
    meta=mod/'mod_info.json';info=json.loads(meta.read_text(encoding='utf8'))
    if info['version']!='1.0.30':raise ValueError('Wrong previous mod version')
    info['version']='1.0.31';info['description']=exact(info['description'],'1.0.30','1.0.31')
    assert len(info['replace'])==41 and SOURCE not in info['replace']
    meta.write_text(json.dumps(info,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
    readme=mod/'CZYTAJ.txt';text=readme.read_text(encoding='utf8')
    text=exact(text,'STARSECTOR PL ASCII 1.0.30','STARSECTOR PL ASCII 1.0.31')
    text+='\nPoprawiono odmiane nazw zasobow w opisie sprzetu pomiarowego floty; rowniez dla jednej jednostki. Patchery JAR pozostaly na zgodnej mapie 1.0.30.\n'
    readme.write_text(text,encoding='utf8')
    installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
    installer.write_text(exact(installer.read_text(encoding='utf8'),'const edition = "1.0.30"','const edition = "1.0.31"'),encoding='utf8')
    print(json.dumps({'release':'1.0.31','changed_data_files':1,'total_data_files':870,'java_source_sha256':NEW_SHA,'changed_jar_maps':0,'jar_patchers_remain':'1.0.30'},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);apply(p.parse_args().worktree)
