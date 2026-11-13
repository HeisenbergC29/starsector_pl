#!/usr/bin/env python3
"""Independent release 1.0.54 CSV/Go/game-data validation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1054 import OLD,NEW,BASE_SHA,ADDITIONS,CORRECTIONS,readmap,encode,make,sha
from verify_1052 import tree_digest,RULES_SHA,DATA_TREE_SHA
NEW_SHA='d7256e12565e62d3cce7c67479014af9857a1b9357e252bcca26a7ae79067ce0'
GO_1053_SHA='51b76035859321f90cf004d0f736de295010066637b04b396e4d95b5787575c8'
OBF_1053_SHA='435da69852718501146f08b4fada80ae2714c9142b435f90e600c86c594120be'
OBF_GO_SHA='afee0585b7c42017abe64332d66ad4dc6a6720171912d969fb966248123834cc'
EDITS=(('const version = "1053"','const version = "1054"'),
 ('const exeVersion = "1.0.53"','const exeVersion = "1.0.54"'),
 ('"1050", "1051", "1052", version}', '"1050", "1051", "1052", "1053", version}'),
 ('PL ASCII patch up to 1.0.53','PL ASCII patch up to 1.0.54'))

def check(root):
 root=Path(root);obf=root/'buildtools/NARZEDZIA_OBF';api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';tr=api/'translations'
 old=tr/OLD;new=tr/NEW
 if sha(old.read_bytes())!=BASE_SHA or sha(new.read_bytes())!=NEW_SHA:raise ValueError('API map SHA changed')
 orig=readmap(old);updated=readmap(new)
 if encode(orig)!=old.read_bytes() or encode(make(orig))!=new.read_bytes():raise ValueError('API map exact delta/CRLF changed')
 if len(updated)!=5290 or len(set((x['source_class'],x['english_literal']) for x in updated))!=5290:raise ValueError('Duplicate API map entries')
 actual=(api/'main.go').read_text('utf8')
 for previous,now in reversed(EDITS):
  if actual.count(now)!=1:raise ValueError(('Missing or ambiguous Go release source anchor',now))
  actual=actual.replace(now,previous)
 if sha(actual.encode())!=GO_1053_SHA:raise ValueError('API Go patcher changed outside approved version strings')
 if sha((obf/'TLUMACZENIA_OBF_10153.csv').read_bytes())!=OBF_1053_SHA or sha((obf/'main.go').read_bytes())!=OBF_GO_SHA:
  raise ValueError('OBF patcher should remain exactly 1.0.53')
 if 'const edition = "1.0.54"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer version not updated')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if (meta.get('version'),meta.get('gameVersion'),len(meta.get('replace',[])))!=('1.0.54','0.98a-RC8',41):raise ValueError('Mod metadata invalid')
 if not (root/'mod/CZYTAJ.txt').read_text('utf8').startswith('STARSECTOR PL ASCII 1.0.54'):raise ValueError('Outdated user documentation')
 files=[f for f in (root/'mod/data').rglob('*') if f.is_file()]
 tree,count=tree_digest(root)
 if len(files)!=870 or count!=869 or tree!=DATA_TREE_SHA or sha((root/'mod/data/campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError('Game data unexpectedly changed')
 return {'release':'1.0.54','api_map_entries':5290,'new_keys':len(ADDITIONS),'corrected_rows':len(CORRECTIONS),
 'obf_map_entries_unchanged':3537,'active_api_strings_expected':5288,'changed_java_classes_expected':6,
 'unmodified_data_files':870,'unchanged_prior_api_and_obf_patcher_source_outside_version_constants':True,
 'api_map_sha256':NEW_SHA,'new_executable_java_bytecode_changes':0,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(check(a.worktree),indent=2))
