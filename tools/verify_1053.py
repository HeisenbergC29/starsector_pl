#!/usr/bin/env python3
"""Independent, byte-exact OBF-only 1.0.53 release verifier."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1053 import (OLD_OBF,NEW_OBF,OLD_API,NEW_API,OBF_SHA,API_SHA,GO_OBF_SHA,
 GO_API_SHA,OBF_MAIN_EDITS,OBF_TEST_EDITS,API_MAIN_EDITS,read_csv,make_obf,serialize,sha,CHANGES)
from verify_1052 import tree_digest,RULES_SHA,DATA_TREE_SHA

OBF_NEW_SHA='435da69852718501146f08b4fada80ae2714c9142b435f90e600c86c594120be'

def reverse(source,pairs):
 for a,b in reversed(pairs):
  if source.count(b)!=1:raise ValueError(('Nonunique or missing new Go source anchor',b[:120]))
  source=source.replace(b,a)
 return source

def check(root):
 root=Path(root);obf=root/'buildtools/NARZEDZIA_OBF';api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';trans=api/'translations'
 orig=obf/OLD_OBF;cur=obf/NEW_OBF
 if sha(orig.read_bytes())!=OBF_SHA or sha(cur.read_bytes())!=OBF_NEW_SHA:
  raise ValueError('OBF map changed from audited version')
 source=read_csv(orig);target=read_csv(cur)
 if serialize(source)!=orig.read_bytes() or serialize(make_obf(source))!=cur.read_bytes():
  raise ValueError('OBF exact three-row delta or CSV format mismatch')
 if len(target)!=3537 or len({(x['source_class'],x['english_literal']) for x in target})!=3537:
  raise ValueError('OBF duplicate/missing row')
 if sha((trans/OLD_API).read_bytes())!=API_SHA or (trans/NEW_API).read_bytes()!=(trans/OLD_API).read_bytes():
  raise ValueError('Unexpected API mapping edit')
 for folder,name,edits,expect in ((obf,'main.go',OBF_MAIN_EDITS,GO_OBF_SHA),
   (api,'main.go',API_MAIN_EDITS,GO_API_SHA)):
  current=(folder/name).read_text('utf8')
  if sha(reverse(current,edits).encode('utf8'))!=expect:raise ValueError(('Unexpected Go source change',name))
 before=obf/'main_test.go'
 if 'alreadyThisRelease("patched 10153")' not in before.read_text('utf8'):
  raise ValueError('OBF current-version regression test not updated')
 if 'const edition = "1.0.53"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer does not describe 1.0.53')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 if meta.get('version')!='1.0.53' or meta.get('gameVersion')!='0.98a-RC8' or len(meta.get('replace',[]))!=41:
  raise ValueError('Wrong mod manifest')
 if not (root/'mod/CZYTAJ.txt').read_text('utf8').startswith('STARSECTOR PL ASCII 1.0.53'):
  raise ValueError('Outdated user instructions')
 data=root/'mod/data';files=[x for x in data.rglob('*') if x.is_file()]
 tree,count=tree_digest(root)
 if len(files)!=870 or count!=869 or tree!=DATA_TREE_SHA or sha((data/'campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError('Packaged game data accidentally changed')
 # The two dead API mappings are NOT missing translations in the game:
 # one is delivered as mod Java source and the other as OBF constant #816.
 api_rows=read_csv(trans/NEW_API)
 if len(api_rows)!=5283:raise ValueError('Unexpected API map length')
 ghosts={(r['source_class'],r['english_literal']) for r in api_rows if r['source_class'].startswith('data/') or r['source_class']=='com.fs.starfarer.ui.newui.FleetMemberRecoveryDialog'}
 if ghosts!={('data/hullmods/SurveyingEquipment.java','The combined surveying equipment in your fleet reduces the survey cost by %s supplies and %s heavy machinery.'),
  ('com.fs.starfarer.ui.newui.FleetMemberRecoveryDialog','Select ships to recover')}:
  raise ValueError('Unexplained cross-module API mapping')
 java=(data/'hullmods/SurveyingEquipment.java').read_text('utf8')
 if 'Sprzet pomiarowy calej floty zmniejsza koszt badania planet' not in java or 'jedn. zaopatrzenia i %s jedn. ciezkich maszyn.' not in java:
  raise ValueError('Localized survey description is not delivered as mod source')
 return {'version':'1.0.53','obf_entries':3537,'new_recovery_ui_entries':len(CHANGES),
  'new_obf_map_sha256':OBF_NEW_SHA,'new_obf_patched_jar_sha256':'85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1',
  'api_entries':5283,'api_map_same_as_1052':True,'known_cross_layer_api_rows':2,
  'localized_mod_data_files_unchanged':870,'new_executable_java_changes':0,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(check(p.parse_args().worktree),indent=2))
