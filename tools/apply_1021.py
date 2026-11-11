#!/usr/bin/env python3
"""Apply reviewed 1.0.21 translations and structural data corrections over 1.0.20.

OBF two visible UI labels; API one visible table header; three data files
correct the consistent Polish name for Persean League and Polish case.
No Java bytecode/identifier edits, no proprietary JARs distributed.
"""
import argparse,csv,json,shutil
from pathlib import Path
OBF={'com.fs.starfarer.ui.impl.oO0O':{
 'Show advanced options >>>':'Pokaz opcje zaawansowane >>>',
 '<<< Hide advanced options':'<<< Ukryj opcje zaawansowane',
}}
API={'com.fs.starfarer.api.impl.hullmods.ConvertedHangar':{
 'Wing':'Eskadra',
}}
OBF_SHA_1021='cfcf4860d7b451074e6285488f4bf24f91d2dd683aad95ef11ce344894cb84be'  # Verified on original JAR 0.98a-RC8.
STATUS='VERIFIED_VISIBLE_UI_1021'

def exact(data,old,new):
 assert data.count(old)==1,(old,data.count(old))
 return data.replace(old,new)

def update_map(src,dst,translations,old_expected):
 assert src.is_file() and not dst.exists()
 with src.open(encoding='utf8',newline='') as f:
  reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 assert len(rows)==old_expected,(src,len(rows),old_expected)
 assert fields==['source_class','english_literal','polish_ascii_draft','status']
 for cl,items in translations.items():
  for en,pl in items.items():
   assert en.isascii() and pl.isascii(),(en,pl)
   assert (cl,en) not in {(r['source_class'],r['english_literal']) for r in rows}
   rows.append({'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
 with dst.open('w',encoding='utf8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\r\n');writer.writeheader();writer.writerows(rows)
 return len(rows)

def main(root):
 assert (root/'mod/mod_info.json').is_file()
 obfdir=root/'buildtools/NARZEDZIA_OBF'
 apidir=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 obfrows=update_map(obfdir/'TLUMACZENIA_OBF_10118.csv',obfdir/'TLUMACZENIA_OBF_10121.csv',OBF,3142)
 apirows=update_map(apidir/'translations/TLUMACZENIA_JAR_1020.csv',apidir/'translations/TLUMACZENIA_JAR_1021.csv',API,5107)
 assert (obfrows,apirows)==(3144,5108)
 p=obfdir/'main.go';s=p.read_text('utf8')
 s=exact(s,'TLUMACZENIA_OBF_10117.csv TLUMACZENIA_OBF_10118.csv','TLUMACZENIA_OBF_10117.csv TLUMACZENIA_OBF_10118.csv TLUMACZENIA_OBF_10121.csv')
 s=exact(s,'const currentPatchState = "patched 10118"','const currentPatchState = "patched 10121"')
 s=exact(s,'var knownPreviousOBFHashes = map[string]string{',
         'var knownPreviousOBFHashes = map[string]string{\n\t"c95b45715e4d7c1b982d154acdc6776a3cf60756e83eefb00ea526a96c5a6c92": "10118",')
 s=exact(s,'loadTranslations("TLUMACZENIA_OBF_10118.csv")','loadTranslations("TLUMACZENIA_OBF_10121.csv")')
 s=exact(s,'state == currentPatchState || state == "patched 10117"','state == currentPatchState || state == "patched 10118" || state == "patched 10117"')
 s=exact(s,'OBF 1.0.18 | stan:', 'OBF 1.0.21 | stan:')
 s=exact(s,'1.0.18: Lokalizacja tekstow OBF','1.0.21: Lokalizacja tekstow OBF')
 s=exact(s,'0.9.99-1.0.18; odmowa modyfikacji','0.9.99-1.0.21; odmowa modyfikacji')
 p.write_text(s,'utf8')
 # Retain old mapping test but test version detection against the current 10121 state.
 p=obfdir/'main_test.go';s=p.read_text('utf8')
 s=exact(s,'alreadyThisRelease("patched 10118")','alreadyThisRelease("patched 10121")')
 s=exact(s,'[]string{"original", "patched 10117"','[]string{"original", "patched 10118", "patched 10117"')
 p.write_text(s,'utf8')
 p=obfdir/'mapping_10118_test.go';s=p.read_text('utf8')
 s=exact(s,'!alreadyThisRelease("patched 10118") || alreadyThisRelease("patched 10117")',
            'alreadyThisRelease("patched 10118") || alreadyThisRelease("patched 10117")')
 p.write_text(s,'utf8')
 p=obfdir/'mapping_10121_test.go';assert not p.exists()
 p.write_text('''package main
import "testing"
func TestOBF10121AdvancedOptionsUI(t *testing.T) {
 m,err:=loadTranslations("TLUMACZENIA_OBF_10121.csv")
 if err!=nil {t.Fatal(err)}
 if len(m)!=533 {t.Fatalf("expected 533 classes, got %d",len(m))}
 cl:=m["com/fs/starfarer/ui/impl/oO0O.class"]
 if cl["Show advanced options >>>"]!="Pokaz opcje zaawansowane >>>" || cl["<<< Hide advanced options"]!="<<< Ukryj opcje zaawansowane" {t.Fatal("UI labels missing")}
 if knownPreviousOBFHashes["c95b45715e4d7c1b982d154acdc6776a3cf60756e83eefb00ea526a96c5a6c92"]!="10118" {t.Fatal("previous OBF 10118 not supported")}
 if !alreadyThisRelease("patched 10121") || alreadyThisRelease("patched 10118") {t.Fatal("incorrect version detection")}
}
''',encoding='utf8')
 p=apidir/'main.go';s=p.read_text('utf8')
 s=exact(s,'const version = "1020"','const version = "1021"')
 s=exact(s,'const exeVersion = "1.0.20"','const exeVersion = "1.0.21"')
 s=exact(s,'"1018", "1019", version}', '"1018", "1019", "1020", version}')
 s=exact(s,'PL ASCII patch up to 1.0.20','PL ASCII patch up to 1.0.21')
 s=exact(s,'const expectedOBFPatched10118 = "c95b45715e4d7c1b982d154acdc6776a3cf60756e83eefb00ea526a96c5a6c92"',
         'const expectedOBFPatched10118 = "c95b45715e4d7c1b982d154acdc6776a3cf60756e83eefb00ea526a96c5a6c92"\nconst expectedOBFPatched10121 = "'+OBF_SHA_1021+'"')
 s=exact(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10118',
         'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10121 && hash(obf) != expectedOBFPatched10118')
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=p.read_text('utf8');s=exact(s,'const edition = "1.0.20"','const edition = "1.0.21"');p.write_text(s,'utf8')
 edits={
  'missions/coralnebula/MissionDefinition.java': [('Ligi Perseusza','Ligi Perseanskiej')],
  'missions/coralnebula/mission_text.txt': [('Ligi Perseusza','Ligi Perseanskiej'),('zaopatrzenie Rycerze Ludda','zaopatrzenie Rycerzy Ludda')],
  'characters/skills/skill_data.csv': [('Akt zalozycielski Ligi Perseusza','Akt zalozycielski Ligi Perseanskiej')],
 }
 for name,fixes in edits.items():
  p=root/'mod/data'/name;s=p.read_bytes()
  for old,new in fixes:s=exact(s,old.encode('ascii'),new.encode('ascii'))
  p.write_bytes(s)
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
 assert meta['version']=='1.0.20';meta['version']='1.0.21'
 meta['description']=exact(meta['description'],'1.0.20','1.0.21')
 p.write_text(json.dumps(meta,indent=2,ensure_ascii=True)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
 s=exact(s,'STARSECTOR PL ASCII 1.0.20','STARSECTOR PL ASCII 1.0.21')
 s+='\nDodatkowe etykiety interfejsu, korekta nazwy Ligi Perseanskiej i odmiany nazwy Rycerzy Ludda.\n'
 p.write_text(s,'utf8')
 print('1.0.21: 2 OBF UI labels, 1 API table heading, 4 data text corrections; maps:',obfrows,apirows)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);main(p.parse_args().worktree)