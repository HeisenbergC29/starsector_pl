#!/usr/bin/env python3
"""1.0.66: JVM-scoped simulator, colony industry and Galatia tutorial UI.

Use only original Java source-class + CONSTANT_String keys. Never translate ids,
category keys, game scripts or variable identifiers; all modifications are text.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once

VERSION='1.0.66';OLD='TLUMACZENIA_JAR_1065.csv';NEW='TLUMACZENIA_JAR_1066.csv'
BASE_SHA='4d83faa23a64a85a094c325d6f7f53e7d8944da7919eb497eb20be480aba2163'
SIM='com.fs.starfarer.api.impl.SimulatorPluginImpl'
IND='com.fs.starfarer.api.impl.campaign.econ.impl.BaseIndustry'
TUT='com.fs.starfarer.api.impl.campaign.tutorial.TutorialMissionIntel'
CLASSES={SIM:74,IND:70,TUT:48}
DRAFT={'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
STATUS='REVIEWED_ORIGINAL_JVM_1066_OFFLINE_GAME_TEST_AFTER_1_1'
ADDITIONS={
 (SIM,'Aggression / behavior'):'Agresja i zachowanie',
 (SIM,'DevMode stuff'):'Opcje deweloperskie',
 (IND,'day'):'dzien',
 (IND,'days'):'dni',
 (IND,'unit'):'jedn',
 (IND,'units'):'jedn',
 (IND,' left'):'',
 (IND,'%s and %s '):'Koszt: %s; czas: %s ',
 (IND,' at '):' — kolonia: '.replace(' — ',' - '),
 (TUT,'Completed'):'Ukonczono',
 (TUT,'Go Dark'):'trybu skrytego',
 (TUT,'"Storage"'):'"Magazyn"',
 (TUT,'"autofit"'):'"automatyczne dopasowanie"',
}
CORRECTIONS={
 (IND,'Requires %s more '):'Pozostaly czas: %s ',
 (IND,' to upgrade. You have %s.'):'. Dostepne srodki: %s.',
 (IND,' to build. You have %s.'):'. Dostepne srodki: %s.',
 (IND,' to finish building.'):'.',
 (IND,'Disrupted: '):'Zaklocenia, pozostalo: ',
 (IND,'Upgrading: '):'Ulepszanie, pozostalo: ',
 (IND,'Building: '):'Budowa, pozostalo: ',
 (TUT,'Active Sensor Burst'):'aktywnego impulsu czujnikow',
 (TUT,'Emergency Burn'):'awaryjnego dopalacza',
}
EXPECTED_ROWS=5327
RELEASE_SUFFIX=(
 '\nWersja 1.0.66: uzupelniono ustawienia symulatora, czasy budowy i opisy '
 'produkcji kolonii oraz teksty samouczka Galatii. Przypadki dzien/dni, '
 'jedn., koszty i dynamiczne nazwy sprawdzono na oryginalnym bajtkodzie. '
 'Nie zmieniono technicznych identyfikatorow. Testy w uruchomionej grze '
 'wykonywane beda dopiero po wydaniu 1.1.\n'
)

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def fp(r:dict)->str:return sha('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode())

def build(rows:list[dict])->tuple[list[dict],dict]:
 if len(rows)!=5314 or len({(r['source_class'],r['english_literal']) for r in rows})!=5314 or sha(encode(rows))!=BASE_SHA:
  raise ValueError('Not the byte-identical v1.0.65 API map')
 for cl,n in CLASSES.items():
  if sum(r['source_class']==cl for r in rows)!=n:raise ValueError(('Source class cardinality',cl))
 if len(ADDITIONS)!=13 or len(CORRECTIONS)!=9:raise ValueError('Unapproved mapping delta size')
 keys={(r['source_class'],r['english_literal']) for r in rows}
 if keys.intersection(ADDITIONS) or set(CORRECTIONS)-keys:raise ValueError('Translation keys missing or already translated')
 out=[];reviewed=[];repaired=[]
 for row in rows:
  r=dict(row);key=(r['source_class'],r['english_literal'])
  if key in CORRECTIONS:
   text=CORRECTIONS[key]
   if text==row['polish_ascii_draft'] or not text.isascii():raise ValueError(('Not a translation',key))
   for tok in ['%s','%d','%f','%NAME%','\n','\r','\t']:
    if text.count(tok)!=row['polish_ascii_draft'].count(tok):
     raise ValueError(('Changed interpolation token',key,tok))
   r['polish_ascii_draft']=text
   repaired.append({'source_class':key[0],'english_literal':key[1],'old':row['polish_ascii_draft'],'new':text,'prior_status':row['status']})
  if row['source_class'] in CLASSES and row['status'] in DRAFT:
   r['status']=STATUS
   reviewed.append({'source_class':r['source_class'],'english_literal':r['english_literal'],
    'english_key_sha256':sha(r['english_literal'].encode()),'old_status':row['status'],
    'old_row_sha256':fp(row),'row_sha256':fp(r),'old_draft':row['polish_ascii_draft'],
    'new_draft':r['polish_ascii_draft'],'evidence':'original_JVM_Simulator_BaseIndustry_Tutorial_1066',
    'review_status':'original_JVM_scoped_semantic_review_offline_game_tests_after_1_1'})
  out.append(r)
 for (cl,en),pl in ADDITIONS.items():
  if not (en.isascii() and pl.isascii()) or any(en.count(s)!=pl.count(s) for s in ('%s','%d','%f','\n','\r')):
   raise ValueError(('New mapping includes unsafe bytes/placeholders',cl,en))
  out.append({'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
 if len(out)!=EXPECTED_ROWS or len({(r['source_class'],r['english_literal']) for r in out})!=EXPECTED_ROWS:
  raise ValueError('New map cardinality invalid')
 actual={cl:sum(r['source_class']==cl and r['old_status'] in DRAFT for r in reviewed) for cl in CLASSES}
 if actual!={SIM:58,IND:56,TUT:47} or len(reviewed)!=161 or len(repaired)!=9:
  raise ValueError(('Unapproved source historic inventory',actual,len(repaired)))
 return out,{'reviewed_status_rows':reviewed,'repaired':repaired,'new_literals':list(ADDITIONS)}

def apply(root:Path)->dict:
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';tr=api/'translations'
 source=tr/OLD;dest=tr/NEW
 if dest.exists() or sha(source.read_bytes())!=BASE_SHA:raise ValueError('Wrong baseline/reapply')
 original=readmap(source)
 if encode(original)!=source.read_bytes():raise ValueError('Unexpected CSV serialization')
 updated,meta=build(original);payload=encode(updated)
 go=api/'main.go';code=go.read_text('utf8')
 for before,after in [
  ('const version = "1065"','const version = "1066"'),
  ('const exeVersion = "1.0.65"','const exeVersion = "1.0.66"'),
  ('"1064", version}','"1064", "1065", version}'),
  ('PL ASCII patch up to 1.0.65','PL ASCII patch up to 1.0.66')]:code=once(code,before,after)
 inst=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 installer=once(inst.read_text('utf8'),'const edition = "1.0.65"','const edition = "1.0.66"')
 info=root/'mod/mod_info.json';m=json.loads(info.read_text('utf8'))
 if (m.get('version'),m.get('gameVersion'))!=('1.0.65','0.98a-RC8'):
  raise ValueError('Unexpected game version or mod baseline')
 m['version']='1.0.66';m['description']=once(m['description'],'1.0.65','1.0.66')
 guide=root/'mod/CZYTAJ.txt'
 txt=once(guide.read_text('utf8'),'STARSECTOR PL ASCII 1.0.65','STARSECTOR PL ASCII 1.0.66')+RELEASE_SUFFIX
 dest.write_bytes(payload);go.write_text(code,'utf8');inst.write_text(installer,'utf8')
 info.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n',encoding='utf8');guide.write_text(txt,'utf8')
 return {'release':VERSION,'prior_map_rows':len(original),'new_map_rows':len(updated),
  'new_java_ui_literals':len(ADDITIONS),'corrected_java_fragments':len(CORRECTIONS),
  'historic_draft_rows_inspected':len(meta['reviewed_status_rows']),
  'new_map_sha256':sha(payload),'previous_map_sha256':BASE_SHA,
  'changed_game_data_files':0,'jvm_opcode_changes':0,'native_game_tests':'after_1_1_release'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(apply(p.parse_args().worktree),indent=2))
