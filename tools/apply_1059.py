#!/usr/bin/env python3
"""1.0.59: class-scoped original-JVM-verified monthly report tooltip translations.

Do not translate a shared token globally. All additions are constrained to the
single class, with assembly tests covering variable quantities/commodity names.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once

OLD='TLUMACZENIA_JAR_1058.csv'
NEW='TLUMACZENIA_JAR_1059.csv'
BASE_MAP_SHA='c45d1e8e33240b7716e94b9e5ca1f3ae7b74eb1314db38fb57f146b85b863848'
CLASS='com.fs.starfarer.api.impl.campaign.MonthlyReportNodeTooltipCreator'
STATUS='VERIFIED_ORIGINAL_JVM_MONTHLY_TOOLTIP_1059_PENDING_WINDOWS'
# These are CONSTANT_String literals used by addSectionHeading or StringBuilder;
# none are configuration keys or technical identifiers.
ADDITIONS={
 'Equipment':'Wyposazenie',
 'Ships':'Okrety',
 'Resources':'Zasoby',
 'unit':'',
 'units':'',
 ' of ':'',
}
CORRECTION=('Approximately %s ','Okolo %s ', 'Szacunkowa ilosc: %s jedn. Towar: ')
EXPECTED_ROWS=5304
RELEASE_SUFFIX=('\nPoprawiono angielskie naglowki raportu miesiecznego oraz opis ilosci towarow '
                '(6 nowych mapowan Java API i 1 korekta skladanego zdania). '
                'Identyfikatory techniczne, skrypty i zasady rozgrywki bez zmian.\n')

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def build(rows:list[dict])->list[dict]:
 if len(rows)!=5298 or len({(r['source_class'],r['english_literal']) for r in rows})!=5298:
  raise ValueError('Expected exactly 5298 unique entries in 1.0.58 API map')
 keys={(r['source_class'],r['english_literal']) for r in rows}
 if any((CLASS,key) in keys for key in ADDITIONS):raise ValueError('New monthly literals already mapped')
 out=[]; changed=0
 for row in rows:
  item=dict(row)
  if (item['source_class'],item['english_literal'])==(CLASS,CORRECTION[0]):
   if item['polish_ascii_draft']!=CORRECTION[1] or item['status']!='MANUAL_UI_LITERAL_1003':
    raise ValueError('Unexpected previous monthly quantity fragment')
   item['polish_ascii_draft']=CORRECTION[2]
   item['status']=STATUS
   changed+=1
  out.append(item)
 if changed!=1:raise ValueError('The original monthly template was not found exactly once')
 for en,pl in ADDITIONS.items():
  if not en.isascii() or not pl.isascii() or any(s in en+pl for s in ('\r','\n')):
   raise ValueError('Non-ASCII or multiline additions disallowed')
  out.append({'source_class':CLASS,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
 if len(out)!=EXPECTED_ROWS or len({(r['source_class'],r['english_literal']) for r in out})!=EXPECTED_ROWS:
  raise ValueError('Map cardinality invalid')
 return out

def apply(root:Path)->dict:
 root=Path(root)
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 src=api/'translations'/OLD;dst=api/'translations'/NEW
 if dst.exists() or sha(src.read_bytes())!=BASE_MAP_SHA:raise ValueError('Wrong baseline or already installed')
 rows=readmap(src)
 if encode(rows)!=src.read_bytes():raise ValueError('Unexpected map CSV serialization')
 encoded=encode(build(rows))
 code=api/'main.go';s=code.read_text(encoding='utf8')
 for a,b in [
  ('const version = "1058"','const version = "1059"'),
  ('const exeVersion = "1.0.58"','const exeVersion = "1.0.59"'),
  ('"1057", version}','"1057", "1058", version}'),
  ('PL ASCII patch up to 1.0.58','PL ASCII patch up to 1.0.59')]:s=once(s,a,b)
 installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 ins=once(installer.read_text(encoding='utf8'),'const edition = "1.0.58"','const edition = "1.0.59"')
 meta=root/'mod/mod_info.json';m=json.loads(meta.read_text(encoding='utf8'))
 if (m.get('version'),m.get('gameVersion'))!=('1.0.58','0.98a-RC8'):raise ValueError('Incorrect game/mod baseline')
 m['version']='1.0.59'
 m['description']=once(m['description'],'1.0.58','1.0.59')
 guide=root/'mod/CZYTAJ.txt'
 gd=once(guide.read_text(encoding='utf8'),'STARSECTOR PL ASCII 1.0.58','STARSECTOR PL ASCII 1.0.59')+RELEASE_SUFFIX
 # Commit mutations only after every precondition succeeded.
 dst.write_bytes(encoded);code.write_text(s,encoding='utf8')
 installer.write_text(ins,encoding='utf8')
 meta.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 guide.write_text(gd,encoding='utf8')
 return {'release':'1.0.59','original_entries':len(rows),'new_map_entries':len(build(rows)),
         'new_class_scoped_literals':len(ADDITIONS),'corrected_templates':1,
         'new_map_sha256':sha(encoded),'previous_map_sha256':BASE_MAP_SHA,
         'changed_data_texts':0,'new_JVM_executable_instruction_changes':0}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);args=p.parse_args()
 print(json.dumps(apply(args.worktree),indent=2))
