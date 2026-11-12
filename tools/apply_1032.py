#!/usr/bin/env python3
"""Starsector PL 1.0.32: repair assembled light-year fuel tooltips and numeric unit labels.

This is a pure JVM CONSTANT_String patch; no game JAR is distributed or edited
outside the already existing Go patcher's exact-match localization mechanism.
Run after overlays 1013..1031. Keep every original map row/status intact except
its reviewed Polish text; semantic approval is documented separately.
"""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

STATUS_NEW='VERIFIED_COMPOSED_FUEL_TOOLTIP_1032'
A='com.fs.starfarer.api.impl.campaign.abilities.'
C='com.fs.starfarer.api.impl.campaign.'
CORRECTIONS={
 A+'DurationAbilityWithCost2': {
  'Consumes %s light ':('Zuzywa paliwo odpowiadajace %s latom swietlnym ', 'Zuzywa paliwo potrzebne do pokonania %s '),
  ' worth of fuel.':(' paliwa.','.'),
  ' worth of fuel and reduces the combat readiness ':(' i zmniejsza gotowosc bojowa ', ' i obniza gotowosc bojowa '),
  'of all ships by %s of a combat deployment.':('dla wszystkich okretow o %s kosztu wystawienia do walki.','wszystkich okretow o %s kosztu jednego wystawienia do walki.'),
 },
 A+'EmergencyBurnAbility': {
  'Consumes %s light ':('Zuzywa paliwo odpowiadajace %s latom swietlnym ', 'Zuzywa paliwo potrzebne do pokonania %s '),
  ' worth of fuel and reduces the combat readiness ':(' jednostek paliwa i zmniejsza gotowosc bojowa ', ' i obniza gotowosc bojowa '),
  'Consumes %s fuel and reduces the combat readiness of all ships, costing up to %s supplies to recover. Also prevents combat readiness recovery while active.':('Zuzywa %s jednostek paliwa i obniza gotowosc bojowa wszystkich okretow. Jej odzyskanie kosztuje do %s jednostek zaopatrzenia. Ponadto blokuje regeneracje gotowosci bojowej podczas dzialania.','Zuzywa %s jedn. paliwa i obniza gotowosc bojowa wszystkich okretow. Jej odzyskanie kosztuje do %s jedn. zaopatrzenia. Ponadto blokuje regeneracje gotowosci bojowej podczas dzialania.'),
  'Consumes %s fuel and prevents combat readiness recovery while active.':('Zuzywa %s jednostek paliwa i blokuje regeneracje gotowosci bojowej podczas dzialania.','Zuzywa %s jedn. paliwa i blokuje regeneracje gotowosci bojowej podczas dzialania.'),
 },
 A+'FractureJumpAbility': {
  'Jumping into hyperspace consumes %s light ':('Skok w nadprzestrzen zuzywa paliwo odpowiadajace %s latom swietlnym ','Skok w nadprzestrzen zuzywa paliwo potrzebne do pokonania %s '),
  ' worth of fuel and reduces the combat readiness ':(' paliwa i zmniejsza gotowosc bojowa ',' i obniza gotowosc bojowa '),
  'Jumping into hyperspace consumes %s fuel and slightly reduces the combat readiness of all ships, costing up to %s supplies to recover. Jumping into a star system is free.':('Skok do nadprzestrzeni zuzywa %s paliwa i nieznacznie obniza gotowosc bojowa wszystkich okretow. Jej przywrocenie kosztuje do %s jednostek zaopatrzenia. Skok do ukladu gwiezdnego jest darmowy.','Skok do nadprzestrzeni zuzywa %s paliwa i nieznacznie obniza gotowosc bojowa wszystkich okretow. Jej przywrocenie kosztuje do %s jedn. zaopatrzenia. Skok do ukladu gwiezdnego jest darmowy.'),
 },
 C+'rulecmd.salvage.MarketCMD': {
  'A bombardment requires %s fuel. You have %s fuel.':('Bombardowanie wymaga %s jednostek paliwa. Masz %s.','Bombardowanie wymaga %s jedn. paliwa. Masz %s jedn. paliwa.'),
  'The bombardment requires %s fuel. You have %s fuel.':('Bombardowanie wymaga %s jednostek paliwa. Masz %s.','Bombardowanie wymaga %s jedn. paliwa. Masz %s jedn. paliwa.'),
 },
 C+'terrain.HyperspaceTerrainPlugin': {
  'Traveling through hyperspace consumes fuel based on the distance travelled. Your fleet requires %s fuel per light-year.*':('Podrozowanie przez nadprzestrzen zuzywa paliwo zaleznie od pokonanej odleglosci. Twoja flota zuzywa %s jednostek paliwa na rok swietlny.*','Podrozowanie przez nadprzestrzen zuzywa paliwo zaleznie od pokonanej odleglosci. Twoja flota zuzywa %s jedn. paliwa na rok swietlny.*'),
 },
 C+'skills.ContainmentProcedures$Level4': {
  'Your fleet has a base fuel consumption of %s, which ':('Twoja flota zuzywa bazowo %s jednostek paliwa, co ','Bazowe zuzycie paliwa twojej floty to %s jedn., co '),
  ' reduced by %s, or %s units':(' zmniejszono o %s, czyli o %s jednostek',' zmniejszono o %s, czyli o %s jedn.'),
 },
 C+'skills.MakeshiftEquipment$Level3': {
  'Your fleet requires a base %s supplies per month for maintenance, which ':('Twoja flota wymaga bazowo %s jednostek zaopatrzenia miesiecznie na utrzymanie, co ','Bazowe miesieczne zuzycie zaopatrzenia floty na utrzymanie to %s jedn., co '),
  ' reduced by %s, or %s units':(' zmniejszono o %s, czyli o %s jednostek',' zmniejszono o %s, czyli o %s jedn.'),
 },
 C+'skills.Navigation$Level4': {
  'Your fleet has a base fuel consumption of %s, which ':('Twoja flota zuzywa bazowo %s jednostek paliwa, co ','Bazowe zuzycie paliwa twojej floty to %s jedn., co '),
  ' reduced by %s, or %s units':(' zmniejszono o %s, czyli o %s jednostek',' zmniejszono o %s, czyli o %s jedn.'),
 },
 C+'intel.bar.events.DeliveryBarEvent': {
  '"I\'ve got %s units of ':('"Mam %s jednostek ','"Mam %s jedn. '),
  'There are %s units of ':('Jest %s jednostek ','Dostepne: %s jedn. '),
  " Your fleet's fuel tanks can hold an additional %s units of fuel.":(' Zbiorniki paliwa twojej floty pomieszcza dodatkowe %s jednostek paliwa.',' Zbiorniki paliwa twojej floty pomieszcza dodatkowe %s jedn. paliwa.'),
  " Your fleet's holds can accommodate an additional %s units of cargo.":(' Ladownie twojej floty pomieszcza dodatkowe %s jednostek ladunku.',' Ladownie twojej floty pomieszcza dodatkowe %s jedn. ladunku.'),
 },
 C+'intel.bar.events.DeliveryMissionIntel': {
  '%s units to ':('%s jednostek do ','%s jedn. do '),
 },
}
NEW={cl:{"year's":'roku swietlnego',"years'":'lat swietlnych'} for cl in (
 A+'DurationAbilityWithCost2',A+'EmergencyBurnAbility',A+'FractureJumpAbility')}
FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def exact(s,a,b):
    count=s.count(a)
    if count!=1:raise AssertionError(('expected unique anchor',a,count))
    return s.replace(a,b,1)

def edits():return sum(len(p) for p in CORRECTIONS.values())

def apply(root:Path):
    src=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
    old=src/'translations/TLUMACZENIA_JAR_1030.csv'
    new=src/'translations/TLUMACZENIA_JAR_1032.csv'
    if new.exists():raise FileExistsError(new)
    with old.open(encoding='utf8',newline='') as f:
        read=csv.DictReader(f);assert read.fieldnames==FIELDS;rows=list(read)
    if len(rows)!=5219:raise AssertionError('Unexpected previous mapping row count')
    keys={(x['source_class'],x['english_literal']) for x in rows}
    replacements=set()
    for row in rows:
        cl,en=row['source_class'],row['english_literal']
        if en not in CORRECTIONS.get(cl,{}):continue
        previous,target=CORRECTIONS[cl][en]
        if row['polish_ascii_draft']!=previous:raise AssertionError((cl,en,row['polish_ascii_draft'],previous))
        if len(re.findall(r'%(?:\d+\$)?[sdfc]',previous))!=len(re.findall(r'%(?:\d+\$)?[sdfc]',target)):
            raise AssertionError(('format markers',cl,en))
        if not target.isascii() or en.count('\n')!=target.count('\n'):raise AssertionError(('charset',cl,en))
        row['polish_ascii_draft']=target
        replacements.add((cl,en))
    expected={(cl,en) for cl,pairs in CORRECTIONS.items() for en in pairs}
    if replacements!=expected:raise AssertionError(('missing old keys',expected-replacements))
    for cl,items in NEW.items():
        for en,pl in items.items():
            if (cl,en) in keys or not en.isascii() or not pl.isascii():raise AssertionError((cl,en))
            rows.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS_NEW))
    assert len(rows)==5225
    with new.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
    main=src/'main.go';s=main.read_text('utf8')
    s=exact(s,'const version = "1030"','const version = "1032"')
    s=exact(s,'const exeVersion = "1.0.30"','const exeVersion = "1.0.32"')
    s=exact(s,'"1028", "1029", version}','"1028", "1029", "1030", version}')
    s=exact(s,'PL ASCII patch up to 1.0.30','PL ASCII patch up to 1.0.32')
    main.write_text(s,'utf8')
    # OBF map and patch state remain identical; only its visible version label changes.
    obf=root/'buildtools/NARZEDZIA_OBF/main.go'
    s=obf.read_text('utf8');s=exact(s,'OBF 1.0.30 | stan:', 'OBF 1.0.32 | stan:')
    obf.write_text(s,'utf8')
    inst=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
    inst.write_text(exact(inst.read_text('utf8'),'const edition = "1.0.31"','const edition = "1.0.32"'),'utf8')
    mod=root/'mod/mod_info.json';j=json.loads(mod.read_text('utf8'))
    if j['version']!='1.0.31':raise AssertionError('Wrong input version')
    j['version']='1.0.32';j['description']=exact(j['description'],'1.0.31','1.0.32')
    mod.write_text(json.dumps(j,indent=2,ensure_ascii=True)+'\n','utf8')
    readme=root/'mod/CZYTAJ.txt';st=readme.read_text('utf8');st=exact(st,'STARSECTOR PL ASCII 1.0.31','STARSECTOR PL ASCII 1.0.32')
    st+='\nPoprawiono 3 wieloczlonowe podpowiedzi paliwa (rok/lata swietlne) i odmiane liczbowych jednostek w komunikatach. Bajtkod gry bez zmian.\n'
    readme.write_text(st,'utf8')
    summary={'version':'1.0.32','api_added_literals':6,'api_corrected_literals':edits(),'api_map_rows':len(rows),'obf_map_changes':0,'data_file_changes':0}
    print(json.dumps(summary,indent=2));return summary

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 apply(p.parse_args().worktree)
