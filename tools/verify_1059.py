#!/usr/bin/env python3
"""Strict source-only 1.0.59 API mapping and complete data-integrity checks."""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
from apply_1059 import CLASS,ADDITIONS,CORRECTION,BASE_MAP_SHA,EXPECTED_ROWS,STATUS,OLD,NEW,build,sha,RELEASE_SUFFIX
from apply_1054 import readmap,encode

NEW_MAP_SHA='cfa73e2eca4a7e957ec68c72551a7f87d1de447f5cf8c2b735e8e7bb2bbc5b67'
DATA_SHA='feb6e159ae8d6aa6622b3dd5e8414b425082b930ee6c739baddb0091127fb370'
RULES_SHA='4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04'
GO_SHA='9bbbba4f2cc3225bf54d31dc1541184a5d7143671262428ca270cc6080bf022e'

def quantities(mapping):
 """Build UI sentence in the same StringBuilder order as the original JVM."""
 for qty in (1,2,5,12,21):
  for name in ('Ruda','Paliwo','Ciezka maszyna'):
   text=mapping[CORRECTION[0]].replace('%s',str(qty))+mapping['unit' if qty<=1 else 'units']+mapping[' of ']+name+'.'
   expected=f'Szacunkowa ilosc: {qty} jedn. Towar: {name}.'
   if text!=expected:raise ValueError(('Composed quantity is broken',qty,name,text))
 return 15

def check(root:Path)->dict:
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';trans=api/'translations'
 old=(trans/OLD).read_bytes();current=(trans/NEW).read_bytes()
 if sha(old)!=BASE_MAP_SHA or sha(current)!=NEW_MAP_SHA:raise ValueError('Unexpected API mapping hash')
 rows=readmap(trans/OLD);expected=build(rows);newrows=readmap(trans/NEW)
 if current!=encode(expected) or newrows!=expected:raise ValueError('Unexpected map delta or CSV formatting')
 keys={(x['source_class'],x['english_literal']):x for x in newrows}
 scoped={x['english_literal']:x['polish_ascii_draft'] for x in newrows if x['source_class']==CLASS}
 if any(scoped[k]!=v for k,v in ADDITIONS.items()) or scoped[CORRECTION[0]]!=CORRECTION[2]:
  raise ValueError('Missing exact scoped replacements')
 if any(keys[(CLASS,k)]['status']!=STATUS for k in [*ADDITIONS,CORRECTION[0]]):
  raise ValueError('Unreviewed/invalid status for the new literals')
 renders=quantities(scoped)
 if sha((api/'main.go').read_bytes())!=GO_SHA:raise ValueError('API patcher implementation modified outside approved version changes')
 installer=(root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 if 'const edition = "1.0.59"' not in installer:raise ValueError('Installer version mismatch')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if (meta.get('version'),meta.get('gameVersion'),len(meta.get('replace',[])))!=('1.0.59','0.98a-RC8',41):
  raise ValueError('Mod metadata mismatch')
 guide=(root/'mod/CZYTAJ.txt').read_text('utf8')
 if not guide.startswith('STARSECTOR PL ASCII 1.0.59') or not guide.endswith(RELEASE_SUFFIX):
  raise ValueError('Player documentation mismatch')
 data=root/'mod/data';files=sorted(p for p in data.rglob('*') if p.is_file())
 digest=sha('\n'.join(f'{p.relative_to(data).as_posix()}:{sha(p.read_bytes())}' for p in files).encode())
 if len(files)!=870 or digest!=DATA_SHA:raise ValueError(('Unexpected game data delta',len(files),digest))
 if sha((data/'campaign/rules.csv').read_bytes())!=RULES_SHA:raise ValueError('Dialog data changed')
 return {'release':'1.0.59','class_scoped_new_literals':6,'revised_old_literal':1,
         'total_api_map_rows':len(newrows),'api_map_sha256':NEW_MAP_SHA,
         'monthly_report_quantity_renderings_checked':renders,
         'game_data_files_byte_identical':870,'dialogue_rules_sha256_unchanged':RULES_SHA,
         'no_gameplay_code_changed':True,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(check(a.worktree),indent=2))
