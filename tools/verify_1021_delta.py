#!/usr/bin/env python3
"""Check 1.0.21 approved new text-only translation delta without original JARs.

Does not claim full translation completeness or original data integrity;
the latter requires the separately provided commercial data archive.
"""
import argparse,csv,json
from pathlib import Path

OBF={'com.fs.starfarer.ui.impl.oO0O':{
 'Show advanced options >>>':'Pokaz opcje zaawansowane >>>',
 '<<< Hide advanced options':'<<< Ukryj opcje zaawansowane',}}
API={'com.fs.starfarer.api.impl.hullmods.ConvertedHangar':{'Wing':'Eskadra'}}
DATA={
 'missions/coralnebula/MissionDefinition.java': [('Ligi Perseusza','Ligi Perseanskiej')],
 'missions/coralnebula/mission_text.txt': [('Ligi Perseusza','Ligi Perseanskiej'),('zaopatrzenie Rycerze Ludda','zaopatrzenie Rycerzy Ludda')],
 'characters/skills/skill_data.csv': [('Akt zalozycielski Ligi Perseusza','Akt zalozycielski Ligi Perseanskiej')]}

def rows(p):
 with p.open(encoding='utf8',newline='') as f:
  reader=csv.DictReader(f)
  assert reader.fieldnames==['source_class','english_literal','polish_ascii_draft','status']
  return list(reader)

def assert_map(before,after,delta):
 original=rows(before);current=rows(after)
 assert current[:len(original)]==original,(before,'prior mapping changed')
 expected=[{'source_class':c,'english_literal':k,'polish_ascii_draft':v,'status':'VERIFIED_VISIBLE_UI_1021'} for c,items in delta.items() for k,v in items.items()]
 assert current[len(original):]==expected,(after,'unapproved map delta')
 assert all(x['polish_ascii_draft'].isascii() for x in expected)
 return len(current)

def main(root):
 obf=root/'buildtools/NARZEDZIA_OBF';api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 assert assert_map(obf/'TLUMACZENIA_OBF_10118.csv',obf/'TLUMACZENIA_OBF_10121.csv',OBF)==3144
 assert assert_map(api/'TLUMACZENIA_JAR_1020.csv',api/'TLUMACZENIA_JAR_1021.csv',API)==5108
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.21' and meta['gameVersion']=='0.98a-RC8'
 for name,pairs in DATA.items():
  raw=(root/'mod/data'/name).read_bytes()
  for before,after in pairs:
   assert after.encode('ascii') in raw and before.encode('ascii') not in raw,(name,before,after)
 p=(root/'buildtools/NARZEDZIA_OBF/main.go').read_text('utf8')
 assert 'loadTranslations("TLUMACZENIA_OBF_10121.csv")' in p
 assert 'const currentPatchState = "patched 10121"' in p
 p=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
 assert 'const version = "1021"' in p and 'const expectedOBFPatched10121' in p
 print('1.0.21 DELTA CHECK PASS: OBF +2, API +1, data 4 text replacements; previous CSVs intact')

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);main(a.parse_args().worktree)