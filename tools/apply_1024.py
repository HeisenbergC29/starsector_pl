#!/usr/bin/env python3
"""Starsector PL 1.0.24: menu, refit filters and campaign display labels.

Review: original 0.98a-RC8 JVM CONSTANT_String and javap callsites.
Never translate Java enum identifiers or modify executable bytecode.
Snapshot base: 1.0.23. Reproducible overlay, retaining old map CSV for upgrades.
"""
import argparse, csv, json
from pathlib import Path

STATUS='VERIFIED_UI_CALLSITE_1024'
OBF={
 'com.fs.starfarer.title.C':{
  'Back':'Wstecz','Continue':'Kontynuuj','Tutorials':'Samouczki',
  'Missions':'Misje','Codex':'Kodeks','Settings':'Ustawienia',
  'Credits':'Tworcy','Quit':'Wyjdz',
 },
 'com.fs.starfarer.coreui.refit.WeaponPickerDialog':{
  'Ballistic':'Balistyczna','Energy':'Energetyczna','Missile':'Rakietowa','Owned':'Posiadane',
 },
 'com.fs.starfarer.coreui.refit.FighterPickerDialog':{
  'Bombers':'Bombowce','Fighters':'Mysliwce','Interceptors':'Przechwytujace','Owned':'Posiadane',
 },
 'com.fs.starfarer.coreui.refit.wgd2.WeaponGroupDialogV2':{
  'Auto-assign':'Auto-przypisz','Cancel':'Anuluj','Confirm':'Potwierdz',
  'Flux':'Strumien','Group':'Grupa','Weapon':'Bron',
 },
 'com.fs.starfarer.launcher.opengl.GLLauncher':{
  'Activate!':'Aktywuj!','Mods...':'Mody...','Options...':'Opcje...',
 },
 'com.fs.starfarer.launcher.opengl.ooOO':{
  'Antialiasing':'Wygladzanie krawedzi','Apply':'Zastosuj','Cancel':'Anuluj',
 },
}
API={
 'com.fs.starfarer.api.impl.PlanetSearchData$1':{'Planets':'Planety','Stars':'Gwiazdy'},
 'com.fs.starfarer.api.impl.PlanetSearchData$2':{
   'Claimed':'Objete roszczeniami','Populated':'Zamieszkane','Unclaimed':'Bez roszczen',
 },
 'com.fs.starfarer.api.campaign.econ.MonthlyReport':{'Colonies':'Kolonie'},
 'com.fs.starfarer.api.campaign.impl.items.BaseSpecialItemPlugin':{
  'None':'Brak','Price: ':'Cena: ',
 },
 'com.fs.starfarer.api.campaign.FleetAssignment':{
  'Attacking':'Atakuje','Defending':'Broni','Following':'Podaza',
  'Holding':'Utrzymuje pozycje','Intercepting':'Przechwytuje',
  'Orbiting':'Orbituje','Raiding':'Przeprowadza najazd','Travelling':'Podrozuje',
 },
}
OLD_OBF='f391bc4f0a0c6078845f02415b80378a9d45375ab37eb6c287fcac4058b46abb'
# Replace after exact patch on original starfarer_obf.jar is independently SHA-checked.
NEW_OBF='ab9933a7c9879879e0b0a12516dec63cedf9bd7517430400bb2bf0a9577c2560'


def replace(s,a,b):
    assert s.count(a)==1,('expected unique source anchor',repr(a),s.count(a))
    return s.replace(a,b)


def csv_overlay(src,dst,extra,num):
    assert src.is_file() and not dst.exists(),(src,dst)
    with src.open('r',newline='',encoding='utf8') as f:
        rd=csv.DictReader(f); assert rd.fieldnames==['source_class','english_literal','polish_ascii_draft','status']; old=list(rd)
    assert len(old)==num,(len(old),num)
    existing={(r['source_class'],r['english_literal']) for r in old}
    assert len(existing)==len(old)
    new=[]
    for cl,pairs in extra.items():
        for en,pl in pairs.items():
            assert en.isascii() and pl.isascii() and en!=pl and (cl,en) not in existing
            assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' '),(en,pl)
            assert '\n' not in en+pl and '%' not in en+pl and '{' not in en+pl and '$' not in en+pl
            new.append({'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
    with dst.open('w',newline='',encoding='utf8') as f:
        wr=csv.DictWriter(f,fieldnames=rd.fieldnames,lineterminator='\r\n');wr.writeheader();wr.writerows(old+new)
    return len(old),len(new)


def main(root):
    obf=root/'buildtools/NARZEDZIA_OBF'
    api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
    older,nobs=csv_overlay(obf/'TLUMACZENIA_OBF_10123.csv',obf/'TLUMACZENIA_OBF_10124.csv',OBF,3185)
    olda,na=csv_overlay(api/'translations/TLUMACZENIA_JAR_1023.csv',api/'translations/TLUMACZENIA_JAR_1024.csv',API,5134)
    assert nobs==28 and na==16,(nobs,na)
    # Preserve complete prior map history to upgrade exactly from 1.0.23.
    p=obf/'main.go';s=p.read_text('utf8')
    s=replace(s,'TLUMACZENIA_OBF_10121.csv TLUMACZENIA_OBF_10123.csv',
                 'TLUMACZENIA_OBF_10121.csv TLUMACZENIA_OBF_10123.csv TLUMACZENIA_OBF_10124.csv')
    s=replace(s,'const currentPatchState = "patched 10123"','const currentPatchState = "patched 10124"')
    s=replace(s,'var knownPreviousOBFHashes = map[string]string{',
                 'var knownPreviousOBFHashes = map[string]string{\n\t"'+OLD_OBF+'": "10123",')
    s=replace(s,'loadTranslations("TLUMACZENIA_OBF_10123.csv")','loadTranslations("TLUMACZENIA_OBF_10124.csv")')
    s=replace(s,'state == currentPatchState || state == "patched 10121"',
                 'state == currentPatchState || state == "patched 10123" || state == "patched 10121"')
    s=replace(s,'OBF 1.0.23 | stan:','OBF 1.0.24 | stan:')
    s=replace(s,'1.0.23: Lokalizacja tekstow OBF','1.0.24: Lokalizacja tekstow OBF')
    s=replace(s,'0.9.99-1.0.23; odmowa modyfikacji','0.9.99-1.0.24; odmowa modyfikacji')
    p.write_text(s,'utf8')
    p=obf/'main_test.go';s=p.read_text('utf8')
    s=replace(s,'alreadyThisRelease("patched 10123")','alreadyThisRelease("patched 10124")')
    p.write_text(s,'utf8')
    p=obf/'mapping_10123_test.go';s=p.read_text('utf8')
    s=replace(s,'!alreadyThisRelease("patched 10123") || alreadyThisRelease("patched 10121")',
                 'alreadyThisRelease("patched 10123") || alreadyThisRelease("patched 10121")')
    p.write_text(s,'utf8')
    p=obf/'mapping_10124_test.go';assert not p.exists()
    p.write_text('''package main
import "testing"
func TestOBF10124MenuAndRefit(t *testing.T) {
 m,e:=loadTranslations("TLUMACZENIA_OBF_10124.csv")
 if e!=nil {t.Fatal(e)}
 if m["com/fs/starfarer/title/C.class"]["Continue"]!="Kontynuuj" || m["com/fs/starfarer/title/C.class"]["Settings"]!="Ustawienia" {t.Fatal("Missing Polish main menu")}
 if m["com/fs/starfarer/coreui/refit/WeaponPickerDialog.class"]["Ballistic"]!="Balistyczna" {t.Fatal("Missing weapon tab")}
 if knownPreviousOBFHashes["'''+OLD_OBF+'''"]!="10123" {t.Fatal("Missing 1.0.23 upgrade state")}
 if !alreadyThisRelease("patched 10124") || alreadyThisRelease("patched 10123") {t.Fatal("Wrong release state")}
}
''','utf8')
    p=api/'main.go';s=p.read_text('utf8')
    s=replace(s,'const version = "1023"','const version = "1024"')
    s=replace(s,'const exeVersion = "1.0.23"','const exeVersion = "1.0.24"')
    s=replace(s,'"1020", "1021", version}', '"1020", "1021", "1023", version}')
    s=replace(s,'PL ASCII patch up to 1.0.23','PL ASCII patch up to 1.0.24')
    s=replace(s,'const expectedOBFPatched10123 = "'+OLD_OBF+'"',
        'const expectedOBFPatched10123 = "'+OLD_OBF+'"\nconst expectedOBFPatched10124 = "'+NEW_OBF+'"')
    s=replace(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10123',
        'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10124 && hash(obf) != expectedOBFPatched10123')
    p.write_text(s,'utf8')
    p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
    p.write_text(replace(p.read_text('utf8'),'const edition = "1.0.23"','const edition = "1.0.24"'),'utf8')
    p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
    assert meta['version']=='1.0.23';meta['version']='1.0.24'
    meta['description']=replace(meta['description'],'1.0.23','1.0.24')
    p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
    p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
    s=replace(s,'STARSECTOR PL ASCII 1.0.23','STARSECTOR PL ASCII 1.0.24')
    s+='\nPrzetlumaczono brakujace przyciski glownego menu, launchera, zarzadzania uzbrojeniem i filtry planet oraz statusy flot.\n'
    p.write_text(s,'utf8')
    print('1.0.24: OBF +',nobs,'API +',na,'rows: ',older+nobs,olda+na)

if __name__=='__main__':
    arg=argparse.ArgumentParser();arg.add_argument('worktree',type=Path)
    main(arg.parse_args().worktree)