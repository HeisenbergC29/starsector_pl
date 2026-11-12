#!/usr/bin/env python3
"""Starsector PL 1.0.28, +64 OBF and +28 API reviewed player-visible labels.

Reproduces exact source changes without requiring commercial JARs.
Only class-scoped CONSTANT_String payloads, not executable methods or IDs.
"""
import argparse,csv,json,shutil
from pathlib import Path
STATUS='VERIFIED_VISIBLE_UI_METHOD_1028'
OLD_OBF_SHA='8d009ff086bc592b66fbb54b0e23ce11f3c2c85fb2a9ebb6c514c58515f1262d'
NEW_OBF_SHA='282a465e022c5bf292b08cde9cad59db11f0a92cac067dd237fca1475c694fa6'
"""Reviewed OBF-only labels, each checked against original JVM constant pool and javap UI callsites."""
OBF = {'com.fs.starfarer.campaign.ui.Stringnew': {'Abort': 'Przerwij',
                                            'Capital': 'Okrety liniowe',
                                            'Cruisers': 'Krazowniki',
                                            'Destroyers': 'Niszczyciele',
                                            'Fighters': 'Mysliwce',
                                            'Frigates': 'Fregaty'},
 'com.fs.starfarer.campaign.ui.intel.H': {'Load': 'Wczytaj',
                                          'Reset': 'Resetuj',
                                          'Resources': 'Zasoby',
                                          'Store': 'Zapisz'},
 'com.fs.starfarer.campaign.ui.marketinfo.ExistingIndustryPickerDialog': {'Cancel': 'Anuluj',
                                                                          'Empty': 'Puste',
                                                                          'Industry/structure': 'Przemysl/struktura'},
 'com.fs.starfarer.campaign.ui.marketinfo.M': {'Illegal': 'Nielegalne', 'Legal': 'Legalne'},
 'com.fs.starfarer.campaign.ui.marketinfo.MarketInfoPanel': {'Commodities': 'Towary',
                                                             'Events': 'Wydarzenia'},
 'com.fs.starfarer.campaign.ui.marketinfo.float': {'Found: ': 'Znaleziono: ',
                                                   'Searching...': 'Wyszukiwanie...'},
 'com.fs.starfarer.campaign.ui.marketinfo.intnew': {'Building': 'W budowie', 'Queued': 'W kolejce'},
 'com.fs.starfarer.campaign.ui.marketinfo.oOoO': {'Closed': 'Zamkniete', 'Growth': 'Rozwoj'},
 'com.fs.starfarer.campaign.ui.marketinfo.t': {'Abandon': 'Porzuc', 'Stabilize': 'Stabilizuj'},
 'com.fs.starfarer.campaign.ui.trade.F': {'Buy': 'Kup', 'Sell': 'Sprzedaj'},
 'com.fs.starfarer.coreui.A.O0Oo': {'Days': 'Dni',
                                    'Distance': 'Odleglosc',
                                    'Fuel': 'Paliwo',
                                    'Hyperspace': 'Nadprzestrzen',
                                    'Waypoint': 'Punkt trasy'},
 'com.fs.starfarer.coreui.A.OoOO': {'Quantity': 'Ilosc', 'Unsurveyed': 'Niezbadana'},
 'com.fs.starfarer.coreui.A.R': {'Constellations': 'Konstelacje',
                                 'Exploration': 'Eksploracja',
                                 'Inhabited': 'Zamieszkane',
                                 'Legend': 'Legenda',
                                 'Names': 'Nazwy',
                                 'Starscape': 'Mapa gwiazd'},
 'com.fs.starfarer.coreui.privatesuper': {'Cargo': 'Ladunek',
                                          'Fleet': 'Flota',
                                          'Fuel': 'Paliwo',
                                          'Personnel': 'Personel',
                                          'Supplies': 'Zaopatrzenie',
                                          'Supplies/day': 'Zaopatrzenie/dzien'},
 'com.fs.starfarer.coreui.refit.ManageVariantsDialog$Oo': {'Delete': 'Usun',
                                                           'Load': 'Wczytaj',
                                                           'Rename': 'Zmien nazwe'},
 'com.fs.starfarer.ui.impl.F$2': {'Friendly': 'Przyjazny',
                                  'Hostile': 'Wrogi',
                                  'Neutral': 'Neutralny',
                                  'Unknown': 'Nieznany'},
 'com.fs.starfarer.ui.impl.K': {'Add': 'Dodaj',
                                'Cancel': 'Anuluj',
                                'Category': 'Kategoria',
                                'Clear': 'Wyczysc',
                                'Empty': 'Pusto',
                                'Remove': 'Usun',
                                'Reset': 'Resetuj'},
 'com.fs.starfarer.ui.newui.nullsuper': {'Name:': 'Imie:',
                                         'None': 'Brak',
                                         'Post:': 'Funkcja:',
                                         'Rank:': 'Stopien:'}}
API = {'com.fs.starfarer.api.impl.campaign.FactionPersonalityPickerPluginImpl': {'Aggressive': 'Agresywny',
                                                                           'Cautious': 'Ostrozny',
                                                                           'Reckless': 'Brawurowy',
                                                                           'Steady': 'Opanowany'},
 'com.fs.starfarer.api.impl.campaign.NewGameDialogPluginImpl': {'Continue': 'Kontynuuj',
                                                                'Leave': 'Odejdz'},
 'com.fs.starfarer.api.impl.campaign.RuleBasedInteractionDialogPluginImpl': {'Leave': 'Odejdz'},
 'com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin': {'Cancel': 'Anuluj',
                                                              'Confirm': 'Potwierdz'},
 'com.fs.starfarer.api.impl.campaign.intel.BaseMissionIntel': {'Abandon': 'Porzuc',
                                                               'Accept': 'Przyjmij'},
 'com.fs.starfarer.api.impl.campaign.intel.events.HostileActivityEventIntel': {'Danger': 'Zagrozenie',
                                                                               'Extreme': 'Skrajne',
                                                                               'High': 'Wysokie',
                                                                               'Low': 'Niskie',
                                                                               'Medium': 'Srednie',
                                                                               'Minimal': 'Minimalne',
                                                                               'None': 'Brak',
                                                                               'Unknown': 'Nieznane'},
 'com.fs.starfarer.api.impl.campaign.rulecmd.AddRemoveCommodity': {'Acquired ': 'Zdobyto ',
                                                                   'Gained ': 'Uzyskano ',
                                                                   'Lost ': 'Utracono '},
 'com.fs.starfarer.api.impl.campaign.submarkets.LocalResourcesSubmarketPlugin': {'Leave': 'Zostaw',
                                                                                 'Now': 'Teraz',
                                                                                 'Take': 'Wez'},
 'com.fs.starfarer.api.impl.campaign.submarkets.StoragePlugin': {'Leave': 'Zostaw',
                                                                 'Pay': 'Zaplac',
                                                                 'Take': 'Wez'}}

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
 old=rows(obf/'TLUMACZENIA_OBF_10127.csv');assert len(old)==3421
 previous={(r['source_class'],r['english_literal']) for r in old};assert len(previous)==len(old)
 extra=[]
 for cl,mapping in OBF.items():
  for en,pl in mapping.items():
   assert en!=pl and en.isascii() and pl.isascii() and (cl,en) not in previous
   assert en.count('\n')==pl.count('\n')
   assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' '),(cl,repr(en),repr(pl))
   assert not (en.isupper() and len(en)>2)
   extra.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 assert len(extra)==64 and len(OBF)==18
 out=obf/'TLUMACZENIA_OBF_10128.csv';assert not out.exists()
 with out.open('w',encoding='utf8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
  writer.writeheader();writer.writerows(old+extra)
 p=obf/'main.go';s=p.read_text('utf8')
 s=one(s,'TLUMACZENIA_OBF_10126.csv TLUMACZENIA_OBF_10127.csv','TLUMACZENIA_OBF_10126.csv TLUMACZENIA_OBF_10127.csv TLUMACZENIA_OBF_10128.csv')
 s=one(s,'const currentPatchState = "patched 10127"','const currentPatchState = "patched 10128"')
 s=one(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"'+OLD_OBF_SHA+'": "10127",')
 s=one(s,'loadTranslations("TLUMACZENIA_OBF_10127.csv")','loadTranslations("TLUMACZENIA_OBF_10128.csv")')
 s=one(s,'state == currentPatchState || state == "patched 10126"','state == currentPatchState || state == "patched 10127" || state == "patched 10126"')
 s=one(s,'OBF 1.0.27 | stan:','OBF 1.0.28 | stan:')
 s=one(s,'1.0.27: Lokalizacja tekstow OBF','1.0.28: Lokalizacja tekstow OBF')
 s=one(s,'0.9.99-1.0.27; odmowa modyfikacji','0.9.99-1.0.28; odmowa modyfikacji')
 p.write_text(s,'utf8')
 p=obf/'main_test.go';p.write_text(one(p.read_text('utf8'),'alreadyThisRelease("patched 10127")','alreadyThisRelease("patched 10128")'),'utf8')
 p=obf/'mapping_10127_test.go'
 p.write_text(one(p.read_text('utf8'),'!alreadyThisRelease("patched 10127") || alreadyThisRelease("patched 10126")','alreadyThisRelease("patched 10127") || alreadyThisRelease("patched 10126")'),'utf8')
 p=obf/'mapping_10128_test.go';assert not p.exists()
 p.write_text('package main\nimport "testing"\nfunc TestOBF1028SafeUserLabels(t *testing.T) {\n m,e:=loadTranslations("TLUMACZENIA_OBF_10128.csv")\n if e!=nil {t.Fatal(e)}\n cases:=map[string]map[string]string{\n  "com/fs/starfarer/ui/impl/K.class":{"Add":"Dodaj","Category":"Kategoria"},\n  "com/fs/starfarer/coreui/A/R.class":{"Starscape":"Mapa gwiazd","Names":"Nazwy"},\n  "com/fs/starfarer/campaign/ui/marketinfo/M.class":{"Legal":"Legalne","Illegal":"Nielegalne"},\n }\n for cl,entries:=range cases {for en,pl:=range entries {if m[cl][en]!=pl {t.Fatalf("%s %q: %q != %q",cl,en,m[cl][en],pl)}}}\n if knownPreviousOBFHashes["8d009ff086bc592b66fbb54b0e23ce11f3c2c85fb2a9ebb6c514c58515f1262d"]!="10127" {t.Fatal("Missing 1.0.27 upgrade hash")}\n if !alreadyThisRelease("patched 10128") || alreadyThisRelease("patched 10127") {t.Fatal("Wrong current state")}\n}\n','utf8')
 oldapi=rows(api/'translations/TLUMACZENIA_JAR_1027.csv');assert len(oldapi)==5180
 known_api={(r['source_class'],r['english_literal']) for r in oldapi}
 extra_api=[]
 for cl,values in API.items():
  for en,pl in values.items():
   assert en!=pl and en.isascii() and pl.isascii() and (cl,en) not in known_api
   assert en.count('\n')==pl.count('\n')
   assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' '),(cl,repr(en),repr(pl))
   assert not (en.isupper() and len(en)>2)
   extra_api.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 assert len(extra_api)==28 and len(API)==9
 newapi=api/'translations/TLUMACZENIA_JAR_1028.csv';assert not newapi.exists()
 with newapi.open('w',encoding='utf8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
  writer.writeheader();writer.writerows(oldapi+extra_api)
 p=api/'main.go';s=p.read_text('utf8')
 s=one(s,'const version = "1027"','const version = "1028"')
 s=one(s,'const exeVersion = "1.0.27"','const exeVersion = "1.0.28"')
 s=one(s,'"1025", "1026", version}', '"1025", "1026", "1027", version}')
 s=one(s,'PL ASCII patch up to 1.0.27','PL ASCII patch up to 1.0.28')
 s=one(s,'const expectedOBFPatched10127 = "'+OLD_OBF_SHA+'"','const expectedOBFPatched10127 = "'+OLD_OBF_SHA+'"\nconst expectedOBFPatched10128 = "'+NEW_OBF_SHA+'"')
 s=one(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10127','hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10128 && hash(obf) != expectedOBFPatched10127')
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';p.write_text(one(p.read_text('utf8'),'const edition = "1.0.27"','const edition = "1.0.28"'),'utf8')
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
 assert meta['version']=='1.0.27'
 meta['version']='1.0.28';meta['description']=one(meta['description'],'1.0.27','1.0.28')
 p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
 s=one(s,'STARSECTOR PL ASCII 1.0.27','STARSECTOR PL ASCII 1.0.28')
 s+='\nUzupelniono etykiety mapy sektora, ryzyka, handlu, osobowosci i magazynowania.\n'
 p.write_text(s,'utf8')
 print('1.0.28: OBF 3421+64=3485, API 5180+28=5208; data unchanged')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 args=p.parse_args();main(args.worktree)