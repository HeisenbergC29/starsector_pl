#!/usr/bin/env python3
"""Reviewed Starsector PL 1.0.26 OBF-only overlay.

86 short player-facing button, tab and table labels in 20 original JVM classes.
Source commercial JARs are not needed to reproduce this source overlay.
"""
import argparse,csv,json,shutil
from pathlib import Path
STATUS='VERIFIED_UI_LABEL_CALLSITE_1026'
OLD_OBF_SHA='dc1fecf61d12d8819bab11b3d1bf20c4aecc294ac27ebce747e08b0dd35ae033'
NEW_OBF_SHA='a475ef535590b79da74d425f9e3f7566c85bed163e4a3795e88a593b7f69f42a'
"""Reviewed OBF-only labels, each checked against original JVM constant pool and javap UI callsites."""
OBF = {
 'com.fs.starfarer.coreui.refit.Q': {
  'Strip':'Rozbroj', 'Save':'Zapisz', 'Undo':'Cofnij', 'Autofit...':'Autodopasuj...', 'Restore...':'Przywroc...', 'Restore':'Przywroc', 'Cancel':'Anuluj',
 },
 'com.fs.starfarer.campaign.ui.marketinfo.PlanetSurveyPanel': {'Continue':'Kontynuuj','Leave':'Odejdz'},
 'com.fs.starfarer.campaign.ui.marketinfo.GroundRaidTargetPickerDialog':{
  'Cancel':'Anuluj','Danger':'Zagrozenie','Impact':'Skutek','Location':'Lokalizacja','Objective':'Cel','Quantity':'Ilosc','Reset':'Resetuj','Value':'Wartosc',
 },
 'com.fs.starfarer.campaign.ui.marketinfo.IndustryPickerDialog':{
  'Build':'Buduj','Cost':'Koszt','Dismiss':'Zamknij','Name':'Nazwa','Type':'Typ','Upkeep':'Utrzymanie',
 },
 'com.fs.starfarer.campaign.ui.marketinfo.CommodityOverviewPanel':{
  'Back':'Wstecz','Incoming':'Przychodzace','Outgoing':'Wychodzace',
 },
 'com.fs.starfarer.coreui.k':{
  'Admins':'Administratorzy','Officers':'Oficerowie','Cancel':'Anuluj','Confirm':'Potwierdz','Reassign':'Zmien przydzial','Reset':'Resetuj',
 },
 'com.fs.starfarer.ui.newui.FleetMemberRecoveryDialog': {'All':'Wszystkie','Recover':'Odzyskaj','Cancel':'Anuluj'},
 'com.fs.starfarer.coreui.refit.ModPickerDialogV3':{'Hullmod':'Mod. kadluba','Installed':'Zainstalowane'},
 'com.fs.starfarer.campaign.ui.intel.PlanetListV2':{
  'Class':'Klasa','Dist':'Odlegl.','Hazard':'Zagrozenie','Location':'Lokalizacja','Name':'Nazwa','Type':'Typ',
 },
 'com.fs.starfarer.campaign.ui.marketinfo.NearbyMarketDialog':{
  'Accessibility':'Dostepnosc','Dismiss':'Zamknij','Dist':'Odlegl.','Market':'Rynek','Size':'Wielkosc',
 },
 'com.fs.starfarer.ui.impl.FleetMemberOrdnancePanel':{
  'Large':'Duze','Medium':'Srednie','Mounts:':'Mocowania:','None':'Brak','Small':'Male',
 },
 'com.fs.starfarer.campaign.ui.marketinfo.b': {'Cancel':'Anuluj','Confirm':'Potwierdz','Downgrade':'Obniz poziom','Upgrade':'Ulepsz'},
 'com.fs.starfarer.campaign.command.OooO':{'Assign':'Przydziel','Dismiss':'Zwolnij','Unassigned':'Nieprzydzielony'},
 'com.fs.starfarer.campaign.command.L':{'Deprioritize':'Obniz priorytet','Prioritize':'Nadaj priorytet'},
 'com.fs.starfarer.coreui.returnnew':{
  'Cargo':'Ladunek','Character':'Postac','Fleet':'Flota','Map':'Mapa','Officers':'Oficerowie','Outposts':'Placowki','Refit':'Modyfikacje',
 },
 'com.fs.starfarer.ui.newui.L':{
  'Character':'Postac','Command':'Dowodzenie','Fleet':'Flota','Intel':'Informacje','Map':'Mapa','Refit':'Modyfikacje',
 },
 'com.fs.starfarer.campaign.ui.trade.o0OO':{
  'Cargo':'Ladunek','Credits':'Kredyty','Jettison':'Wyrzuc','Sort':'Sortuj',
 },
 'com.fs.starfarer.campaign.ui.intel.PLPanel':{'Date':'Data','Event':'Zdarzenie','Events':'Zdarzenia'},
 'com.fs.starfarer.campaign.ui.marketinfo.CommodityRowV2':{'Demand':'Popyt','Production':'Produkcja'},
 'com.fs.starfarer.coreui.refit.wgd2.WeaponGroupDialogV2$3':{'Alternating':'Naprzemiennie','Linked':'Polaczone'},
}

def one(s,a,b):
 assert s.count(a)==1,('expected a single exact replacement',a,s.count(a))
 return s.replace(a,b)

def rows(p):
 with p.open('r',encoding='utf8',newline='') as f:
  r=csv.DictReader(f)
  assert r.fieldnames==['source_class','english_literal','polish_ascii_draft','status']
  return list(r)

def main(root):
 obf=root/'buildtools/NARZEDZIA_OBF';api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old=rows(obf/'TLUMACZENIA_OBF_10125.csv');assert len(old)==3294
 previous={(r['source_class'],r['english_literal']) for r in old};assert len(previous)==len(old)
 extra=[]
 for cl,mapping in OBF.items():
  for en,pl in mapping.items():
   assert en!=pl and en.isascii() and pl.isascii() and (cl,en) not in previous
   assert en.count('\n')==pl.count('\n')
   assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' ')
   extra.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 assert len(extra)==86 and len(OBF)==20
 out=obf/'TLUMACZENIA_OBF_10126.csv';assert not out.exists()
 with out.open('w',encoding='utf8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
  writer.writeheader();writer.writerows(old+extra)
 p=obf/'main.go';s=p.read_text('utf8')
 s=one(s,'TLUMACZENIA_OBF_10124.csv TLUMACZENIA_OBF_10125.csv','TLUMACZENIA_OBF_10124.csv TLUMACZENIA_OBF_10125.csv TLUMACZENIA_OBF_10126.csv')
 s=one(s,'const currentPatchState = "patched 10125"','const currentPatchState = "patched 10126"')
 s=one(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"'+OLD_OBF_SHA+'": "10125",')
 s=one(s,'loadTranslations("TLUMACZENIA_OBF_10125.csv")','loadTranslations("TLUMACZENIA_OBF_10126.csv")')
 s=one(s,'state == currentPatchState || state == "patched 10124"','state == currentPatchState || state == "patched 10125" || state == "patched 10124"')
 s=one(s,'OBF 1.0.25 | stan:','OBF 1.0.26 | stan:')
 s=one(s,'1.0.25: Lokalizacja tekstow OBF','1.0.26: Lokalizacja tekstow OBF')
 s=one(s,'0.9.99-1.0.25; odmowa modyfikacji','0.9.99-1.0.26; odmowa modyfikacji')
 p.write_text(s,'utf8')
 p=obf/'main_test.go';p.write_text(one(p.read_text('utf8'),'alreadyThisRelease("patched 10125")','alreadyThisRelease("patched 10126")'),'utf8')
 p=obf/'mapping_10125_test.go';p.write_text(one(p.read_text('utf8'),'!alreadyThisRelease("patched 10125") || alreadyThisRelease("patched 10124")','alreadyThisRelease("patched 10125") || alreadyThisRelease("patched 10124")'),'utf8')
 p=obf/'mapping_10126_test.go';assert not p.exists()
 p.write_text('''package main
import "testing"
func TestOBF10126ButtonsTabsAndHeaders(t *testing.T) {
 m,e:=loadTranslations("TLUMACZENIA_OBF_10126.csv")
 if e!=nil {t.Fatal(e)}
 cases:=map[string]map[string]string{
  "com/fs/starfarer/coreui/refit/Q.class":{"Autofit...":"Autodopasuj...","Undo":"Cofnij"},
  "com/fs/starfarer/campaign/ui/intel/PlanetListV2.class":{"Hazard":"Zagrozenie","Dist":"Odlegl."},
  "com/fs/starfarer/ui/newui/L.class":{"Fleet":"Flota","Refit":"Modyfikacje"},
  "com/fs/starfarer/campaign/ui/marketinfo/IndustryPickerDialog.class":{"Upkeep":"Utrzymanie","Build":"Buduj"},
 }
 for cl,values:=range cases {for en,pl:=range values {if m[cl][en]!=pl {t.Fatalf("%s %q: %q != %q",cl,en,m[cl][en],pl)}}}
 if knownPreviousOBFHashes["'''+OLD_OBF_SHA+'''"]!="10125" {t.Fatal("Missing 1.0.25 upgrade state")}
 if !alreadyThisRelease("patched 10126") || alreadyThisRelease("patched 10125") {t.Fatal("Wrong current state")}
}
''','utf8')
 oldapip=api/'translations/TLUMACZENIA_JAR_1025.csv';assert len(rows(oldapip))==5150
 newapip=api/'translations/TLUMACZENIA_JAR_1026.csv';assert not newapip.exists()
 shutil.copyfile(oldapip,newapip)
 p=api/'main.go';s=p.read_text('utf8')
 s=one(s,'const version = "1025"','const version = "1026"')
 s=one(s,'const exeVersion = "1.0.25"','const exeVersion = "1.0.26"')
 s=one(s,'"1024", version}', '"1024", "1025", version}')
 s=one(s,'PL ASCII patch up to 1.0.25','PL ASCII patch up to 1.0.26')
 s=one(s,'const expectedOBFPatched10125 = "'+OLD_OBF_SHA+'"',
       'const expectedOBFPatched10125 = "'+OLD_OBF_SHA+'"\nconst expectedOBFPatched10126 = "'+NEW_OBF_SHA+'"')
 s=one(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10125',
       'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10126 && hash(obf) != expectedOBFPatched10125')
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';p.write_text(one(p.read_text('utf8'),'const edition = "1.0.25"','const edition = "1.0.26"'),'utf8')
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
 assert meta['version']=='1.0.25'
 meta['version']='1.0.26';meta['description']=one(meta['description'],'1.0.25','1.0.26')
 p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
 s=one(s,'STARSECTOR PL ASCII 1.0.25','STARSECTOR PL ASCII 1.0.26')
 s+='\nDopelniono polskie przyciski i naglowki refitu, najazdow, przemyslu, planet, oficerow i nawigacji po zakladkach.\n'
 p.write_text(s,'utf8')
 print('1.0.26: OBF 3294+86=3380, API map unchanged (5150 rows)')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 args=p.parse_args();main(args.worktree)