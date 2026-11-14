#!/usr/bin/env python3
"""v1.0.63: reviewed Luddic Path cells intel, with technical tags preserved.

Only one Java API class's source-string translations and version metadata change.
The substitutions are keyed by complete JVM source class + exact original literal.
Dynamic industry, location, and colony names are isolated after punctuation to avoid
forcing an impossible Polish case onto a player-defined name.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once

CLASS='com.fs.starfarer.api.impl.campaign.intel.bases.LuddicPathCellsIntel'
OLD='TLUMACZENIA_JAR_1062.csv';NEW='TLUMACZENIA_JAR_1063.csv'
BASE_SHA='1f85680ff856b858f2f4db342aa98754c085a35bec6e9d0538113a55f9471f01'
DRAFT={'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
STATUS='REVIEWED_ORIGINAL_JVM_LUDDIC_CELLS_1063_PENDING_WINDOWS'
REPAIRS={
 'Colony threats':'Colony threats', # Set.add() tag, not visible Polish UI text
 'Colony destroyed by planetbuster':'Kolonia zniszczona bronia planetobojcza',
 'If they succeed, the colony will effectively be destroyed.':' Jesli plan sie powiedzie, kolonia zostanie praktycznie zniszczona.',
 'The Pather base at the ':'Baza Sciezki Ludda (lokalizacja: ',
 ' is providing support to these cells.':') wspiera te komorki.',
 'The Pather cells have conducted a successful act of sabotage, disrupting ':'Komorki Sciezki Ludda przeprowadzily udany sabotaz. Cel: ',
 ' operations for %s ':'. Zaklocenie potrwa %s ',
 'An attempted act of sabotage against ':'Lokalne sluzby bezpieczenstwa udaremnily probe sabotazu. Cel: ',
 ' operations was averted by the local security forces.':'.',
 'The Pather cells have smuggled a planetbuster onto ':'Wyznawcy Sciezki Ludda przemycili bron planetobojcza. Cel: ',
 ' and detonated it. The colony has been effectively destroyed.':'. Nastepnie zdetonowali ladunek, praktycznie niszczac kolonie.',
 ', but the local security forces were able to locate and disarm it, thereby ':'. Lokalne sluzby bezpieczenstwa odnalazly i rozbroily ladunek, ',
 'There are indications that the Pather cells are preparing to sneak a planetbuster onto ':'Istnieja przeslanki, ze wyznawcy Sciezki Ludda planuja przemycic bron planetobojcza. Cel: ',
 ' operations disrupted for %s ':': zaklocenie dzialalnosci na %s ',
}
RELEASE_SUFFIX=('\nW raporcie o komorkach Sciezki Ludda poprawiono 14 fragmentow dotyczacych '
 'sabotażu, broni planetobojczej, statusu baz i odmiany nazw przemyslu. '
 'Przywrocono oryginalny techniczny klucz kategorii Colony threats; '
 '35 historycznych wpisow Java API sprawdzono w oryginalnym JVM. '
 'Dynamiczne angielskie on/at nadal wymaga osobnej poprawki poza mapa tekstow.\n')
# Game-facing mod is ASCII-only even if this source code is Unicode.
RELEASE_SUFFIX=RELEASE_SUFFIX.replace('ż','z')

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def fp(row:dict)->str:return sha('\0'.join(row[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode('utf8'))

def build(rows:list[dict])->tuple[list[dict],dict]:
 if len(rows)!=5314 or sha(encode(rows))!=BASE_SHA:
  raise ValueError('Wrong base API mapping version/hash')
 keys={(r['source_class'],r['english_literal']) for r in rows}
 if len(keys)!=5314:raise ValueError('Duplicate API literal keys')
 selected={r['english_literal']:r for r in rows if r['source_class']==CLASS}
 if len(selected)!=47 or any(k not in selected for k in REPAIRS):
  raise ValueError('LuddicPathCellsIntel source string inventory not as expected')
 if len(REPAIRS)!=14 or sum(r['status'] in DRAFT for r in selected.values())!=35:
  raise ValueError('Unexpected historical draft count')
 if any(selected[k]['status'] not in DRAFT or selected[k]['polish_ascii_draft']==v for k,v in REPAIRS.items()):
  raise ValueError('Repaired historical rows were altered or previously reviewed')
 result=[];reviews=[];edited=[]
 for old in rows:
  row=dict(old)
  if row['source_class']==CLASS:
   key=row['english_literal'];previous=row['polish_ascii_draft']
   if key in REPAIRS:
    new=REPAIRS[key]
    for marker in ('%s','%d','%f','\r','\n','\t'):
     if previous.count(marker)!=new.count(marker):raise ValueError(('Java formatting changed',key,marker))
    if not new.isascii():raise ValueError(('Non-ASCII translation',key))
    row['polish_ascii_draft']=new;edited.append(key)
   if row['status'] in DRAFT:
    reviews.append({'source_class':CLASS,'english_literal':key,'old_draft':previous,
     'old_status':old['status'],'new_draft':row['polish_ascii_draft'],
     'old_row_sha256':fp(old),'new_row_sha256':fp(row),
     'english_key_sha256':sha(key.encode('utf8'))})
    row['status']=STATUS
  result.append(row)
 if len(result)!=5314 or len(reviews)!=35 or len(edited)!=14 or set(edited)!=set(REPAIRS):
  raise ValueError('Unapproved translation count')
 return result,{'reviews':reviews,'repaired':edited}

def apply(root:Path)->dict:
 root=Path(root)
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';d=api/'translations'
 original=d/OLD;target=d/NEW
 if target.exists() or sha(original.read_bytes())!=BASE_SHA:raise ValueError('Not pristine 1.0.62 mapping')
 rows=readmap(original)
 if encode(rows)!=original.read_bytes():raise ValueError('Source map unexpectedly reserialized')
 updated,stats=build(rows);bytes_=encode(updated)
 file=api/'main.go';code=file.read_text('utf8')
 for a,b in [('const version = "1062"','const version = "1063"'),
   ('const exeVersion = "1.0.62"','const exeVersion = "1.0.63"'),
   ('"1061", version}','"1061", "1062", version}'),
   ('PL ASCII patch up to 1.0.62','PL ASCII patch up to 1.0.63')]:code=once(code,a,b)
 installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 ins=once(installer.read_text('utf8'),'const edition = "1.0.62"','const edition = "1.0.63"')
 info=root/'mod/mod_info.json';meta=json.loads(info.read_text('utf8'))
 if (meta.get('version'),meta.get('gameVersion'))!=('1.0.62','0.98a-RC8'):
  raise ValueError('Wrong game metadata baseline')
 meta['version']='1.0.63';meta['description']=once(meta['description'],'1.0.62','1.0.63')
 guide=root/'mod/CZYTAJ.txt';readme=once(guide.read_text('utf8'),'STARSECTOR PL ASCII 1.0.62','STARSECTOR PL ASCII 1.0.63')+RELEASE_SUFFIX
 # Mutate only after all constraints and expected edits pass.
 target.write_bytes(bytes_);file.write_text(code,encoding='utf8')
 installer.write_text(ins,encoding='utf8');info.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
 guide.write_text(readme,encoding='utf8')
 return {'release':'1.0.63','historical_api_reviewed_new':35,'existing_literals_corrected':14,
  'api_mapping_entries':5314,'map_sha256':sha(bytes_), 'game_data_changed':0,
  'new_executable_java_instructions':0,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(apply(p.parse_args().worktree),indent=2))
