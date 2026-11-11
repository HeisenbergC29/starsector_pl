#!/usr/bin/env python3
"""Starsector PL 1.0.22: unify player-visible names of the Persean League.

Base: precisely verified 1.0.21 worktree. This overlay changes three data files
and release metadata, no game scripts, CSV IDs, JAR mappings or class bytecode.
Keep historical 1.0.21 JAR maps: the 1.0.22 patch is data-only.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import re
from pathlib import Path

BASELINE_SHA = {
    'mod/data/campaign/rules.csv': 'd5fb809d771d99c23b42234de217ff3d89bb4491969841ff35a464512e198c30',
    'mod/data/strings/descriptions.csv': '6870f48caf15c71891fead1dbb49f1daab83404cf4dc226978167034bea12e41',
    'mod/data/missions/coralnebula/mission_text.txt': 'a13b3df4e915de8bf060fadef68740349eab40c5e28d7d62f8d0589e4b0c35ae',
    'mod/mod_info.json': '86d59ee00651d48183059a59cda5c4fa14411c7aad52a4974380d5cd3d090661',
    'mod/CZYTAJ.txt': 'd26b0f0a0c40087754b7c7297df4c8ff3a808769870e739ed14acd5d6b7ab343',
    'buildtools/NARZEDZIA_INSTALATOR/main.go': '6fb604c0b6284a4d9a739f398bcec3d5ad5d9dd3108b745c177b8f382f66e549',
}
# Important: word boundaries prevent the short source 'Persea' matching the
# ALREADY CORRECT inflected adjective 'Perseanskiej'.
NAME_RE = re.compile(rb'\b(Liga|Ligi|Lige) (Perseusza|Persea)\b')
NAMES = {b'Liga':b'Liga Perseanska', b'Ligi':b'Ligi Perseanskiej', b'Lige':b'Lige Perseanska'}
EXPECT = {
 'mod/data/campaign/rules.csv': 59,
 'mod/data/strings/descriptions.csv': 4,
 'mod/data/missions/coralnebula/mission_text.txt': 2,
}
TOKEN_RE=re.compile(rb'\$[A-Za-z][A-Za-z_0-9]*(?:\.[A-Za-z_0-9]+)*|\{[A-Za-z_0-9]+\}|<[A-Za-z/][A-Za-z_0-9 ="\-]*>')

def checksum(s): return hashlib.sha256(s).hexdigest()

def records(raw):
    return list(csv.reader(io.StringIO(raw.decode('ascii'), newline='')))

def only_text_columns(before, after, source, allowed):
    old,new=records(before),records(after)
    assert len(old)==len(new) and old[0]==new[0]
    fields=old[0]
    assert allowed<=set(fields),(source,'missing approved column')
    changes=0
    for i,(a,b) in enumerate(zip(old[1:],new[1:]),2):
        assert len(a)==len(b),(source,i,'width')
        for j,(x,y) in enumerate(zip(a,b)):
            if x!=y:
                changes+=1
                assert fields[j] in allowed,(source,i,fields[j])
                assert TOKEN_RE.findall(x.encode('ascii'))==TOKEN_RE.findall(y.encode('ascii')),(source,i,'changed dynamic token')
    assert changes>0
    return changes

def main(root):
    for name,expected in BASELINE_SHA.items():
        p=root/name
        assert p.is_file(),('missing',p)
        assert checksum(p.read_bytes())==expected,('wrong 1.0.21 input',name,checksum(p.read_bytes()))
    counts=collections.Counter()
    for name,expected in EXPECT.items():
        p=root/name; before=p.read_bytes()
        def replace(m):
            counts[m.group(0).decode('ascii')]+=1
            return NAMES[m.group(1)]
        after,n=NAME_RE.subn(replace,before)
        assert n==expected,(name,n,expected)
        assert before.count(b'\n')==after.count(b'\n')
        assert TOKEN_RE.findall(before)==TOKEN_RE.findall(after),(name,'dynamic token mismatch')
        if name.endswith('rules.csv'): only_text_columns(before,after,name,{'text'})
        if name.endswith('descriptions.csv'): only_text_columns(before,after,name,{'text1','text2','text3','text4','text5'})
        assert not NAME_RE.search(after)
        p.write_bytes(after)
    assert sum(counts.values())==65 and counts==collections.Counter({
        'Ligi Persea':11,'Ligi Perseusza':45,'Liga Persea':1,
        'Liga Perseusza':4,'Lige Perseusza':4}),counts
    mod_info=root/'mod/mod_info.json';meta=json.loads(mod_info.read_text('utf8'))
    assert meta['version']=='1.0.21'
    meta['version']='1.0.22'
    assert meta['description'].count('1.0.21')==1
    meta['description']=meta['description'].replace('1.0.21','1.0.22')
    mod_info.write_text(json.dumps(meta,indent=2,ensure_ascii=True)+'\n','utf8')
    readme=root/'mod/CZYTAJ.txt';s=readme.read_text('utf8')
    assert s.count('STARSECTOR PL ASCII 1.0.21')==1
    s=s.replace('STARSECTOR PL ASCII 1.0.21','STARSECTOR PL ASCII 1.0.22')
    s+='\nUjednolicono 65 nazw Ligi Perseanskiej w dialogach, opisach i opisie misji.\n'
    readme.write_text(s,'utf8')
    installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=installer.read_text('utf8')
    assert s.count('const edition = "1.0.21"')==1
    installer.write_text(s.replace('const edition = "1.0.21"','const edition = "1.0.22"'),'utf8')
    print('1.0.22: 65 player-visible League names normalized in 3 data files; JAR maps unchanged')
    print(json.dumps(dict(sorted(counts.items())),indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path)
    main(ap.parse_args().worktree)