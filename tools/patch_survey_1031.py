#!/usr/bin/env python3
"""Create a text-only SurveyingEquipment.java override from user's own game data.

This intentionally stores no original commercial Java source in Git or release
source trees. Code is checked against an exact original SHA and two whitelisted
Java string literals; CRLF, whitespace and every other byte remain untouched.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

SOURCE_REL=Path('data/hullmods/SurveyingEquipment.java')
ORIGINAL_SHA='71bf4e0c12fb5d277345ab01de6c82f743240a374aba4ad399c287e6037a371e'
REPLACEMENTS={
 b'The combined surveying equipment in your fleet reduces the survey cost by %s ':
 b'Sprzet pomiarowy calej floty zmniejsza koszt badania planety o %s jedn. ',
 b'supplies and %s heavy machinery.':
 b'zaopatrzenia i %s jedn. ciezkich maszyn.',
}

def patch(source:bytes)->bytes:
    if hashlib.sha256(source).hexdigest()!=ORIGINAL_SHA:
        raise ValueError('Unexpected original Starsector data Java SHA-256; refusing rewrite')
    data=source
    for old,new in REPLACEMENTS.items():
        if data.count(old)!=1:raise ValueError('missing or repeated English literal in original source')
        if not new.isascii() or old.count(b'%s')!=new.count(b'%s'):
            raise AssertionError('Invalid literal markers or non ASCII target')
        data=data.replace(old,new,1)
    if data.count(b'\r\n')!=source.count(b'\r\n') or data.count(b'\n')!=source.count(b'\n'):
        raise AssertionError('Source newline convention changed')
    if hashlib.sha256(data).digest()==hashlib.sha256(source).digest():raise AssertionError('No change')
    return data

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--game-data',type=Path,required=True,help='Private original data/ parent directory')
    a.add_argument('--mod',type=Path,required=True,help='Existing mod root')
    opts=a.parse_args()
    src=opts.game_data/SOURCE_REL
    dst=opts.mod/SOURCE_REL
    before=src.read_bytes();after=patch(before)
    if dst.exists():
        if dst.read_bytes()==after:print('Idempotent: file already localized');return
        raise ValueError(f'Refusing to overwrite another file: {dst}')
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_bytes(after)
    print(json.dumps({'path':str(SOURCE_REL),'source_sha256':ORIGINAL_SHA,
                      'localized_sha256':hashlib.sha256(after).hexdigest(),'changed_literals':len(REPLACEMENTS),
                      'source_code_modified':False,'native_game_tested':False}))
if __name__=='__main__':main()
