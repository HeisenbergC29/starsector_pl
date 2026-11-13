#!/usr/bin/env python3
"""Starsector PL 1.0.47: number-neutral colony industry unit tooltips.

14 exact, class-scoped API translations in 12 JVM classes. Does not modify
Java instructions, identifiers, data files, source English or review statuses.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

BASE='TLUMACZENIA_JAR_1046.csv'
NEW='TLUMACZENIA_JAR_1047.csv'
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
BASE_SHA='8c09fa12c41199e92008551cf89e86a30e59329531ad6ba40731c9d697a73a93'
PREFIX='com.fs.starfarer.api.impl.campaign.econ.impl.'
BASE_INDUSTRY=PREFIX+'BaseIndustry'
FULL_SENTENCE='Reduces upkeep cost by %s. Reduces demand by %s unit. '
CHANGES={}

def add(cls,en,old):
    if not cls.startswith(PREFIX) or en.count('%s')!=old.count('%s') or old.count('%s jednostke.')!=1:
        raise ValueError(('Bad reviewed source mapping',cls,en))
    new=old.replace('%s jednostke.','%s jedn.')
    assert new.count('jedn..')==0 and new.isascii() and new.endswith(' ')==old.endswith(' ')
    if (cls,en) in CHANGES:raise ValueError('Duplicate source row')
    CHANGES[(cls,en)]=(old,new)

add(BASE_INDUSTRY,'Increases production by %s unit.','Zwieksza produkcje o %s jednostke.')
add(BASE_INDUSTRY,'Reduces demand by %s unit.','Zmniejsza zapotrzebowanie o %s jednostke.')
add(BASE_INDUSTRY,'Reduces upkeep cost by %s. Reduces demand by %s unit.',
    'Zmniejsza koszt utrzymania o %s. Zmniejsza zapotrzebowanie o %s jednostke.')
add(BASE_INDUSTRY,FULL_SENTENCE,
    'Zmniejsza koszty utrzymania o %s i zapotrzebowanie o %s jednostke. ')
add(PREFIX+'ItemEffectsRepo$1$2','production by %s unit.','produkcje o %s jednostke.')
for industry in ('Cryorevival','GroundDefenses','MilitaryBase','OrbitalStation','PlanetaryShield',
                 'Spaceport','TechMining','TradeCenter','Waystation'):
    add(PREFIX+industry,FULL_SENTENCE,
        'Zmniejsza koszty utrzymania o %s. Zmniejsza zapotrzebowanie o %s jednostke. ')
assert len(CHANGES)==14 and len({k[0] for k in CHANGES})==11

sha=lambda b:hashlib.sha256(b).hexdigest()
def once(s,a,b):
    if s.count(a)!=1:raise ValueError(('Expected once',a,s.count(a)))
    return s.replace(a,b)

def readmap(path):
    with Path(path).open(encoding='utf8',newline='') as f:
        r=csv.DictReader(f)
        if r.fieldnames!=FIELDS:raise ValueError('Invalid map column layout')
        return list(r)

def validated_changes(rows):
    hit=set();result=[]
    for r in rows:
        key=r['source_class'],r['english_literal']
        if key not in CHANGES:continue
        if key in hit:raise ValueError(('Duplicate mapping key',key))
        hit.add(key)
        old,new=CHANGES[key]
        if r['polish_ascii_draft']!=old:raise ValueError(('Unexpected original Polish value',key))
        for token in ('%s','%d','%f','%%','\n'):
            if r['english_literal'].count(token)!=old.count(token) or old.count(token)!=new.count(token):
                raise ValueError(('Placeholder mismatch',key,token))
        if old.startswith(' ')!=new.startswith(' ') or old.endswith(' ')!=new.endswith(' '):
            raise ValueError(('Whitespace boundary change',key))
        if new.count('jedn..'):raise ValueError(('Doubled period',key))
        result.append({'source_class':key[0],'english_sha256':sha(key[1].encode()),
                       'old_polish_sha256':sha(old.encode()),'new_polish_sha256':sha(new.encode()),
                       'source_status':r['status']})
    if hit!=CHANGES.keys():raise ValueError(('Missing mapped keys',len(hit),len(CHANGES)))
    return result

def write_map(root):
    td=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    old=td/BASE;new=td/NEW
    if new.exists():raise FileExistsError(new)
    if sha(old.read_bytes())!=BASE_SHA:raise ValueError('Wrong 1.0.46 baseline map SHA')
    rows=readmap(old)
    if len(rows)!=5260:raise ValueError('Incorrect baseline row count')
    evidence=validated_changes(rows)
    for row in rows:
        k=row['source_class'],row['english_literal']
        if k in CHANGES:row['polish_ascii_draft']=CHANGES[k][1]
    with new.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
    if len(readmap(new))!=5260:raise ValueError('New map length wrong')
    return evidence,sha(new.read_bytes())

def apply(root):
    root=Path(root)
    review,new_hash=write_map(root)
    go=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go'
    s=go.read_text(encoding='utf8')
    for a,b in (
       ('const version = "1046"','const version = "1047"'),
       ('const exeVersion = "1.0.46"','const exeVersion = "1.0.47"'),
       ('"1038", "1040", "1041", "1042", version}','"1038", "1040", "1041", "1042", "1046", version}'),
       ('PL ASCII patch up to 1.0.46','PL ASCII patch up to 1.0.47'),
    ):s=once(s,a,b)
    go.write_text(s,encoding='utf8')
    ins=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
    ins.write_text(once(ins.read_text(encoding='utf8'),'const edition = "1.0.46"','const edition = "1.0.47"'),encoding='utf8')
    path=root/'mod/mod_info.json';meta=json.loads(path.read_text(encoding='utf8'))
    if meta['version']!='1.0.46' or meta['gameVersion']!='0.98a-RC8':raise ValueError('Wrong mod metadata')
    meta['version']='1.0.47';meta['description']=once(meta['description'],'1.0.46','1.0.47')
    path.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    path=root/'mod/CZYTAJ.txt';v=path.read_text(encoding='utf8')
    v=once(v,'STARSECTOR PL ASCII 1.0.46','STARSECTOR PL ASCII 1.0.47')
    v+='\nPoprawiono 14 tekstow produkcji i zapotrzebowania w interfejsie kolonii; jednostki wyswietlaja sie poprawnie niezaleznie od liczby (jedn.). Oryginalne zasoby gry pozostaja nietkniete.\n'
    path.write_text(v,encoding='utf8')
    return {'version':'1.0.47','corrected_api_rows':len(review),'changed_class_count':len(set(k[0] for k in CHANGES)),
            'api_map_rows':5260,'new_api_map_sha256':new_hash,'data_file_changes':0,'review':review}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--report',type=Path)
    a=p.parse_args();result=apply(a.worktree)
    if a.report:a.report.write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='review'},indent=2))
