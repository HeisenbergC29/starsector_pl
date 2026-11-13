#!/usr/bin/env python3
"""1.0.43: grammar-safe, gender-neutral noun references in 31 visible rules.csv rows.

Delta from 1.0.42; byte-exact splicing only inside one CSV field per row.
NOT a fix to any of the 219 JVM getter invocation instructions.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
from apply_1034 import rows_with_spans

PREV_SHA='fd7697b869bc4951204a7e90583ab8526ae1d046ba715454048b7cbaedcd3751'
SOURCE='data/campaign/rules.csv'
PATCHES={}
def p(key,*changes):
    assert key not in PATCHES and changes
    assert all(a!=b and a.isascii() and b.isascii() for a,b in changes)
    PATCHES[key]=changes

# Fleet/patrol contact: keep rank and role in the text; suppress ambiguous English possessive.
p('TTmarketPostWeirdHMbegin',('$HisOrHer spojrzenie','Spojrzenie rozmowcy'))
for id in ('PathFleetWeirdModsUnknownEnd','PathFleetWeirdModsUnknownEndWeaker','PathFleetWeirdModsUnknownEndTrade','PathFleetWeirdModsEnd4'):
    p(id,('do $hisOrHer zalogi','do wlasnej zalogi'))

# Religious welcomes: body parts belong to the speaking person, not the player.
p('convDefaultGreetingFaithful',('Na ekranie pojawia sie $personName, ktory sklada $hisOrHer dlonie w powitaniu.','Na ekranie pojawia sie $personName, skladajac dlonie na powitanie.'))
p('lkeChalcedonVIPstartNeutral',('skladajac poboznie $hisOrHer dlonie','skladajac poboznie dlonie'))
p('LKEpatherFleetServePath2',('otwiera $hisOrHer oczy','otwiera oczy'))
p('LKEpatherFleetSPOpt',('$HisOrHer oczy','Oczy rozmowcy'))
for id in ('BFFIstationTalk2sedge','BFFIstationTalk2sedgeZ'):
    p(id,('$HisOrHer oczy','Oczy rozmowcy'),('$hisOrHer glos','glos rozmowcy'))
p('gaKA_ttBusinessSel',('$hisOrHer glos','glos agenta'),('$HisOrHer oczy','Oczy agenta'))
for id in ('gaFCArchonPLtellCavin','gaFCArchonTellCavin'):
    p(id,('odnajduje $hisOrHer glos','odzyskuje glos'))
for id in ('gaFCArchonLetMeSeeHerGoad','gaFCArchonLetMeSeeHerAppeal'):
    p(id,('$HisOrHer twarz','Twarz archonta'),('zamyka $hisOrHer oczy','zamyka oczy'))

# Other military/contract conversations.
p('gaPZTriTachEncounterNoZig',('$HisOrHer wzrok','Wzrok rozmowcy'))
p('gaPZDiktatEncounterStandard',('Kropla potu splywa po $hisOrHer twarzy','Kropla potu splywa po twarzy oficera'))
p('gaPZDiktatEncounterOnlyZig2',('$hisOrHer oczy','oczy oficera'))
p('gaATG_pirateScanThreaten1',('do $hisOrHer zalogi','do swojej zalogi'))
p('GARRPirateMainOptions',('klaszcze w $hisOrHer dlonie','klaszcze w dlonie'))
p('proComDeliverGreetingUnderworld',('$HisOrHer wzrok','Wzrok rozmowcy'))
p('LOCRLcontact1again',('sklada $hisOrHer dlonie','sklada dlonie'))
p('LOCRLjudgeResponseF',('$HisOrHer glos','Glos rozmowcy'))
p('sdtuMercReactWeaker',('zamyka $hisOrHer oczy','zamyka oczy'))
p('sdtuMercHegReact1onMyWay',('pokazuje $hisOrHer dlonia','pokazuje dlonia'))
p('affkDeclineSel2',('przesuwajac palcem po $hisOrHer twarzy','przesuwajac palcem po policzku'))
p('plArmadaComms',('Na $hisOrHer twarzy','Na twarzy rozmowcy'))
p('LCP_complySel',('sklada $hisOrHer dlonie','sklada dlonie'))
p('KOLTHolyArmadaCommsA',('"Przyjmujemy twoja prosbe", na $hisOrHer twarzy','"Przyjmujemy twoja prosbe". Na twarzy rozmowcy'))
p('sdPunExSayEconWar',('Na $hisOrHer twarzy','Na twarzy rozmowcy'))

assert len(PATCHES)==31 and sum(map(len,PATCHES.values()))==36
PRONOUN=re.compile(rb'\$[A-Za-z_0-9]*(?:[Hh]eOrShe|[Hh]isOrHer|[Hh]imOrHer|[Mm]anOrWoman|[Hh]imOrHerself)\b')
def sha(blob:bytes)->str:return hashlib.sha256(blob).hexdigest()

def patch_bytes(blob:bytes,check_sha=True):
    if check_sha and sha(blob)!=PREV_SHA:raise ValueError('Wrong 1.0.42 rules.csv SHA')
    if not blob.isascii() or b'\n' in blob.replace(b'\r\n',b''):raise ValueError('Non-ASCII or LF instead of CRLF')
    spans=rows_with_spans(blob)
    if spans[0][2]!=['id','trigger','conditions','script','text','options','notes']:raise ValueError('Invalid CSV layout')
    pieces=[];seen=set();before=after=0;replacements=0;ledger=[]
    for start,end,row in spans[1:]:
        key=row[0]
        if key not in PATCHES:continue
        if key in seen or len(row)!=7:raise ValueError('Duplicated or broken row '+key)
        seen.add(key)
        block=blob[start:end]
        if PRONOUN.findall(row[4].encode('ascii'))==[]:raise ValueError('No pronouns in target row '+key)
        old_text=row[4];before+=len(PRONOUN.findall(old_text.encode('ascii')))
        for english,polish in PATCHES[key]:
            a=english.replace('\"','\"\"').encode('ascii');b=polish.replace('\"','\"\"').encode('ascii')
            if block.count(a)!=1 or old_text.count(english)!=1:raise ValueError(('Expected once in text',key,english))
            block=block.replace(a,b,1);replacements+=1
        parsed=list(csv.reader(block.decode('ascii').splitlines(keepends=True)))
        if len(parsed)!=1 or len(parsed[0])!=7 or parsed[0][:4]!=row[:4] or parsed[0][5:]!=row[5:]:
            raise ValueError(('Non-text column change',key))
        if PRONOUN.search(parsed[0][4].encode('ascii')):raise ValueError(('Remaining gender variable',key))
        after+=len(PRONOUN.findall(parsed[0][4].encode('ascii')))
        pieces.append((start,end,block))
        ledger.append({'id':key,'before_text_sha256':sha(old_text.encode('ascii')),'after_text_sha256':sha(parsed[0][4].encode('ascii')),
                       'before_placeholder_count':len(PRONOUN.findall(old_text.encode('ascii'))),'after_placeholder_count':0,
                       'replacements':len(PATCHES[key])})
    if seen!=set(PATCHES):raise ValueError(('Missing target IDs',set(PATCHES)-seen))
    last=0;out=bytearray()
    for a,b,block in pieces:out.extend(blob[last:a]);out.extend(block);last=b
    out.extend(blob[last:]);out=bytes(out)
    if not out.isascii() or b'\n' in out.replace(b'\r\n',b''):raise ValueError('Bad output ASCII/CRLF')
    if len(rows_with_spans(out))!=len(spans):raise ValueError('Row count changed')
    counts={'modified_rows':len(pieces),'literal_replacements':replacements,'removed_gender_placeholders':before-after,
            'remaining_gender_placeholders_in_modified_rows':after,'sha256_before':sha(blob),'sha256_after':sha(out)}
    assert len(pieces)==31 and replacements==36 and before==36 and after==0
    return out,counts,ledger

def apply(root:Path):
    root=Path(root);f=root/'mod'/SOURCE;info=root/'mod/mod_info.json'
    m=json.loads(info.read_text(encoding='utf8'))
    if m['version']!='1.0.42':raise ValueError('Version must be 1.0.42')
    data,stats,ledger=patch_bytes(f.read_bytes());f.write_bytes(data)
    m['version']='1.0.43';m['description']=m['description'].replace('1.0.42','1.0.43')
    info.write_text(json.dumps(m,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
    file=root/'mod/CZYTAJ.txt';s=file.read_text(encoding='utf8')
    if s.count('STARSECTOR PL ASCII 1.0.42')!=1:raise ValueError('Missing previous readme header')
    file.write_text(s.replace('STARSECTOR PL ASCII 1.0.42','STARSECTOR PL ASCII 1.0.43')+'\nPoprawiono 31 dialogow, usuwajac niepoprawnie skladane frazy dzierzawcze przy czesciach ciala i zalogach.\n',encoding='utf8')
    file=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=file.read_text(encoding='utf8')
    if s.count('const edition = "1.0.42"')!=1:raise ValueError('Missing previous installer edition')
    file.write_text(s.replace('const edition = "1.0.42"','const edition = "1.0.43"'),encoding='utf8')
    return stats,ledger

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('worktree',type=Path);parser.add_argument('--ledger-out',type=Path)
    args=parser.parse_args();stats,ledger=apply(args.worktree)
    if args.ledger_out:args.ledger_out.write_text(json.dumps({'version':'1.0.43','stats':stats,'approved':ledger},ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(stats,indent=2))
