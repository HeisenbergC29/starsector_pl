#!/usr/bin/env python3
"""1.0.23: translate confirmed player-visible UI labels (no technical IDs).

Source: exact JVM CONSTANT_String in Starsector 0.98a-RC8; call sites
individually checked using javap -c -p against the original commercial JARs.
Only changes the translation CSV maps, patcher version support, and release metadata.
Commercial JARs are NOT included in the project/release.
"""
import argparse, csv, hashlib, json
from pathlib import Path

STATUS='VERIFIED_UI_LABEL_BY_JAVAP_1023'
OBF={
 'com.fs.starfarer.ui.impl.CargoTooltipFactory':{
   'Accuracy':'Celnosc', 'Ammo':'Amunicja', 'Available':'Dostepne',
   'Charges':'Ladunki', 'Damage':'Obrazenia', 'Deficit':'Niedobor',
   'Demand':'Zapotrzebowanie', 'Excess':'Nadwyzka',
   'Hitpoints':'Wytrzymalosc', 'Location':'Lokalizacja',
   'Perfect':'Idealna', 'Range':'Zasieg', 'Special':'Specjalne',
   'Speed':'Predkosc', 'Tracking':'Naprowadzanie',
   ' (Beam)':' (Wiazka)',
 },
 'com.fs.starfarer.campaign.ui.marketinfo.CommodityDetailDialog':{
   'Accessibility':'Dostepnosc', 'Dismiss':'Zamknij',
   'Faction':'Frakcja','Income':'Przychod', 'Quantity':'Ilosc',
   'Rank':'Pozycja', 'Size':'Wielkosc',
 },
 'com.fs.starfarer.campaign.ui.marketinfo.cdd.CommodityDetailDialogV2':{
   'Access':'Dostep','Colony':'Kolonia','Consumers':'Odbiorcy',
   'Dismiss':'Zamknij', 'Faction':'Frakcja','Income':'Przychod',
   'Producers':'Producenci','Quantity':'Ilosc','Size':'Wielkosc',
   'Value':'Wartosc',
 },
 'com.fs.starfarer.codex2.CodexDetailPanel':{
   'Demand':'Zapotrzebowanie','Effects':'Efekty',
   'Industry':'Przemysl','Item':'Przedmiot',
   'Production':'Produkcja','Structure':'Budowla',
 },
 'com.fs.starfarer.campaign.ui.marketinfo.EconomyOverviewPanel':{
   'Incoming':'Przychodzace', 'Outgoing':'Wychodzace',
 },
}
API={
 'com.fs.starfarer.api.impl.SimulatorPluginImpl':{
   'Aggressive':'Agresywny','Behavior':'Zachowanie',
   'Cautious':'Ostrozny','Custom':'Wlasne','Default':'Domyslne',
   'Mixed':'Mieszane','None':'Brak','Normal':'Normalny',
   'Officers':'Oficerowie','Other':'Inne','Reckless':'Brawurowy',
   'Some':'Niektorzy', 'Stationary':'Nieruchome','Steady':'Zrownowazony',
 },
 'com.fs.starfarer.api.impl.combat.CRPluginImpl':{
   'Critical':'Krytyczne','Excellent':'Doskonala',
   'Low':'Niskie','None':'Brak','Poor':'Slaba',
   'Serious':'Powazne','Standard':'Standardowa',
 },
 'com.fs.starfarer.api.impl.campaign.CoreReputationPlugin':{
   ' not affected':' bez zmian',
 },
 'com.fs.starfarer.api.impl.campaign.abilities.ToggleAbilityWithCost':{
   'educes the combat readiness ':'mniejsza gotowosc bojowa',
 },
 'com.fs.starfarer.api.impl.campaign.econ.impl.BaseIndustry':{
   'Improvements':'Ulepszenia',
   'Items':'Przedmioty','Production':'Produkcja',
 },
}

# Value for 1.0.23 is computed after running the OBF patcher on the *original*
# starfarer_obf.jar and checking the entire changed-class bytecode audit.
OBF_SHA_1023='f391bc4f0a0c6078845f02415b80378a9d45375ab37eb6c287fcac4058b46abb'


def exact(s,old,new):
    assert s.count(old)==1,(old,s.count(old))
    return s.replace(old,new)


def update_csv(src,dst,mapping,expected):
    assert src.is_file() and not dst.exists(),(src,dst)
    with src.open(encoding='utf8',newline='') as f:
        rr=csv.DictReader(f); fields=rr.fieldnames; rows=list(rr)
    assert fields==['source_class','english_literal','polish_ascii_draft','status']
    assert len(rows)==expected,(src,len(rows),expected)
    keys={(r['source_class'],r['english_literal']) for r in rows}
    assert len(keys)==len(rows)
    for cl,labels in mapping.items():
      for en,pl in labels.items():
        assert en.isascii() and pl.isascii() and (cl,en) not in keys,(cl,en)
        assert '\n' not in en and '\n' not in pl
        assert not ('%' in en) and not ('%' in pl),en
        rows.append({'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
    with dst.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\r\n'); w.writeheader();w.writerows(rows)
    return len(rows)


def main(root):
    assert len(OBF_SHA_1023)==64 and all(x in '0123456789abcdef' for x in OBF_SHA_1023), 'OBF SHA must be verified on original before building release'
    obf=root/'buildtools/NARZEDZIA_OBF'
    api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
    n_obf=update_csv(obf/'TLUMACZENIA_OBF_10121.csv',obf/'TLUMACZENIA_OBF_10123.csv',OBF,3144)
    n_api=update_csv(api/'translations/TLUMACZENIA_JAR_1021.csv',api/'translations/TLUMACZENIA_JAR_1023.csv',API,5108)
    # New OBF patch state; previous patched JAR must remain upgradeable.
    p=obf/'main.go';s=p.read_text('utf8')
    s=exact(s,'TLUMACZENIA_OBF_10118.csv TLUMACZENIA_OBF_10121.csv',
            'TLUMACZENIA_OBF_10118.csv TLUMACZENIA_OBF_10121.csv TLUMACZENIA_OBF_10123.csv')
    s=exact(s,'const currentPatchState = "patched 10121"','const currentPatchState = "patched 10123"')
    s=exact(s,'var knownPreviousOBFHashes = map[string]string{',
            'var knownPreviousOBFHashes = map[string]string{\n\t"cfcf4860d7b451074e6285488f4bf24f91d2dd683aad95ef11ce344894cb84be": "10121",')
    s=exact(s,'loadTranslations("TLUMACZENIA_OBF_10121.csv")','loadTranslations("TLUMACZENIA_OBF_10123.csv")')
    s=exact(s,'state == currentPatchState || state == "patched 10118"',
            'state == currentPatchState || state == "patched 10121" || state == "patched 10118"')
    s=exact(s,'OBF 1.0.21 | stan:','OBF 1.0.23 | stan:')
    s=exact(s,'1.0.21: Lokalizacja tekstow OBF','1.0.23: Lokalizacja tekstow OBF')
    s=exact(s,'0.9.99-1.0.21; odmowa modyfikacji','0.9.99-1.0.23; odmowa modyfikacji')
    p.write_text(s,'utf8')
    # Keep known older Go tests and add exact checks for upgraded OBF state.
    p=obf/'main_test.go';s=p.read_text('utf8')
    s=exact(s,'alreadyThisRelease("patched 10121")','alreadyThisRelease("patched 10123")')
    s=exact(s,'[]string{"original", "patched 10118"',
            '[]string{"original", "patched 10121", "patched 10118"')
    p.write_text(s,'utf8')
    p=obf/'mapping_10121_test.go';s=p.read_text('utf8')
    s=exact(s,'!alreadyThisRelease("patched 10121") || alreadyThisRelease("patched 10118")',
            'alreadyThisRelease("patched 10121") || alreadyThisRelease("patched 10118")')
    p.write_text(s,'utf8')
    p=obf/'mapping_10123_test.go';assert not p.exists()
    p.write_text('''package main
import "testing"
func TestOBF10123RealUIHeaders(t *testing.T) {
 m,e:=loadTranslations("TLUMACZENIA_OBF_10123.csv")
 if e!=nil {t.Fatal(e)}
 if len(m)!=533 {t.Fatalf("expected 533 existing UI classes, got %d",len(m))}
 c:=m["com/fs/starfarer/ui/impl/CargoTooltipFactory.class"]
 if c["Accuracy"]!="Celnosc" || c["Damage"]!="Obrazenia" {t.Fatal("Untranslated cargo labels")}
 if knownPreviousOBFHashes["cfcf4860d7b451074e6285488f4bf24f91d2dd683aad95ef11ce344894cb84be"]!="10121" {t.Fatal("no upgrade from 1.0.22")}
 if !alreadyThisRelease("patched 10123") || alreadyThisRelease("patched 10121") {t.Fatal("wrong version state")}
}
''','utf8')
    # API version + both old and current OBF fingerprints.
    p=api/'main.go';s=p.read_text('utf8')
    s=exact(s,'const version = "1021"','const version = "1023"')
    s=exact(s,'const exeVersion = "1.0.21"','const exeVersion = "1.0.23"')
    s=exact(s,'"1019", "1020", version}', '"1019", "1020", "1021", version}')
    s=exact(s,'PL ASCII patch up to 1.0.21','PL ASCII patch up to 1.0.23')
    s=exact(s,'const expectedOBFPatched10121 = "cfcf4860d7b451074e6285488f4bf24f91d2dd683aad95ef11ce344894cb84be"',
       'const expectedOBFPatched10121 = "cfcf4860d7b451074e6285488f4bf24f91d2dd683aad95ef11ce344894cb84be"\nconst expectedOBFPatched10123 = "'+OBF_SHA_1023+'"')
    s=exact(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10121',
       'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10123 && hash(obf) != expectedOBFPatched10121')
    p.write_text(s,'utf8')
    p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=p.read_text('utf8')
    p.write_text(exact(s,'const edition = "1.0.22"','const edition = "1.0.23"'),'utf8')
    p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
    assert meta['version']=='1.0.22';meta['version']='1.0.23';meta['description']=exact(meta['description'],'1.0.22','1.0.23')
    p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
    p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
    s=exact(s,'STARSECTOR PL ASCII 1.0.22','STARSECTOR PL ASCII 1.0.23')
    s+='\nPrzetlumaczono kolejne etykiety symulatora, ryzyka awarii, handlu, kodeksu i uzbrojenia.\n'
    p.write_text(s,'utf8')
    print('1.0.23:',n_obf,n_api,'map rows;',sum(map(len,OBF.values())),'OBF +',sum(map(len,API.values())),'API')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path);main(ap.parse_args().worktree)