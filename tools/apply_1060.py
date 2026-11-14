#!/usr/bin/env python3
"""1.0.60: original-JVM-scoped trade-route and procurement UI grammar fixes.

Never replace identical literals outside the two named classes. Technical IDs,
intel category tags, scripts, and other Java executable instructions are not edited.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once

OLD='TLUMACZENIA_JAR_1059.csv'
NEW='TLUMACZENIA_JAR_1060.csv'
BASE_SHA='cfa73e2eca4a7e957ec68c72551a7f87d1de447f5cf8c2b735e8e7bb2bbc5b67'
TRADE='com.fs.starfarer.api.impl.campaign.intel.misc.TradeFleetDepartureIntel'
PROCURE='com.fs.starfarer.api.impl.campaign.intel.ProcurementMissionIntel'
STATUS='VERIFIED_ORIGINAL_JVM_INTEL_UI_1060_OFFLINE_PENDING_WINDOWS'
ADDITIONS={
 (TRADE,'From '):'Trasa: ',
 (TRADE,' to '):', cel: ',
 (TRADE,'goods'):'towary',
 (TRADE,'materiel'):'materialy',
 (PROCURE,'Faction: '):'Frakcja: ',
}
# The output of getWhat() is nominative ('towary', 'materialy', or both), and
# may be appended to three different sentences. The two old quantity cases
# were grammatically invalid because they required a genitive phrase.
REPAIRS={
 (TRADE,"It's noteworthy because it's carrying a large quantity of "):(
  'To warte uwagi, bo przewozi duza ilosc ',
  'To warte uwagi: flota przewozi znaczne ilosci ladunku. Rodzaj: '),
 (TRADE,"It's noteworthy because it's carrying a large quantity of valuable "):(
  'To warte uwagi, bo przewozi duza ilosc cennych ',
  'To warte uwagi: flota przewozi znaczne ilosci cennego ladunku. Rodzaj: '),
}
RELEASE_SUFFIX=('\nNaprawiono opis trasy floty handlowej, dopasowanie nazw ladunku do '
                'opisu jego ilosci i etykiete frakcji kontraktu dostawy. '
                'Dane, identyfikatory techniczne i logika gry sa nietkniete.\n')
EXPECTED_ROWS=5309

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def build(base:list[dict])->list[dict]:
 if len(base)!=5304 or len({(r['source_class'],r['english_literal']) for r in base})!=5304:
  raise ValueError('Unexpected 1.0.59 API map cardinality')
 existing={(r['source_class'],r['english_literal']) for r in base}
 if set(ADDITIONS)&existing:raise ValueError('New mapping key already exists')
 if not set(REPAIRS)<=existing:raise ValueError('Repaired key missing')
 out=[];seen=set()
 for row in base:
  item=dict(row);key=(item['source_class'],item['english_literal'])
  if key in REPAIRS:
   old,new=REPAIRS[key]
   if item['polish_ascii_draft']!=old or item['status']!='OPTIONAL_PATCHER_NOT_GAME_TESTED':
    raise ValueError(('Previously translated text or status changed',key))
   if any(old.count(token)!=new.count(token) for token in ('%s','%d','%f','\n','\r')):
    raise ValueError(('Format tokens modified',key))
   item['polish_ascii_draft']=new;item['status']=STATUS;seen.add(key)
  out.append(item)
 if seen!=set(REPAIRS):raise ValueError('Some repairs were not applied')
 for (cls,eng),pl in ADDITIONS.items():
  if not eng.isascii() or not pl.isascii() or '\n' in pl or '\r' in pl or eng.count('%s')!=pl.count('%s'):
   raise ValueError(('Invalid ASCII or formatting',cls,eng))
  out.append({'source_class':cls,'english_literal':eng,'polish_ascii_draft':pl,'status':STATUS})
 if len(out)!=EXPECTED_ROWS or len({(r['source_class'],r['english_literal']) for r in out})!=EXPECTED_ROWS:
  raise ValueError('Duplicate mapping after upgrade')
 return out

def apply(root:Path)->dict:
 root=Path(root)
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';translations=api/'translations'
 source=translations/OLD;target=translations/NEW
 if target.exists() or sha(source.read_bytes())!=BASE_SHA:
  raise ValueError('This overlay requires precisely the 1.0.59 API mapping')
 prev=readmap(source)
 if encode(prev)!=source.read_bytes():raise ValueError('Unexpected CSV serialization of API mapping')
 new=encode(build(prev))
 main=api/'main.go';s=main.read_text('utf8')
 for old,replacement in [
  ('const version = "1059"','const version = "1060"'),
  ('const exeVersion = "1.0.59"','const exeVersion = "1.0.60"'),
  ('"1058", version}','"1058", "1059", version}'),
  ('PL ASCII patch up to 1.0.59','PL ASCII patch up to 1.0.60'),
 ]:s=once(s,old,replacement)
 installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 new_installer=once(installer.read_text('utf8'),'const edition = "1.0.59"','const edition = "1.0.60"')
 modinfo=root/'mod/mod_info.json';d=json.loads(modinfo.read_text('utf8'))
 if (d['version'],d['gameVersion'])!=('1.0.59','0.98a-RC8'):
  raise ValueError('Mod metadata is not the 1.0.59 baseline')
 d['version']='1.0.60';d['description']=once(d['description'],'1.0.59','1.0.60')
 readme=root/'mod/CZYTAJ.txt';text=once(readme.read_text('utf8'),'STARSECTOR PL ASCII 1.0.59','STARSECTOR PL ASCII 1.0.60')+RELEASE_SUFFIX
 # Commit changes only after all inputs and replacement anchors are verified.
 target.write_bytes(new)
 main.write_text(s,encoding='utf8');installer.write_text(new_installer,encoding='utf8')
 modinfo.write_text(json.dumps(d,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 readme.write_text(text,encoding='utf8')
 return {'release':'1.0.60','new_api_literals':len(ADDITIONS),'repaired_api_literals':len(REPAIRS),
         'total_api_map_rows':EXPECTED_ROWS,'new_map_sha256':sha(new),
         'affected_java_classes':len({x[0] for x in ADDITIONS}|{x[0] for x in REPAIRS}),
         'game_data_files_changed':0,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('worktree',type=Path)
 args=parser.parse_args();print(json.dumps(apply(args.worktree),indent=2))
