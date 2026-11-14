#!/usr/bin/env python3
"""Strict 1.0.60 API-map delta verification; game data and Java logic untouched."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1054 import readmap,encode,once
from apply_1060 import TRADE,PROCURE,OLD,NEW,ADDITIONS,REPAIRS,BASE_SHA,STATUS,EXPECTED_ROWS,RELEASE_SUFFIX,build,sha
from verify_1059 import DATA_SHA,RULES_SHA,GO_SHA as PREV_GO_SHA

NEW_SHA='963634daecdbd86e007091f90788367d826ade750d4b16bf335dd88ce439b724'
NEW_GO_SHA='e606928e67e9a509fc026583b15513a09d2e6d588a2d592d1a680c1d26031932'

def composed_texts(mapping:dict[tuple[str,str],str]):
 def v(cls,eng):return mapping[(cls,eng)]
 goods=[v(TRADE,'goods'),v(TRADE,'materiel'),v(TRADE,'goods and materiel')]
 if goods!=['towary','materialy','towary i materialy']:
  raise ValueError('Wrong nominative cargo categories')
 prefixes=[v(TRADE,x) for x in [
  "It's noteworthy because it's carrying a large quantity of ",
  "It's noteworthy because it's carrying a large quantity of valuable ",
  "It's noteworthy because it's carrying valuable "]]
 rendered=[]
 for i,prefix in enumerate(prefixes):
  for name in goods:
   text=prefix+name+'.'
   if not text.isascii() or any(fault in text for fault in ('duza ilosc towary','duza ilosc cennych materialy','duza ilosc cennych towary')):
    raise ValueError(('Untranslated/incorrect cargo quantity assembly',i,name,text))
   if i==0 and not text.startswith('To warte uwagi: flota przewozi znaczne ilosci ladunku. Rodzaj: '):
    raise ValueError('Large-cargo branch did not preserve grammatical case')
   if i==1 and not text.startswith('To warte uwagi: flota przewozi znaczne ilosci cennego ladunku. Rodzaj: '):
    raise ValueError('Large valuable-cargo branch did not preserve grammatical case')
   if i==2 and not text.startswith('To warte uwagi, bo przewozi cenne '):
    raise ValueError('Valuable-cargo branch invalid')
   rendered.append(text)
 route_cases=[('Jangala','Chicomoztoc'),('Kazeron','Eochu Bres'),('Tartessus','Asharu'),('Nowa Ziemia','Stacja Delta')]
 for source,destination in route_cases:
  out=v(TRADE,'From ')+source+v(TRADE,' to ')+destination
  if out!=f'Trasa: {source}, cel: {destination}':raise ValueError('Grammar depends on proper-name declension')
 for faction in ['Hegemonia','Liga Perseanska','Tri-Tachyon']:
  out=v(PROCURE,'Faction: ')+faction
  if out!=f'Frakcja: {faction}':raise ValueError('Untranslated faction tooltip label')
 return {'cargo_variants':len(rendered),'route_variants':len(route_cases),'faction_variants':3,'total':len(rendered)+len(route_cases)+3}

def check(root:Path)->dict:
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';trans=api/'translations'
 old=(trans/OLD).read_bytes();new=(trans/NEW).read_bytes()
 if (sha(old),sha(new))!=(BASE_SHA,NEW_SHA):raise ValueError('Unexpected v1.0.59 or v1.0.60 map SHA')
 previous=readmap(trans/OLD);rows=readmap(trans/NEW)
 expected=build(previous)
 if encode(expected)!=new or rows!=expected or len(rows)!=EXPECTED_ROWS:
  raise ValueError('Unapproved API mappings or CSV serialization')
 keys={(x['source_class'],x['english_literal']):x for x in rows}
 for key,pl in ADDITIONS.items():
  if keys[key]['polish_ascii_draft']!=pl or keys[key]['status']!=STATUS:raise ValueError(('Missing new translation',key))
 for key,(_,pl) in REPAIRS.items():
  if keys[key]['polish_ascii_draft']!=pl or keys[key]['status']!=STATUS:raise ValueError(('Missing repaired translation',key))
 if ('com.fs.starfarer.api.impl.campaign.intel.misc.TradeFleetDepartureIntel','Smuggling') in keys:
  raise ValueError('Technical category tag must not be mapped')
 if (PROCURE,'Trade') in keys:raise ValueError('Trade tag is an internal category')
 renders=composed_texts({k:r['polish_ascii_draft'] for k,r in keys.items()})
 main=(api/'main.go').read_text('utf8')
 if sha(main.encode())!=NEW_GO_SHA:raise ValueError('Unexpected Go code')
 for a,b in reversed([
  ('const version = "1059"','const version = "1060"'),
  ('const exeVersion = "1.0.59"','const exeVersion = "1.0.60"'),
  ('"1058", version}','"1058", "1059", version}'),
  ('PL ASCII patch up to 1.0.59','PL ASCII patch up to 1.0.60'),
 ]):main=once(main,b,a)
 if sha(main.encode())!=PREV_GO_SHA:raise ValueError('Non-version executable Go code changed')
 if 'const edition = "1.0.60"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer version not advanced')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if (meta.get('version'),meta.get('gameVersion'),len(meta.get('replace',[])))!=('1.0.60','0.98a-RC8',41):
  raise ValueError('Mod metadata changed incorrectly')
 guide=(root/'mod/CZYTAJ.txt').read_text('utf8')
 if not guide.startswith('STARSECTOR PL ASCII 1.0.60') or not guide.endswith(RELEASE_SUFFIX):
  raise ValueError('Wrong release documentation')
 data=root/'mod/data';files=sorted(x for x in data.rglob('*') if x.is_file())
 digest=sha('\n'.join(f'{p.relative_to(data).as_posix()}:{sha(p.read_bytes())}' for p in files).encode())
 if len(files)!=870 or digest!=DATA_SHA or sha((data/'campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError('Game data or dialogue rows have been altered')
 return {'release':'1.0.60','old_api_map_rows':len(previous),'new_api_map_rows':len(rows),
         'added_literals':len(ADDITIONS),'corrected_literals':len(REPAIRS),
         'rendered_combinations':renders['total'],'render_details':renders,
         'unchanged_data_files':len(files),'unchanged_rules_sha256':RULES_SHA,
         'mapping_sha256':NEW_SHA,'changed_java_classes_expected':2,
         'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(check(a.worktree),indent=2))
