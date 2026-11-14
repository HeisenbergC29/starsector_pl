#!/usr/bin/env python3
"""1.0.64: verify and translate Hegemony inspection and Luddic Path base intel.

Two exact class-scoped Java API string maps; preserve the category tokens used
by Set.add/Set.contains in original JVM. Do not rewrite JVM instructions.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once

INSPECTION='com.fs.starfarer.api.impl.campaign.intel.inspection.HegemonyInspectionIntel'
PATH_BASE='com.fs.starfarer.api.impl.campaign.intel.bases.LuddicPathBaseIntel'
CLASSES={INSPECTION:28,PATH_BASE:28}
DRAFT_COUNTS={INSPECTION:24,PATH_BASE:24}
OLD='TLUMACZENIA_JAR_1063.csv'
NEW='TLUMACZENIA_JAR_1064.csv'
DRAFT={'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
STATUS='REVIEWED_ORIGINAL_JVM_INSPECTION_PATHBASE_1064_PENDING_WINDOWS'
REPAIRS={
 (INSPECTION,'Colony threats'):'Colony threats',
 (INSPECTION,'The authorities at '):'Decyzja wladz kolonii: ',
 (INSPECTION,' will comply with the inspection. '):' - zgoda na inspekcje. ',
 (INSPECTION,'Operations at %s disrupted'):'Zaklocono dzialalnosc: %s',
 (INSPECTION,' forces arrive in-system and encounter resistance'):': oddzialy dotarly do ukladu i napotkaly opor',
 (PATH_BASE,'Colony threats'):'Colony threats',
 (PATH_BASE,'Fleet log'):'Fleet log',
 (PATH_BASE,'The base serves to provide material support to active Pather cells on nearby colonies, enabling them '):
 'Baza zapewnia wsparcie materialne aktywnym komorkom Sciezki Ludda na pobliskich koloniach, umozliwiajac im ',
 (PATH_BASE,'You do not know of any active pather cells this base might be providing support to.'):
 'Nie wiadomo, czy baza wspiera jakiekolwiek aktywne komorki Sciezki Ludda.',
}
TECHNICAL={(INSPECTION,'Colony threats'),(PATH_BASE,'Colony threats'),(PATH_BASE,'Fleet log')}
BASE_SHA='5443294fa1cdf96b21fb7bba3e5a92b96f8f1b6cec6807203dd7e3e74e1d58fc'
RELEASE_SUFFIX=('\nAudyt inspekcji Hegemonii i baz Sciezki Ludda: 48 historycznych wpisow API '
 'sprawdzono w oryginalnym JVM; poprawiono 9 fragmentow. Zachowano trzy '
 'angielskie klucze techniczne kategorii Colony threats i Fleet log. '
 'Dynamiczne getDisplayNameHasOrHave oraz getDisplayNameIsOrAre pozostaja do osobnej analizy.\n')

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()
def fp(r:dict)->str:return sha('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode())

def build(rows:list[dict])->tuple[list[dict],dict]:
 if len(rows)!=5314 or len({(r['source_class'],r['english_literal']) for r in rows})!=5314:
  raise ValueError('Not the approved 5314-row source map')
 if sha(encode(rows))!=BASE_SHA:raise ValueError('Wrong version or modified original API map')
 for cl,total in CLASSES.items():
  cls=[r for r in rows if r['source_class']==cl]
  if len(cls)!=total or sum(r['status'] in DRAFT for r in cls)!=DRAFT_COUNTS[cl]:
   raise ValueError(('Class inventory or approved history mismatch',cl,len(cls)))
 if any((cl,lit) not in {(r['source_class'],r['english_literal']) for r in rows} for cl,lit in REPAIRS):
  raise ValueError('Required original literal is missing')
 if len(REPAIRS)!=9 or len(TECHNICAL)!=3:raise ValueError('Invalid approved edits')
 updated=[];review=[];changes=[]
 for old in rows:
  new=dict(old);key=(old['source_class'],old['english_literal'])
  if key in REPAIRS:
   val=REPAIRS[key]
   if old['status'] not in DRAFT or old['polish_ascii_draft']==val or not val.isascii():
    raise ValueError(('Unexpected repaired row',key))
   for marker in ('%s','%d','%f','\n','\r','\t'):
    if old['polish_ascii_draft'].count(marker)!=val.count(marker):raise ValueError(('Marker changed',key,marker))
   new['polish_ascii_draft']=val;changes.append(key)
  if old['source_class'] in CLASSES and old['status'] in DRAFT:
   new['status']=STATUS
   review.append({'source_class':old['source_class'],'english_literal':old['english_literal'],
    'english_key_sha256':sha(old['english_literal'].encode()),
    'old_status':old['status'],'old_draft':old['polish_ascii_draft'],
    'new_draft':new['polish_ascii_draft'],'old_row_sha256':fp(old),'row_sha256':fp(new),
    'evidence':'original_JVM_HegemonyInspection_and_LuddicPathBase_1064',
    'review_status':'original_JVM_semantic_review_offline_pending_native_Windows'})
  updated.append(new)
 if len(review)!=48 or len(changes)!=9 or set(changes)!=set(REPAIRS):raise ValueError('Reviewed delta incorrect')
 for k in TECHNICAL:
  row=next(r for r in updated if (r['source_class'],r['english_literal'])==k)
  if row['polish_ascii_draft']!=k[1]:raise ValueError(('Technical category changed',k))
 return updated,{'review':review,'repaired':changes}

def apply(worktree:Path)->dict:
 worktree=Path(worktree)
 api=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old=api/'translations'/OLD;dest=api/'translations'/NEW
 if dest.exists() or sha(old.read_bytes())!=BASE_SHA:raise ValueError('Wrong baseline/already applied')
 rows=readmap(old)
 if encode(rows)!=old.read_bytes():raise ValueError('API source map was reformatted')
 out,details=build(rows);data=encode(out)
 go=api/'main.go';source=go.read_text('utf8')
 for before,after in [
  ('const version = "1063"','const version = "1064"'),
  ('const exeVersion = "1.0.63"','const exeVersion = "1.0.64"'),
  ('"1062", version}','"1062", "1063", version}'),
  ('PL ASCII patch up to 1.0.63','PL ASCII patch up to 1.0.64')]:source=once(source,before,after)
 installer=worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go';ins=once(installer.read_text('utf8'),'const edition = "1.0.63"','const edition = "1.0.64"')
 manifest=worktree/'mod/mod_info.json';m=json.loads(manifest.read_text('utf8'))
 if (m.get('version'),m.get('gameVersion'))!=('1.0.63','0.98a-RC8'):raise ValueError('Incorrect mod baseline')
 m['version']='1.0.64';m['description']=once(m['description'],'1.0.63','1.0.64')
 guide=worktree/'mod/CZYTAJ.txt';readme=once(guide.read_text('utf8'),'STARSECTOR PL ASCII 1.0.63','STARSECTOR PL ASCII 1.0.64')+RELEASE_SUFFIX
 # All conditions checked before writing.
 dest.write_bytes(data);go.write_text(source,'utf8');installer.write_text(ins,'utf8')
 manifest.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n','utf8');guide.write_text(readme,'utf8')
 return {'release':'1.0.64','historic_api_new_reviews':48,'historic_api_total_reviewed':530,
  'corrected_fragments':len(details['repaired']),'technical_keys_preserved':3,
  'mapping_rows':len(out),'map_sha256':sha(data),'mod_data_changes':0,
  'new_jvm_executable_instruction_changes':0,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(apply(p.parse_args().worktree),indent=2))
