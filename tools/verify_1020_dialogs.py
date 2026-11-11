#!/usr/bin/env python3
"""Fail-closed audit for 1.0.20 localized dynamic dialogue, male and female.

Runs without proprietary JAR in CI. Separate JAR comparison is required for release.
"""
import csv
import json
import re
import sys
from pathlib import Path
from apply_1020 import CORRECTIONS, NEW, SHIELD, CLERK, STATUS


def getrows(path):
    with path.open(newline='',encoding='utf8') as f:
        r=csv.DictReader(f)
        assert r.fieldnames==['source_class','english_literal','polish_ascii_draft','status']
        rows=list(r)
    return {(x['source_class'],x['english_literal']):x for x in rows},len(rows)


def check(root):
    folder=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    old,n=getrows(folder/'TLUMACZENIA_JAR_1019.csv')
    new,k=getrows(folder/'TLUMACZENIA_JAR_1020.csv')
    assert n==5106 and k==5107 and len(old)==n and len(new)==k
    assert set(new)-set(old)==set(NEW)
    assert not (set(old)-set(new))
    diffs={key for key in old if old[key]!=new[key]}
    assert diffs==set(CORRECTIONS),(diffs^set(CORRECTIONS))
    for key,(src,dst) in CORRECTIONS.items():
        assert old[key]['polish_ascii_draft']==src
        assert new[key]['polish_ascii_draft']==dst
        assert new[key]['status']==STATUS
        assert re.findall(r'%[sdif]',src)==re.findall(r'%[sdif]',dst)
        assert src.count('\n')==dst.count('\n')
    for key,dst in NEW.items():
        assert new[key]['polish_ascii_draft']==dst and new[key]['status']==STATUS
    assert all(v['polish_ascii_draft'].isascii() for v in new.values())
    get=lambda key: new[(SHIELD,key)]['polish_ascii_draft']
    cases=[]
    for pron in ('on','ona'):
        cases += [
            (get('Ask the veteran spacer what ')+pron+get("'s looking at"),
             f'Zapytaj doswiadczonego kosmonaute, co {pron} obserwuje'),
            (get('Suggest that ')+pron+get(' read the manual then leave'),
             f'Zasugeruj, ze {pron} moze przeczytac instrukcje, a potem odejsc'),
            (get('The spacer explains that just ')+pron+get(' and the pilot got away in an ')+get('escape pod which was only "mostly" malfunctioning. "The miracle wasn\'t that I '),
             f'Kosmonauta wyjasnia, ze tylko {pron} i pilot zdolali uciec w kapsule ratunkowej'),
            (get('Lucky bastards, we two." It all began when ')+pron+get(' was hired on to ')+get('a salvage fleet trawling decivilized systems outside the Core Worlds. '),
             f'Wszystko zaczyna sie, kiedy {pron} dolacza do floty zlomiarzy'),
            (pron+new[(CLERK,' says.')]['polish_ascii_draft'],f'{pron} mowi.'),
        ]
    for assembled,expected in cases:
        assert expected in assembled,(expected,assembled)
        assert 'onpatrzy' not in assembled
        assert 'ona patrzy na' not in assembled
        assert '  ' not in assembled,(assembled,'double-space')
    d=json.loads((root/'mod/mod_info.json').read_text())
    assert d['version']=='1.0.20'
    api=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text()
    obf=(root/'buildtools/NARZEDZIA_OBF/main.go').read_text()
    assert 'const version = "1020"' in api
    assert '"1018", "1019", version}' in api
    assert 'const currentPatchState = "patched 10118"' in obf
    print(json.dumps({'release':'1.0.20','corrected_literals':len(CORRECTIONS),
       'new_literals':len(NEW),'gendered_sentence_cases':len(cases),
       'api_map_rows':k,'OBF':'unchanged since 1.0.18','pass':True},indent=2))

if __name__=='__main__':
    assert len(sys.argv)==2
    check(Path(sys.argv[1]))