#!/usr/bin/env python3
"""Fail-closed v1.0.64 source, translation, original-JVM and grammar verification."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1054 import readmap,encode,once
from apply_1064 import (INSPECTION,PATH_BASE,CLASSES,OLD,NEW,REPAIRS,TECHNICAL,
 BASE_SHA,RELEASE_SUFFIX,build,sha)
from build_review_1064 import check as review_check
NEW_MAP_SHA='080333ba3c5d89f79a27e83737be8eb940c21a10446901ae01de98ef735a7588'
PRIOR_GO_SHA='7261820a172e3a0fa7131cdad5c6d8ff825f5ae2485a0f7c09489a00ad32d292'
NEW_GO_SHA='255eac1601f041ad3f5858f25c952c38b6b7218b3e57c8cc58799a03b01e8c86'
REVIEW_SHA='13a485773ae15ac54fae7dd7ac42e548f3905abedbb1e31f38069ad8c847dd87'
JVM_SHA='290da975c883db82cca75a97b906823537d1fd8b15e0ddb0bc18184ba96794aa'
DATA_SHA='feb6e159ae8d6aa6622b3dd5e8414b425082b930ee6c739baddb0091127fb370'
RULES_SHA='4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04'

def render(maps:dict)->dict:
 i=maps[INSPECTION];l=maps[PATH_BASE]
 for cl,literal in TECHNICAL:
  if maps[cl][literal]!=literal:raise ValueError(('Original JVM technical tag changed',cl,literal))
 markets=['Jangala','Chicomoztoc','Asharu','Nova Maxios','Ruda']
 factions=['Hegemonia','Liga Perseanska','Tri-Tachyon','Kosciol Luddystyczny','Diktat Sindria']
 cases=[]
 def push(group,s):
  if not s.isascii() or any(w in s for w in ('will comply','forces arrive','Zagrozenia dla kolonii','Dziennik floty','komorkom Sciezki na')):
   raise ValueError(('Untranslated/invalid dynamic output',group,s))
  if '  ' in s or '.Na' in s or ': -' in s:raise ValueError(('Broken spacing',group,s))
  cases.append({'kind':group,'text':s})
 for name,faction in zip(markets,factions):
  compliance=i['The authorities at ']+name+i[' will comply with the inspection. ']+i['It is certain to find any AI cores currently in use.']
  if compliance!=f'Decyzja wladz kolonii: {name} - zgoda na inspekcje. Na pewno wykryje wszystkie uzywane obecnie rdzenie SI.':
   raise ValueError(('Incorrect inspection decision',compliance))
  push('inspection_compliance',compliance)
  damage=i['Operations at %s disrupted'].replace('%s',name)
  if damage!=f'Zaklocono dzialalnosc: {name}':raise ValueError(('Wrong dynamic target',damage))
  push('inspection_disruption',damage)
  arrivals=faction+i[' forces arrive in-system and encounter resistance']
  if arrivals!=f'{faction}: oddzialy dotarly do ukladu i napotkaly opor':
   raise ValueError(('Invalid arrival text',arrivals))
  push('forces_arrival',arrivals)
  support=l['The base serves to provide material support to active Pather cells on nearby colonies, enabling them ']+l['to cause widespread damage and destruction.']
  if support!='Baza zapewnia wsparcie materialne aktywnym komorkom Sciezki Ludda na pobliskich koloniach, umozliwiajac im powodowanie rozleglych szkod i zniszczen.':
   raise ValueError(('Unidiomatic base support paragraph',support))
  push('path_base_support',support)
  lack=l['You do not know of any active pather cells this base might be providing support to.']
  if lack!='Nie wiadomo, czy baza wspiera jakiekolwiek aktywne komorki Sciezki Ludda.':
   raise ValueError('Wrong unknown cells status')
  push('path_base_unknown_support',lack)
 if len(cases)!=25:raise ValueError(('Incorrect rendering coverage',len(cases)))
 return {'rendered_combinations':25,'classes':2,'dynamic_names_tested':len(markets)+len(factions),
   'technical_keys_protected':3,'kinds':sorted(set(x['kind'] for x in cases))}

def check(root:Path,repo:Path|None=None)->dict:
 root=Path(root);repo=Path(repo) if repo else Path(__file__).resolve().parent.parent
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';trans=api/'translations'
 b=(trans/OLD).read_bytes();new=(trans/NEW).read_bytes()
 if (sha(b),sha(new))!=(BASE_SHA,NEW_MAP_SHA):raise ValueError('Unknown map SHA')
 old=readmap(trans/OLD);actual=readmap(trans/NEW)
 expected,stats=build(old)
 if expected!=actual or encode(expected)!=new:raise ValueError('Non-approved map entries changed')
 if (len(actual),len(stats['review']),len(stats['repaired']))!=(5314,48,9):raise ValueError('Mapping totals inconsistent')
 maps={cl:{r['english_literal']:r['polish_ascii_draft'] for r in actual if r['source_class']==cl} for cl in CLASSES}
 render_check=render(maps)
 code=(api/'main.go').read_text('utf8');if_sha=sha(code.encode())
 if if_sha!=NEW_GO_SHA:raise ValueError(('Patcher source altered',if_sha))
 for a,b in reversed([('const version = "1063"','const version = "1064"'),
  ('const exeVersion = "1.0.63"','const exeVersion = "1.0.64"'),
  ('"1062", version}','"1062", "1063", version}'),
  ('PL ASCII patch up to 1.0.63','PL ASCII patch up to 1.0.64')]):code=once(code,b,a)
 if sha(code.encode())!=PRIOR_GO_SHA:raise ValueError('JVM patcher executable Go logic changed')
 if 'const edition = "1.0.64"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer edition not updated')
 mod=root/'mod';info=json.loads((mod/'mod_info.json').read_text('utf8'))
 if (info.get('version'),info.get('gameVersion'),len(info.get('replace',[])))!=('1.0.64','0.98a-RC8',41):raise ValueError('Game version/mod metadata malformed')
 guide=(mod/'CZYTAJ.txt').read_text('utf8')
 if not guide.startswith('STARSECTOR PL ASCII 1.0.64') or not guide.endswith(RELEASE_SUFFIX):raise ValueError('Player guide not updated')
 files=sorted(p for p in (mod/'data').rglob('*') if p.is_file())
 digest=sha('\n'.join(f'{x.relative_to(mod/"data").as_posix()}:{sha(x.read_bytes())}' for x in files).encode())
 if len(files)!=870 or digest!=DATA_SHA or sha((mod/'data/campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError(('Original game text/technical content changed',len(files),digest))
 record=repo/'docs/INSPECTION_PATHBASE_REVIEW_1064.json'
 evidence=repo/'docs/JVM_AUDIT_1064.json'
 if sha(record.read_bytes())!=REVIEW_SHA or sha(evidence.read_bytes())!=JVM_SHA:
  raise ValueError('Original-JVM or 48-row audit evidence modified')
 review_check(root,record)
 ev=json.loads(evidence.read_text('utf8'))
 if (ev['original_jvm_ldc_uses'],ev['mapped_literals'],ev['historic_draft_reviews'],ev['repaired_literals'],len(ev['technical_tags']))!=(150,56,48,9,3):
  raise ValueError('Wrong original JVM callsites or protected tag evidence')
 if len(ev['classes'])!=2:raise ValueError('Missing originally audited class')
 for group in ev['classes']:
  cl=group['source_class'];seen=maps[cl]
  if len(group['literal_evidence'])!=28 or any(r['english_literal'] not in seen or not r['uses'] for r in group['literal_evidence']):
   raise ValueError(('Missing original Java callsite',cl))
 return {'release':'1.0.64','historical_api_reviewed_new':48,'historical_api_reviewed_total':530,
  'historical_api_unreviewed':3128,'source_classes':2,'mapped_literals':56,
  'original_jvm_ldc_uses':150,'corrected_literals':9,
  'unchanged_game_data_files':870,'new_map_sha256':NEW_MAP_SHA,
  'native_windows_gameplay_tested':False,**render_check}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--repo',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.repo),indent=2))
