#!/usr/bin/env python3
"""Fail-closed source contract for v1.0.66 (three original JVM classes)."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1054 import readmap,encode,once
from apply_1066 import SIM,IND,TUT,OLD,NEW,BASE_SHA,ADDITIONS,CORRECTIONS,RELEASE_SUFFIX,sha,build
from build_review_1066 import check as review_check
MAP_SHA='3507bbda4a38d5d38a701a063c61a44f0576d3fad5af9b80ba3c0c1206904478'
PREV_GO_SHA='fff448cb53c8638e1d5f417e1efd1ac09d74466ee546ecb85d92c726aabf2e25'
GO_SHA='156f140400a5303e135ee1f914de2d93f7c9014c6d47f83a3af14ccce48d5123'
DATA_SHA='feb6e159ae8d6aa6622b3dd5e8414b425082b930ee6c739baddb0091127fb370'
RULES_SHA='4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04'
REVIEW_SHA='0c310506bf14494bbe7cfb29d9e51cc4010e48ead41cc1034b3ff67a30b10a1f'
JVM_SHA='eed875e3324019cffc86e2ca5c6701158c5f8ba81066311171aeb9b3093b9fbe'
QUANTITIES=[1,2,5,12,21]
COLONIES=['Jangala','Chicomoztoc','Asharu','Sindria','Nova Maxios']

def render(m:dict)->dict:
 sim=m[SIM];ind=m[IND];tut=m[TUT]
 examples=[]
 def add(category,actual,expected):
  if actual!=expected or '%s' in actual or '\n' in actual or not actual.isascii() or '  ' in actual:
   raise ValueError(('Broken composed visible text',category,actual,expected))
  examples.append({'category':category,'text':actual})
 for n,colony in zip(QUANTITIES,COLONIES):
  num=str(n);unit=ind['day' if n==1 else 'days'];production=ind['unit' if n==1 else 'units']
  for prefix,expected in [('Disrupted: ','Zaklocenia, pozostalo: '),
     ('Upgrading: ','Ulepszanie, pozostalo: '),('Building: ','Budowa, pozostalo: ')]:
   add('progress',ind[prefix]+num+' '+unit+ind[' left'],f'{expected}{num} {"dzien" if n==1 else "dni"}')
  add('duration',num+' '+unit,f'{num} {"dzien" if n==1 else "dni"}')
  add('remaining_construction',ind['Requires %s more '].replace('%s',num)+unit+ind[' to finish building.'],
      f'Pozostaly czas: {num} {"dzien" if n==1 else "dni"}.')
  for suffix in (' to build. You have %s.',' to upgrade. You have %s.'):
   sentence=ind['%s and %s '].replace('%s','%VALUE%',1).replace('%s',num,1).replace('%VALUE%','5000')+unit+ind[suffix].replace('%s','2500')
   add('cost_time',sentence,f'Koszt: 5000; czas: {num} {"dzien" if n==1 else "dni"}. Dostepne srodki: 2500.')
  for header in ('Production increased by %s ','Increases production by %s '):
   txt=ind[header].replace('%s',num)+production+'.'
   start=('Produkcja zwiekszona o ' if header=='Production increased by %s ' else 'Zwieksza produkcje o ')
   add('production',txt,f'{start}{num} jedn.')
  add('construction_notification','Rafineria'+ind[' at ']+colony,f'Rafineria - kolonia: {colony}')
  add('tutorial_ability',tut['Use %s to avoid detection, and %s to get away if you are seen.'].replace('%s',tut['Go Dark'],1).replace('%s',tut['Emergency Burn'],1),
       'Uzyj trybu skrytego, aby uniknac wykrycia, a awaryjnego dopalacza, aby uciec, jesli zostaniesz zauwazony.')
  add('tutorial_scanner',tut['Go to Pontus, head out towards the asteroid belt, and then use an %s to locate the probe. '].replace('%s',tut['Active Sensor Burst']),
       'Udaj sie do Pontusa, skieruj sie ku pasowi asteroid, a nastepnie uzyj aktywnego impulsu czujnikow, aby zlokalizowac sonde. ')
 if tut['"Storage"'] not in tut['In addition, you now have access to local storage at Ancyra, and some weapons and supplies have been placed there. To access it, click on the "Storage" button in the trade screen.)']:
  raise ValueError('Polish tutorial tooltip highlight does not occur in the translated paragraph')
 if tut['Completed']!='Ukonczono' or tut['"autofit"']!='"automatyczne dopasowanie"':
  raise ValueError('Tutorial UI terms inconsistent')
 if (sim['Aggression / behavior'],sim['DevMode stuff'])!=('Agresja i zachowanie','Opcje deweloperskie'):
  raise ValueError('Simulator settings headings remained untranslated')
 if (ind['day'],ind['days'],ind['unit'],ind['units'],ind[' left'])!=('dzien','dni','jedn','jedn',''):
  raise ValueError('Incorrect grammar neutralizers in colony UI')
 if len(examples)!=60: # 11 text render types per number
  raise ValueError(('Rendered scenario coverage changed',len(examples)))
 return {'rendered_combinations':len(examples),'tested_numbers':QUANTITIES,
    'tested_colonies':COLONIES,'tutorial_highlight_consistent':True,
    'simulator_titles_translated':True,'all_rendered_ascii':True}

def check(root:Path,repo:Path|None=None)->dict:
 root=Path(root);repo=Path(repo) if repo else Path(__file__).resolve().parent.parent
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';tr=api/'translations'
 if (sha((tr/OLD).read_bytes()),sha((tr/NEW).read_bytes()))!=(BASE_SHA,MAP_SHA):
  raise ValueError('Versioned API translations have wrong SHA')
 old=readmap(tr/OLD);final=readmap(tr/NEW);expected,meta=build(old)
 if final!=expected or encode(final)!=(tr/NEW).read_bytes() or len(final)!=5327:
  raise ValueError('Unapproved Java API translations or map serialization')
 mapped={cl:{r['english_literal']:r['polish_ascii_draft'] for r in final if r['source_class']==cl}
  for cl in (SIM,IND,TUT)}
 if tuple(len(mapped[c]) for c in (SIM,IND,TUT))!=(76,77,52):
  raise ValueError('Class-scoped mapping cardinality mismatch')
 rendered=render(mapped)
 go=(api/'main.go').read_text('utf8')
 if sha(go.encode())!=GO_SHA:raise ValueError('Unapproved Go patcher changes')
 for after,before in reversed([
  ('const version = "1066"','const version = "1065"'),
  ('const exeVersion = "1.0.66"','const exeVersion = "1.0.65"'),
  ('"1064", "1065", version}','"1064", version}'),
  ('PL ASCII patch up to 1.0.66','PL ASCII patch up to 1.0.65')]):
  go=once(go,after,before)
 if sha(go.encode())!=PREV_GO_SHA:raise ValueError('Unexpected Go logic change')
 if 'const edition = "1.0.66"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Stale Windows installer release number')
 mod=root/'mod';cfg=json.loads((mod/'mod_info.json').read_text('utf8'))
 if (cfg.get('version'),cfg.get('gameVersion'),len(cfg.get('replace',[])))!=('1.0.66','0.98a-RC8',41):
  raise ValueError('Mod/game metadata invalid')
 instructions=(mod/'CZYTAJ.txt').read_text('utf8')
 if not instructions.startswith('STARSECTOR PL ASCII 1.0.66') or not instructions.endswith(RELEASE_SUFFIX):
  raise ValueError('Updated user instructions invalid')
 files=sorted(p for p in (mod/'data').rglob('*') if p.is_file())
 digest=sha('\n'.join(f'{p.relative_to(mod/"data").as_posix()}:{sha(p.read_bytes())}' for p in files).encode())
 if len(files)!=870 or digest!=DATA_SHA or sha((mod/'data/campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError('Commercial game data or dialogue options changed')
 record=repo/'docs/SIM_INDUSTRY_TUTORIAL_REVIEW_1066.json'
 evidence=repo/'docs/JVM_AUDIT_1066.json'
 if sha(record.read_bytes())!=REVIEW_SHA or sha(evidence.read_bytes())!=JVM_SHA:
  raise ValueError('Human translation review evidence drifted')
 review_check(root,record)
 audit=json.loads(evidence.read_text('utf8'))
 if (audit['total_original_jvm_ldc_uses'],audit['total_map_literals_after'])!=(669,205):
  raise ValueError('JVM active text evidence does not match approved scope')
 for cl,n in ((SIM,76),(IND,77),(TUT,52)):
  if len(audit['classes'][cl]['mapped_callsites'])!=n:raise ValueError('Missing source bytecode evidence')
 return {'release':'1.0.66','new_missing_ui_texts':13,'corrected_ui_fragments':9,
   'reviewed_draft_status_rows':161,'new_unique_historical_reviews':114,
   'prior_historical_reviews_not_recounted':47,'historical_api_reviews_total':731,
   'historical_api_unreviewed':2927,'original_jvm_ldc_uses':669,
   'mapped_class_scoped_literals':205,'unchanged_game_data_files':870,
   'gameplay_testing':'after_1_1_release',**rendered}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--repo',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.repo),indent=2))
