#!/usr/bin/env python3
"""Starsector PL 1.0.46: class-scoped API UI corrections.

Preserves English keys, review-status labels, and the executable method bytecode.
Reconstructs a separate map from exact 1.0.42 baseline. All data files stay
byte-identical to 1.0.45. The patcher itself performs JVM literal rewrites.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

BASE='TLUMACZENIA_JAR_1042.csv'
NEW='TLUMACZENIA_JAR_1046.csv'
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
BASE_SHA='abaa3521fb8906e9686603ea38252cde5e4b00745761ccb11a7588a410bbb9e9'
PREFIX='com.fs.starfarer.api.'
# Precisely audited English keys, original Polish texts and their final grammar-safe values.
CHANGES={}
def edit(cls,english,old,new):
    if not cls.startswith(PREFIX) or not old or not new or not old.isascii() or not new.isascii() or old==new:
        raise ValueError('Invalid planned change')
    key=(cls,english)
    if key in CHANGES:raise ValueError('Duplicate source key')
    CHANGES[key]=(old,new)

PI=PREFIX+'impl.campaign.intel.events.PiracyRespiteScript'
edit(PI,'    - Colonies receive %s accessibility',
     '    - Kolonie otrzymuja %s dostepnosci','    - Premia do dostepnosci kolonii: %s')
edit(PI,'    - Lasts for %s days',
     '    - Pozostalo %s dni','    - Czas trwania (dni): %s')
INT=PREFIX+'impl.campaign.abilities.InterdictionPulseAbility'
edit(INT,"The disruption lasts for %s seconds, modified by %s second for every %s points of difference in the fleets' sensor strengths.",
     'Zaklocenie trwa %s sekund. Czas ten zmienia sie o %s sekunde za kazde %s pkt roznicy miedzy sila czujnikow flot.',
     'Zaklocenie trwa %s s. Czas ten zmienia sie o %s s na kazde %s pkt roznicy sily czujnikow flot.')
MIS=PREFIX+'impl.hullmods.MissileAutoloader'
edit(MIS,'After a reload, the weapon requires an extra %s seconds, in addition to its normal cooldown, before it can fire again.',
     'Po przeladowaniu bron potrzebuje dodatkowych %s sekund ponad zwykly czas odnowienia, zanim bedzie mogla ponownie wystrzelic.',
     'Po przeladowaniu bron wymaga dodatkowo %s s ponad zwykly czas odnowienia, zanim bedzie mogla ponownie wystrzelic.')
edit(MIS,' CAPACITY REMAINING',' POZOSTALA POJEMNOSC',' POZOSTALY ZAPAS')
edit(PREFIX+'impl.campaign.skills.CrewTraining$Level2','+%s seconds peak operating time for combat ships (maximum: %s)',
     '+%s sekund szczytowego czasu dzialania okretow bojowych (maksymalnie: %s)',
     '+%s s szczytowego czasu dzialania okretow bojowych (maksymalnie: %s)')
edit(PREFIX+'impl.campaign.skills.PhaseCorps$Level3','+%s seconds peak operating time for combat phase ships (maximum: %s)',
     '+%s sekund szczytowego czasu dzialania fazowych okretow bojowych (maksymalnie: %s)',
     '+%s s szczytowego czasu dzialania fazowych okretow bojowych (maksymalnie: %s)')
edit(PREFIX+'impl.campaign.tutorial.GalatianAcademyStipend','You should continue receiving the stipend for another %s months.',
     'Bedziesz otrzymywac stypendium jeszcze przez %s miesiecy.',
     'Stypendium bedzie wyplacane jeszcze przez %s mies.')
AB=PREFIX+'impl.campaign.AbandonMarketPluginImpl'
edit(AB,'Can only abandon colonies of size %s or smaller.',
     'Mozna opuszczac jedynie kolonie o wielkosci %s lub mniejszej.',
     'Porzucic mozna tylko kolonie o wielkosci %s lub mniejszej.')
edit(AB,'You have %s credits.','Masz %s kredytow.','Stan kredytow: %s.')
edit(AB,'Abandoning %s, a size %s colony, requires %s in evacuation expenses. Shutting down all operations will generate %s credits, for a net ',
     'Porzucenie kolonii %s o wielkosci %s wymaga wydatkow ewakuacyjnych w wysokosci %s. Zamkniecie wszystkich zakladow przyniesie %s kredytow, co daje bilans ',
     'Koszt ewakuacji kolonii %s (wielkosc: %s): %s. Przychod z zamkniecia zakladow: %s. Bilans: ')
AFF=PREFIX+'impl.campaign.rulecmd.DoCanAffordCheck$1'
edit(AFF,'You have %s credits available.','Masz do dyspozycji %s kredytow.','Dostepne kredyty: %s.')
edit(AFF,'You only have %s credits available.','Masz do dyspozycji tylko %s kredytow.','Dostepne kredyty: tylko %s.')
# Three original JVM literals, previously not present in the mapping. They form
# the same abandonment tooltip using StringBuilder: prefix + cost/payout + suffix.
ADDITIONS={
    (AB,'cost'): 'koszt',
    (AB,'payout'): 'zysk',
    (AB,' of %s.'): ' %s.',
}
ADD_STATUS='VERIFIED_COMPOSED_ABANDON_TOOLTIP_1046'
assert len(CHANGES)==13 and len(ADDITIONS)==3

def sha(data):return hashlib.sha256(data).hexdigest()
def once(s,a,b):
    if s.count(a)!=1:raise ValueError(('Expected literal exactly once',a,s.count(a)))
    return s.replace(a,b)
def load(path):
    with path.open(encoding='utf8',newline='') as f:
        d=csv.DictReader(f)
        if d.fieldnames!=FIELDS:raise ValueError('Unexpected API map schema')
        return list(d)
def plan(rows):
    seen=set();deltas=[]
    for x in rows:
        key=x['source_class'],x['english_literal']
        if key not in CHANGES:continue
        if key in seen:raise ValueError(('duplicate key',key))
        seen.add(key)
        old,new=CHANGES[key]
        if x['polish_ascii_draft']!=old:raise ValueError(('Unexpected old Polish text',key))
        en=x['english_literal']
        if en.count('%s')!=old.count('%s') or old.count('%s')!=new.count('%s'):
            raise ValueError(('Placeholder mismatch',key))
        for token in ('%d','%f','%%'):
            if en.count(token)!=old.count(token) or old.count(token)!=new.count(token):
                raise ValueError(('Token mismatch',key,token))
        if old.startswith(' ')!=new.startswith(' ') or old.endswith(' ')!=new.endswith(' ') or old.count('\n')!=new.count('\n'):
            raise ValueError(('String boundary mismatch',key))
        deltas.append((key[0],key[1],old,new,x['status']))
    if seen!=CHANGES.keys():raise ValueError(('Missing target keys',set(CHANGES)-seen))
    return deltas

def write_map(root):
    td=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    src=td/BASE;dst=td/NEW
    if dst.exists():raise FileExistsError(dst)
    if sha(src.read_bytes())!=BASE_SHA:raise ValueError('API map 1.0.42 SHA mismatch')
    rows=load(src)
    if len(rows)!=5257:raise ValueError(('Unexpected map count',len(rows)))
    changes=plan(rows)
    current_keys={(r['source_class'],r['english_literal']) for r in rows}
    if current_keys & ADDITIONS.keys():raise ValueError('Already mapped new abandonment fragments')
    for key,newpolish in ADDITIONS.items():
        if key[1].count('%s')!=newpolish.count('%s') or not newpolish.isascii():
            raise ValueError('Invalid new compound fragment')
    for row in rows:
        key=row['source_class'],row['english_literal']
        if key in CHANGES:row['polish_ascii_draft']=CHANGES[key][1]
    for (cls,english),polish in ADDITIONS.items():
        rows.append(dict(source_class=cls,english_literal=english,polish_ascii_draft=polish,status=ADD_STATUS))
    with dst.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n')
        w.writeheader();w.writerows(rows)
    if len(load(dst))!=5260:raise ValueError('Map row loss')
    return changes,sha(dst.read_bytes())

def apply(root):
    root=Path(root)
    changes,mapping_sha=write_map(root)
    go=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go'
    s=go.read_text('utf8')
    for a,b in [
        ('const version = "1042"','const version = "1046"'),
        ('const exeVersion = "1.0.42"','const exeVersion = "1.0.46"'),
        ('"1038", "1040", "1041", version}', '"1038", "1040", "1041", "1042", version}'),
        ('PL ASCII patch up to 1.0.42','PL ASCII patch up to 1.0.46'),
    ]: s=once(s,a,b)
    go.write_text(s,'utf8')
    ins=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
    ins.write_text(once(ins.read_text('utf8'),'const edition = "1.0.45"','const edition = "1.0.46"'),'utf8')
    meta=root/'mod/mod_info.json'
    m=json.loads(meta.read_text('utf8'))
    if m['version']!='1.0.45':raise ValueError('Unexpected previous mod version')
    m['version']='1.0.46'
    m['description']=once(m['description'],'1.0.45','1.0.46')
    meta.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n','utf8')
    player=root/'mod/CZYTAJ.txt'
    txt=once(player.read_text('utf8'),'STARSECTOR PL ASCII 1.0.45','STARSECTOR PL ASCII 1.0.46')
    txt+='\nPoprawiono 16 literalow API: odmiane liczb, czas, dostepnosc, odwolanie do salda i opuszczanie kolonii. Wersja 1.1 nadal jest w opracowaniu.\n'
    player.write_text(txt,'utf8')
    return {'version':'1.0.46','corrected_api_literals':len(changes),'new_api_literals':len(ADDITIONS),
            'changed_classes':len({d[0] for d in changes}|{x[0] for x in ADDITIONS}),
            'api_map_sha256':mapping_sha,'api_map_rows':5260,'data_changes':0}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    print(json.dumps(apply(p.parse_args().worktree),indent=2))
