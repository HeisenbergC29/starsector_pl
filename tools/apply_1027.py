#!/usr/bin/env python3
"""Starsector PL 1.0.27, +41 OBF and +30 API reviewed player-visible labels.

Reproduces exact source changes without requiring commercial JARs.
Only class-scoped CONSTANT_String payloads, not executable methods or IDs.
"""
import argparse,csv,json,shutil
from pathlib import Path
STATUS='VERIFIED_UI_LABEL_CALLSITE_1027'
OLD_OBF_SHA='a475ef535590b79da74d425f9e3f7566c85bed163e4a3795e88a593b7f69f42a'
NEW_OBF_SHA='8d009ff086bc592b66fbb54b0e23ce11f3c2c85fb2a9ebb6c514c58515f1262d'
"""Reviewed OBF-only labels, each checked against original JVM constant pool and javap UI callsites."""
OBF = {'com.fs.starfarer.campaign.ui.trade.new': {'Capital': 'Okret liniowy',
                                            'Cruiser': 'Krazownik',
                                            'Defense': 'Obrona',
                                            'Destroyer': 'Niszczyciel',
                                            'Fighter': 'Mysliwiec',
                                            'Frigate': 'Fregata',
                                            'Maneuverability': 'Manewrowosc',
                                            'None': 'Brak',
                                            'Special': 'Specjalne',
                                            'Unlimited': 'Bez ograniczen'},
 'com.fs.starfarer.ui.impl.CargoTooltipFactory$3': {'Available': 'Dostepne',
                                                    'Deficit': 'Niedobor',
                                                    'Demand': 'Popyt',
                                                    'Excess': 'Nadwyzka',
                                                    'Location': 'Lokalizacja'},
 'com.fs.starfarer.ui.impl.W$1': {'Aggression': 'Agresja', 'Command': 'Dowodzenie'},
 'com.fs.starfarer.ui.impl.oO0O': {'All': 'Wszystkie',
                                   'Allies': 'Sojusznicy',
                                   'Cancel': 'Anuluj',
                                   'Deploy': 'Rozmiesc',
                                   'Deployed': 'Rozmieszczone',
                                   'Opponents': 'Przeciwnicy'},
 'com.fs.starfarer.ui.impl.StandardTooltipV2$1': {'Fearless': 'Nieustraszony', 'Unlimited': 'Bez ograniczen'},
 'com.fs.starfarer.campaign.ui.class': {'Cargo': 'Ladunek',
                                        'Resources': 'Zasoby',
                                        'Salvage': 'Odzysk',
                                        'Trade': 'Handel',
                                        'Uninhabited': 'Niezamieszkane'},
 'com.fs.starfarer.title.OoOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO.OoOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO$oo': {'Accelerate': 'Przyspiesz',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Assault': 'Szturmuj',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Avoid': 'Unikaj',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Decelerate': 'Zwolnij',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Defend': 'Bron',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Eliminate': 'Wyeliminuj',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Engage': 'Atakuj',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Harass': 'Nekaj',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Ignore': 'Ignoruj',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Patrol': 'Patroluj',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'Retreat': 'Wycofaj '
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            'sie'}}
API = {'com.fs.starfarer.api.impl.campaign.rulecmd.salvage.MarketCMD': {'Continue': 'Kontynuuj',
                                                                  'Select': 'Wybierz',
                                                                  'Spoils': 'Zdobycz',
                                                                  'Yes': 'Tak'},
 'com.fs.starfarer.api.impl.campaign.FleetInteractionDialogPluginImpl': {'Cancel': 'Anuluj',
                                                                         'Continue': 'Kontynuuj',
                                                                         'Disengage': 'Zerwij kontakt',
                                                                         'Leave': 'Odejdz',
                                                                         'Proceed': 'Kontynuuj',
                                                                         'Salvaged': 'Odzyskano',
                                                                         'Side': 'Strona',
                                                                         'Yes': 'Tak'},
 'com.fs.starfarer.api.impl.campaign.intel.bar.events.PlanetaryShieldBarEvent': {'Continue': 'Kontynuuj'},
 'com.fs.starfarer.api.impl.campaign.intel.PerseanLeagueMembership': {'Accepted': 'Przyjeto',
                                                                      'Annulled': 'Uniewazniono',
                                                                      'Ended': 'Zakonczono',
                                                                      'Expired': 'Wygaslo',
                                                                      'League': 'Liga',
                                                                      'Colonies': 'Kolonie'},
 'com.fs.starfarer.api.impl.campaign.intel.punitive.PunitiveExpeditionIntel': {'Avert': 'Zapobiegnij'},
 'com.fs.starfarer.api.impl.campaign.intel.ProcurementMissionIntel': {'Dismiss': 'Zamknij'},
 'com.fs.starfarer.api.impl.campaign.JumpPointInteractionDialogPluginImpl': {'Leave': 'Odejdz'},
 'com.fs.starfarer.api.impl.campaign.rulecmd.salvage.SalvageEntity': {'Continue': 'Kontynuuj',
                                                                      'Leave': 'Odejdz',
                                                                      'Salvaged': 'Odzyskano'},
 'com.fs.starfarer.api.impl.campaign.rulecmd.salvage.special.ShipRecoverySpecial': {'Leave': 'Odejdz',
                                                                                    'Not now': 'Nie teraz'},
 'com.fs.starfarer.api.impl.campaign.PlanetInteractionDialogPluginImpl': {'Leave': 'Odejdz'},
 'com.fs.starfarer.api.impl.campaign.procgen.PlayerFleetGenPluginImpl': {'Leave': 'Odejdz'},
 'com.fs.starfarer.api.impl.campaign.intel.bar.events.LuddicPathBaseBarEvent': {'Continue': 'Kontynuuj'}}

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
 old=rows(obf/'TLUMACZENIA_OBF_10126.csv');assert len(old)==3380
 previous={(r['source_class'],r['english_literal']) for r in old};assert len(previous)==len(old)
 extra=[]
 for cl,mapping in OBF.items():
  for en,pl in mapping.items():
   assert en!=pl and en.isascii() and pl.isascii() and (cl,en) not in previous
   assert en.count('\n')==pl.count('\n')
   assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' ')
   extra.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 assert len(extra)==41 and len(OBF)==7
 out=obf/'TLUMACZENIA_OBF_10127.csv';assert not out.exists()
 with out.open('w',encoding='utf8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
  writer.writeheader();writer.writerows(old+extra)
 p=obf/'main.go';s=p.read_text('utf8')
 s=one(s,'TLUMACZENIA_OBF_10125.csv TLUMACZENIA_OBF_10126.csv','TLUMACZENIA_OBF_10125.csv TLUMACZENIA_OBF_10126.csv TLUMACZENIA_OBF_10127.csv')
 s=one(s,'const currentPatchState = "patched 10126"','const currentPatchState = "patched 10127"')
 s=one(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"'+OLD_OBF_SHA+'": "10126",')
 s=one(s,'loadTranslations("TLUMACZENIA_OBF_10126.csv")','loadTranslations("TLUMACZENIA_OBF_10127.csv")')
 s=one(s,'state == currentPatchState || state == "patched 10125"','state == currentPatchState || state == "patched 10126" || state == "patched 10125"')
 s=one(s,'OBF 1.0.26 | stan:','OBF 1.0.27 | stan:')
 s=one(s,'1.0.26: Lokalizacja tekstow OBF','1.0.27: Lokalizacja tekstow OBF')
 s=one(s,'0.9.99-1.0.26; odmowa modyfikacji','0.9.99-1.0.27; odmowa modyfikacji')
 p.write_text(s,'utf8')
 p=obf/'main_test.go';p.write_text(one(p.read_text('utf8'),'alreadyThisRelease("patched 10126")','alreadyThisRelease("patched 10127")'),'utf8')
 p=obf/'mapping_10126_test.go';p.write_text(one(p.read_text('utf8'),'!alreadyThisRelease("patched 10126") || alreadyThisRelease("patched 10125")','alreadyThisRelease("patched 10126") || alreadyThisRelease("patched 10125")'),'utf8')
 p=obf/'mapping_10127_test.go';assert not p.exists()
 p.write_text('''package main
import "testing"
func TestOBF10127TradingAndBattleMenus(t *testing.T) {
 m,e:=loadTranslations("TLUMACZENIA_OBF_10127.csv")
 if e!=nil {t.Fatal(e)}
 cases:=map[string]map[string]string{
  "com/fs/starfarer/campaign/ui/trade/new.class":{"Defense":"Obrona","Maneuverability":"Manewrowosc"},
  "com/fs/starfarer/ui/impl/oO0O.class":{"Allies":"Sojusznicy","Opponents":"Przeciwnicy"},
  "com/fs/starfarer/ui/impl/CargoTooltipFactory$3.class":{"Deficit":"Niedobor","Excess":"Nadwyzka"},
 }
 for cl,values:=range cases {for en,pl:=range values {if m[cl][en]!=pl {t.Fatalf("%s %q: %q != %q",cl,en,m[cl][en],pl)}}}
 if knownPreviousOBFHashes["a475ef535590b79da74d425f9e3f7566c85bed163e4a3795e88a593b7f69f42a"]!="10126" {t.Fatal("Missing 1.0.26 upgrade state")}
 if !alreadyThisRelease("patched 10127") || alreadyThisRelease("patched 10126") {t.Fatal("Wrong current state")}
}
''','utf8')
 oldapip=api/'translations/TLUMACZENIA_JAR_1026.csv';oldapi=rows(oldapip);assert len(oldapi)==5150
 known_api={(r['source_class'],r['english_literal']) for r in oldapi}
 extra_api=[]
 for cl,values in API.items():
  for en,pl in values.items():
   assert en!=pl and en.isascii() and pl.isascii() and (cl,en) not in known_api
   assert en.count('\n')==pl.count('\n')
   assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' ')
   extra_api.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 assert len(extra_api)==30 and len(API)==12
 newapi=api/'translations/TLUMACZENIA_JAR_1027.csv';assert not newapi.exists()
 with newapi.open('w',encoding='utf8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
  writer.writeheader();writer.writerows(oldapi+extra_api)
 p=api/'main.go';s=p.read_text('utf8')
 s=one(s,'const version = "1026"','const version = "1027"')
 s=one(s,'const exeVersion = "1.0.26"','const exeVersion = "1.0.27"')
 s=one(s,'"1025", version}', '"1025", "1026", version}')
 s=one(s,'PL ASCII patch up to 1.0.26','PL ASCII patch up to 1.0.27')
 s=one(s,'const expectedOBFPatched10126 = "'+OLD_OBF_SHA+'"',
       'const expectedOBFPatched10126 = "'+OLD_OBF_SHA+'"\nconst expectedOBFPatched10127 = "'+NEW_OBF_SHA+'"')
 s=one(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10126',
       'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10127 && hash(obf) != expectedOBFPatched10126')
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';p.write_text(one(p.read_text('utf8'),'const edition = "1.0.26"','const edition = "1.0.27"'),'utf8')
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
 assert meta['version']=='1.0.26'
 meta['version']='1.0.27';meta['description']=one(meta['description'],'1.0.26','1.0.27')
 p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
 s=one(s,'STARSECTOR PL ASCII 1.0.26','STARSECTOR PL ASCII 1.0.27')
 s+='\nUzupelniono nazwy klas okretow, ekranu walki, zdobywania lupow i dialogow flot.\n'
 p.write_text(s,'utf8')
 print('1.0.27: OBF 3380+41=3421, API 5150+30=5180; data unchanged')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 args=p.parse_args();main(args.worktree)