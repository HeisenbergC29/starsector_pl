#!/usr/bin/env python3
"""Strict independent v1.0.55 source/data/map reproducibility guard."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1055 import OLD,NEW,OLD_SHA,EXPECTED_ROWS,ADDITIONS,REPAIRS,GO_EDITS,plan
from apply_1054 import readmap,encode,sha
from verify_1052 import tree_digest,RULES_SHA,DATA_TREE_SHA
NEW_SHA='c45d1e8e33240b7716e94b9e5ca1f3ae7b74eb1314db38fb57f146b85b863848'
GO_1054_SHA='52218f48b47ce482597db8b23136135371d65816852065b22d7fcbd27e2c34b5'
OBF_GO_SHA='afee0585b7c42017abe64332d66ad4dc6a6720171912d969fb966248123834cc'
OBF_MAP_SHA='435da69852718501146f08b4fada80ae2714c9142b435f90e600c86c594120be'

def check(root):
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';tr=api/'translations'
 raw=(tr/OLD).read_bytes();dst=(tr/NEW).read_bytes()
 if sha(raw)!=OLD_SHA or sha(dst)!=NEW_SHA:raise ValueError('API maps tampered')
 old=readmap(tr/OLD);new=readmap(tr/NEW)
 if encode(old)!=raw or encode(new)!=dst or encode(plan(old))!=dst:raise ValueError('Unexpected CSV row/order delta')
 if len(new)!=EXPECTED_ROWS:raise ValueError('Wrong API map cardinality')
 source=(api/'main.go').read_text('utf8')
 for before,after in reversed(GO_EDITS):
  if source.count(after)!=1:raise ValueError(('Missing or duplicate API version setting',after))
  source=source.replace(after,before)
 if sha(source.encode())!=GO_1054_SHA:raise ValueError('Unexpected Go code changes')
 obf=root/'buildtools/NARZEDZIA_OBF'
 if sha((obf/'main.go').read_bytes())!=OBF_GO_SHA or sha((obf/'TLUMACZENIA_OBF_10153.csv').read_bytes())!=OBF_MAP_SHA:
  raise ValueError('OBF code or table unexpectedly changed')
 if 'const edition = "1.0.55"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer version not incremented')
 m=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if (m.get('version'),m.get('gameVersion'),len(m.get('replace',[])))!=('1.0.55','0.98a-RC8',41):
  raise ValueError('Unexpected localized manifest')
 if not (root/'mod/CZYTAJ.txt').read_text('utf8').startswith('STARSECTOR PL ASCII 1.0.55'):
  raise ValueError('Outdated player instructions')
 tree,n=tree_digest(root)
 if n!=869 or tree!=DATA_TREE_SHA or sha((root/'mod/data/campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError('Game data modified')
 if len([f for f in (root/'mod/data').rglob('*') if f.is_file()])!=870:raise ValueError('Missing game data')
 return {'version':'1.0.55','rows_api':len(new),'new_class_scoped_literals':len(ADDITIONS),
  'corrected_historical_rows':len(REPAIRS),'effective_api_literals':5296,'modified_classes':3,
  'map_sha256':NEW_SHA,'unchanged_game_data_files':870,'obf_unchanged':True,
  'new_java_method_bytecode_edits':0,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(check(a.worktree),indent=2))
