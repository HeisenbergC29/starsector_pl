#!/usr/bin/env python3
"""Starsector PL 1.0.25: verified short OBF UI labels and ship-accident messages.

Only approved constant-string values; no game Java JAR or data files included.
Snapshot base: 1.0.24. API map 1025 is a byte-compatible copy of API 1024
so version-upgrade checks and recognition of newly translated OBF are consistent.
"""
from pathlib import Path
import argparse, csv, json, shutil
STATUS='VERIFIED_UI_LABEL_AND_ASSEMBLY_1025'
OBF={'com.fs.starfarer.campaign.command.J': {'Warships': 'Okrety wojenne',
                                         'Carriers': 'Lotniskowce',
                                         'Aggression': 'Agresja',
                                         'Weapons': 'Uzbrojenie',
                                         'Fighters': 'Mysliwce',
                                         'Reset': 'Resetuj',
                                         'Confirm': 'Potwierdz'},
 'com.fs.starfarer.campaign.command.CustomProductionPanel': {'Weapons': 'Uzbrojenie',
                                                             'Fighters': 'Mysliwce',
                                                             'Reset': 'Resetuj',
                                                             'Confirm': 'Potwierdz',
                                                             'Cancel': 'Anuluj',
                                                             'Item': 'Przedmiot',
                                                             'Qty': 'Ilosc',
                                                             'Cost': 'Koszt',
                                                             'Yes': 'Tak',
                                                             'No': 'Nie'},
 'com.fs.starfarer.campaign.command.OutpostListPanel': {'Name': 'Nazwa',
                                                        'Conditions': 'Warunki',
                                                        'Location': 'Lokalizacja',
                                                        'Size': 'Wielkosc',
                                                        'Items': 'Przedmioty',
                                                        'Admin': 'Admin.'},
 'com.fs.starfarer.campaign.command.IntelIncomePanel': {'Income': 'Przychod', 'Upkeep': 'Utrzymanie', 'Net': 'Bilans'},
 'com.fs.starfarer.campaign.command.WeaponBlueprintBrowser': {'Small': 'Male',
                                                              'Medium': 'Srednie',
                                                              'Large': 'Duze',
                                                              'Ballistic': 'Balistyczna',
                                                              'Missile': 'Rakietowa',
                                                              'Energy': 'Energetyczna',
                                                              'Size': 'Wielkosc',
                                                              'Type': 'Typ',
                                                              'Cost': 'Koszt'},
 'com.fs.starfarer.campaign.command.FighterBlueprintBrowser': {'Fighter': 'Mysliwiec',
                                                               'Bomber': 'Bombowiec',
                                                               'Interceptor': 'Przechwytywacz',
                                                               'Other': 'Inne',
                                                               'Type': 'Typ',
                                                               'Cost': 'Koszt'},
 'com.fs.starfarer.campaign.command.ShipBlueprintBrowser': {'Frigates': 'Fregaty',
                                                            'Destroyers': 'Niszczyciele',
                                                            'Cruisers': 'Krazowniki',
                                                            'Capitals': 'Okrety liniowe',
                                                            'Warships': 'Okrety wojenne',
                                                            'Carriers': 'Lotniskowce',
                                                            'Civilian': 'Cywilne',
                                                            'Size': 'Wielkosc',
                                                            'Type': 'Typ',
                                                            'Cost': 'Koszt'},
 'com.fs.starfarer.coreui.ooo0': {'Unassigned': 'Nieprzydzielony',
                                  'Assign': 'Przydziel',
                                  'Dismiss': 'Zwolnij',
                                  'Retrain...': 'Przeszkol...',
                                  'Mercenary': 'Najemnik',
                                  'Fearless': 'Nieustraszony'},
 'com.fs.starfarer.campaign.save.null': {'Generate': 'Generuj',
                                         'Name: ': 'Nazwa: ',
                                         'Honorific: ': 'Tytul: ',
                                         'Copy': 'Kopiuj',
                                         'Paste': 'Wklej'},
 'com.fs.starfarer.campaign.comms.v2.D': {'Abandon': 'Porzuc',
                                          'Accept': 'Przyjmij',
                                          'Important': 'Wazne',
                                          'New': 'Nowe',
                                          'Exploration': 'Eksploracja',
                                          'Bounties': 'Nagrody',
                                          'Missions': 'Misje',
                                          'Story': 'Fabula',
                                          'Confirm': 'Potwierdz',
                                          'Cancel': 'Anuluj'},
 'com.fs.starfarer.ui.impl.StandardTooltipV2$9': {'Hostile': 'Wroga',
                                                  'Friendly': 'Przyjazna',
                                                  'Neutral': 'Neutralna',
                                                  'Unknown': 'Nieznana'},
 'com.fs.starfarer.campaign.accidents.ShipLoss': {'lost ': 'utrata ',
                                                  'a ': 'skrzydlo ',
                                                  'the ': 'okret ',
                                                  ' losing ': ' - utrata ',
                                                  ' CR': ' GB'}}

OLD_OBF_SHA='ab9933a7c9879879e0b0a12516dec63cedf9bd7517430400bb2bf0a9577c2560'
NEW_OBF_SHA='dc1fecf61d12d8819bab11b3d1bf20c4aecc294ac27ebce747e08b0dd35ae033'

def replace_one(s,old,new):
    n=s.count(old)
    assert n==1,('Expected one anchor',old,n)
    return s.replace(old,new)

def read_rows(path):
    with path.open(encoding='utf8',newline='') as f:
        r=csv.DictReader(f)
        assert r.fieldnames==['source_class','english_literal','polish_ascii_draft','status']
        return list(r)

def main(root):
    obf=root/'buildtools/NARZEDZIA_OBF'
    api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
    old=read_rows(obf/'TLUMACZENIA_OBF_10124.csv')
    assert len(old)==3213
    prev={(r['source_class'],r['english_literal']) for r in old}
    assert len(prev)==len(old)
    extra=[]
    for cl, mapping in OBF.items():
        for en,pl in mapping.items():
            assert (cl,en) not in prev and en!=pl and en.isascii() and pl.isascii()
            # Source/translation boundaries matter for Java StringBuilder fragments.
            if cl!='com.fs.starfarer.campaign.accidents.ShipLoss':
                assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' '),(en,pl)
            assert en.count('\n')==pl.count('\n')
            extra.append({'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
    assert len(extra)==81
    new=obf/'TLUMACZENIA_OBF_10125.csv'
    assert not new.exists()
    with new.open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
        writer.writeheader();writer.writerows(old+extra)

    p=obf/'main.go';s=p.read_text('utf8')
    s=replace_one(s,'TLUMACZENIA_OBF_10123.csv TLUMACZENIA_OBF_10124.csv','TLUMACZENIA_OBF_10123.csv TLUMACZENIA_OBF_10124.csv TLUMACZENIA_OBF_10125.csv')
    s=replace_one(s,'const currentPatchState = "patched 10124"','const currentPatchState = "patched 10125"')
    s=replace_one(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"'+OLD_OBF_SHA+'": "10124",')
    s=replace_one(s,'loadTranslations("TLUMACZENIA_OBF_10124.csv")','loadTranslations("TLUMACZENIA_OBF_10125.csv")')
    s=replace_one(s,'state == currentPatchState || state == "patched 10123"','state == currentPatchState || state == "patched 10124" || state == "patched 10123"')
    s=replace_one(s,'OBF 1.0.24 | stan:','OBF 1.0.25 | stan:')
    s=replace_one(s,'1.0.24: Lokalizacja tekstow OBF','1.0.25: Lokalizacja tekstow OBF')
    s=replace_one(s,'0.9.99-1.0.24; odmowa modyfikacji','0.9.99-1.0.25; odmowa modyfikacji')
    p.write_text(s,'utf8')
    p=obf/'main_test.go';s=p.read_text('utf8')
    s=replace_one(s,'alreadyThisRelease("patched 10124")','alreadyThisRelease("patched 10125")')
    p.write_text(s,'utf8')
    p=obf/'mapping_10124_test.go';s=p.read_text('utf8')
    s=replace_one(s,'!alreadyThisRelease("patched 10124") || alreadyThisRelease("patched 10123")',
       'alreadyThisRelease("patched 10124") || alreadyThisRelease("patched 10123")')
    p.write_text(s,'utf8')
    t=obf/'mapping_10125_test.go'
    assert not t.exists()
    t.write_text('''package main
import "testing"
func TestOBF10125ShortUILabelsAndShipLoss(t *testing.T) {
 m,e:=loadTranslations("TLUMACZENIA_OBF_10125.csv")
 if e!=nil {t.Fatal(e)}
 if m["com/fs/starfarer/campaign/command/CustomProductionPanel.class"]["Weapons"]!="Uzbrojenie" {t.Fatal("Custom production not translated")}
 if m["com/fs/starfarer/campaign/command/ShipBlueprintBrowser.class"]["Frigates"]!="Fregaty" {t.Fatal("Blueprint categories not translated")}
 if m["com/fs/starfarer/campaign/accidents/ShipLoss.class"][" CR"]!=" GB" {t.Fatal("CR should be GB")}
 if knownPreviousOBFHashes["'''+OLD_OBF_SHA+'''"]!="10124" {t.Fatal("Missing 1.0.24 upgrade")}
 if !alreadyThisRelease("patched 10125") || alreadyThisRelease("patched 10124") {t.Fatal("Wrong version state")}
}
''','utf8')

    p=api/'translations/TLUMACZENIA_JAR_1025.csv'
    assert not p.exists()
    oldapi=api/'translations/TLUMACZENIA_JAR_1024.csv'
    assert len(read_rows(oldapi))==5150, len(read_rows(oldapi))
    shutil.copyfile(oldapi,p)  # no API literal changes in 1.0.25
    p=api/'main.go';s=p.read_text('utf8')
    s=replace_one(s,'const version = "1024"','const version = "1025"')
    s=replace_one(s,'const exeVersion = "1.0.24"','const exeVersion = "1.0.25"')
    s=replace_one(s,'"1023", version}', '"1023", "1024", version}')
    s=replace_one(s,'PL ASCII patch up to 1.0.24','PL ASCII patch up to 1.0.25')
    s=replace_one(s,'const expectedOBFPatched10124 = "'+OLD_OBF_SHA+'"',
                  'const expectedOBFPatched10124 = "'+OLD_OBF_SHA+'"\nconst expectedOBFPatched10125 = "'+NEW_OBF_SHA+'"')
    s=replace_one(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10124',
       'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10125 && hash(obf) != expectedOBFPatched10124')
    p.write_text(s,'utf8')
    p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
    p.write_text(replace_one(p.read_text('utf8'),'const edition = "1.0.24"','const edition = "1.0.25"'),'utf8')
    p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
    assert meta['version']=='1.0.24'
    meta['version']='1.0.25'
    meta['description']=replace_one(meta['description'],'1.0.24','1.0.25')
    p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
    p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
    s=replace_one(s,'STARSECTOR PL ASCII 1.0.24','STARSECTOR PL ASCII 1.0.25')
    s+='\nDopelniono polskie etykiety produkcji i schematow, rozkazow, przychodow, oficerow oraz komunikatow o utracie gotowosci GB.\n'
    p.write_text(s,'utf8')
    print('1.0.25: OBF 3213+81=3294; API map unchanged, mirrored to 1025 for cross-component verification')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('worktree',type=Path)
    main(parser.parse_args().worktree)