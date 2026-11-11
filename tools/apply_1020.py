#!/usr/bin/env python3
"""1.0.20: repair gender-neutral assembled sentences in two campaign bar events.

The modifications affect only translated Java CONSTANT_String values; no IDs,
placeholder patterns, class files or executable bytecode are changed here.
The previous 1.0.19 state is mandatory and is retained for upgrades.
"""
import argparse
import csv
import json
from pathlib import Path

SHIELD='com.fs.starfarer.api.impl.campaign.intel.bar.events.PlanetaryShieldBarEvent'
CLERK='com.fs.starfarer.api.impl.campaign.intel.bar.events.CorruptPLClerkSuppliesBarEvent'
# Values verified in original JVM CONSTANT_String and the 1.0.19 translation map.
CORRECTIONS={
    (SHIELD,"'s looking at"): ('patrzy na', ' obserwuje'),
    (SHIELD,'Suggest that '): ('Zasugeruj, zeby ', 'Zasugeruj, ze '),
    (SHIELD,' read the manual then leave'): (' przeczytac instrukcje i odejsc', ' moze przeczytac instrukcje, a potem odejsc'),
    (SHIELD,'The spacer explains that just '): ('Kosmonauta wyjasnia, ze tuz ', 'Kosmonauta wyjasnia, ze tylko '),
    (SHIELD,' and the pilot got away in an '): (' a pilot zdolal uciec w ', ' i pilot zdolali uciec w '),
    (SHIELD,'Lucky bastards, we two." It all began when '): ('Szczesciarze z nas dwoch." Wszystko zaczelo sie, kiedy ', 'Szczesciarze z nas dwoch." Wszystko zaczyna sie, kiedy '),
    (SHIELD,' was hired on to '): (' zaciagnal sie do ', ' dolacza do '),
}
NEW={(CLERK,' says.'): ' mowi.'}
STATUS='VERIFIED_COMPOSED_GENDER_UI_1020'

def replace_once(s, old, new):
    assert s.count(old)==1,(old,s.count(old))
    return s.replace(old,new)

def main(root):
    assert (root/'mod/mod_info.json').is_file()
    target=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    src=target/'TLUMACZENIA_JAR_1019.csv';dest=target/'TLUMACZENIA_JAR_1020.csv'
    assert not dest.exists(),'1.0.20 already applied'
    with src.open(newline='',encoding='utf8') as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    assert fields==['source_class','english_literal','polish_ascii_draft','status']
    assert len(rows)==5106
    found=set()
    for row in rows:
        key=(row['source_class'],row['english_literal'])
        if key not in CORRECTIONS:continue
        old,new=CORRECTIONS[key]
        assert row['polish_ascii_draft']==old,(key,row['polish_ascii_draft'])
        assert new.isascii(),(key,new)
        row['polish_ascii_draft']=new
        row['status']=STATUS
        found.add(key)
    assert found==set(CORRECTIONS),('Missing corrections',set(CORRECTIONS)-found)
    occupied={(r['source_class'],r['english_literal']) for r in rows}
    assert not(set(NEW)&occupied)
    for (cl,en),pl in NEW.items():
        rows.append({'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
    assert len(rows)==5107
    assert len({(r['source_class'],r['english_literal']) for r in rows})==len(rows)
    assert all(r['polish_ascii_draft'].isascii() for r in rows)
    with dest.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\r\n')
        w.writeheader();w.writerows(rows)

    p=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go';s=p.read_text('utf8')
    s=replace_once(s,'const version = "1019"','const version = "1020"')
    s=replace_once(s,'const exeVersion = "1.0.19"','const exeVersion = "1.0.20"')
    s=replace_once(s,'"1017", "1018", version}', '"1017", "1018", "1019", version}')
    s=replace_once(s,'PL ASCII patch up to 1.0.19','PL ASCII patch up to 1.0.20')
    p.write_text(s,'utf8')
    p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=p.read_text('utf8')
    s=replace_once(s,'const edition = "1.0.19"','const edition = "1.0.20"')
    p.write_text(s,'utf8')
    p=root/'mod/mod_info.json';d=json.loads(p.read_text('utf8'))
    assert d['version']=='1.0.19';d['version']='1.0.20'
    d['description']=replace_once(d['description'],'1.0.19','1.0.20')
    p.write_text(json.dumps(d,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
    s=replace_once(s,'STARSECTOR PL ASCII 1.0.19','STARSECTOR PL ASCII 1.0.20')
    s+='\nPoprawiono skladanie dialogow zalezne od rodzaju gramatycznego postaci.\n'
    p.write_text(s,'utf8')
    print('1.0.20:',len(CORRECTIONS),'verified corrected UI fragments and',len(NEW),'new UI literal; OBF unchanged')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('worktree',type=Path)
    main(a.parse_args().worktree)