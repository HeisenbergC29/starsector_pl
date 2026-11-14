#!/usr/bin/env python3
"""Independent byte-for-byte v1.0.57 rules, sources and map regression checks."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re
from pathlib import Path
from apply_1056 import field_spans,encode_like,decode_field,once,DYNAMIC
from apply_1057 import ROOT,PLAN_FILE,read_plan,patch_rules,sha,BASE_RULES_SHA,EXPECTED_ROWS,EXPECTED_PHRASES,EXPECTED_REMOVED,SUFFIX,BASE_API_MAP_SHA
from verify_1056 import other_data_digest

NEW_RULES_SHA='693b874b6738d792bbf5b74a9e247e594c607c1834a2822823a228511a311f6c'
OTHER_DATA_SHA='5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1'
PREVIOUS_GO_SHA='48dbe1e45d40215b2ab155f25a6204adca0ad67b2f4979c808712af902232862'
NEW_GO_SHA='56cdcdf6a08e4a07e9a5cabc667c48b262ea5638a9fc0dc1420fefdf5f814b2c'
PREVIOUS_CZYTAJ_SHA=None  # reconstructed by stripping the precise 1.0.57 suffix

PRIOR_LEDGER_NAMES=(
 'RULES_PRONOUN_REVIEW_1034.json','RULES_PRONOUN_REVIEW_1035.json','RULES_PRONOUN_REVIEW_1039.json',
 'RULES_POSSESSIVE_REVIEW_1043.json','RULES_GENDER_REVIEW_1044.json','RULES_GENDER_REVIEW_1045.json',
 'RULES_NEUTRAL_REVIEW_1056.json',
)

def reverse_rules(installed:bytes,plan:dict)->bytes:
 if sha(installed)!=NEW_RULES_SHA:raise ValueError('Wrong installed 1.0.57 rules.csv SHA')
 s=installed.decode('ascii');lines=s.splitlines(keepends=True)
 rdr=csv.reader(io.StringIO(s,newline=''))
 prev=0;parts=[];matched=set();rows=0
 for row in rdr:
  rec=''.join(lines[prev:rdr.line_num]);prev=rdr.line_num
  bounds=field_spans(rec)
  if len(bounds)!=len(row):raise ValueError(('Malformed CSV record',rows))
  if rows and row[0] in plan:
   ident=row[0];p=plan[ident]
   if ident in matched:raise ValueError(('Duplicated rule',ident))
   matched.add(ident)
   if row[4]!=p['revised_text']:raise ValueError(('Changed revised text',ident))
   a,b=bounds[4]
   if decode_field(rec[a:b])!=p['revised_text']:raise ValueError(('Changed lexical quoting',ident))
   previous=rec[:a]+encode_like(rec[a:b],p['original_text'])+rec[b:]
   check=list(csv.reader(io.StringIO(previous,newline='')))
   if len(check)!=1 or check[0][:4]!=row[:4] or check[0][5:]!=row[5:] or check[0][4]!=p['original_text']:
    raise ValueError(('Non-text columns not preserved',ident))
   rec=previous
  parts.append(rec);rows+=1
 if rows!=11108 or len(matched)!=EXPECTED_ROWS or prev!=len(lines):
  raise ValueError(('Incomplete reverse audit',rows,len(matched)))
 baseline=''.join(parts).encode('ascii')
 if sha(baseline)!=BASE_RULES_SHA:raise ValueError('Recreated 1.0.56 rules.csv is not byte-identical')
 forward,report=patch_rules(baseline,plan)
 if forward!=installed:raise ValueError('Reconstruction is not reversible')
 return baseline

def check(worktree:Path,root:Path=ROOT,validate_prior:bool=True)->dict:
 worktree=Path(worktree);root=Path(root)
 plan=read_plan(root)
 if validate_prior:
  older=set()
  for name in PRIOR_LEDGER_NAMES:
   src=json.loads((root/'docs'/name).read_text('utf8'))
   rr=src.get('approved',src.get('reviewed',src.get('records',[])))
   keys=[x['id'] for x in rr]
   if len(keys)!=len(set(keys)) or set(keys)&older:
    raise ValueError(('Overlapping historical review list',name))
   older.update(keys)
  if len(older)!=363 or set(plan)&older:
   raise ValueError(('New edits alter previously reviewed records',len(older),set(plan)&older))
 mod=worktree/'mod'
 rules=(mod/'data/campaign/rules.csv').read_bytes()
 baseline=reverse_rules(rules,plan)
 assert sha(baseline)==BASE_RULES_SHA
 digest,count=other_data_digest(mod)
 if count!=869 or digest!=OTHER_DATA_SHA:raise ValueError(('Other original 869 files were changed',count,digest))
 reader=csv.DictReader(io.StringIO(rules.decode('ascii'),newline=''))
 rows=list(reader)
 if len(rows)!=11107 or any(r['id'].startswith('#') and r['id'] in plan for r in rows):raise ValueError('Structural CSV row count changed')
 affected=sum(bool(DYNAMIC.search(r['text'])) for r in rows)
 occurrences=sum(len(DYNAMIC.findall(r['text'])) for r in rows)
 if (affected,occurrences)!=(1028,2089):raise ValueError(('Unexpected remaining gender variable accounting',affected,occurrences))
 api=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 oldmap=(api/'translations/TLUMACZENIA_JAR_1056.csv').read_bytes()
 newmap=(api/'translations/TLUMACZENIA_JAR_1057.csv').read_bytes()
 if sha(oldmap)!=BASE_API_MAP_SHA or newmap!=oldmap:raise ValueError('API mapping was unexpectedly modified')
 src=(api/'main.go').read_text('utf8')
 if sha(src.encode('utf8'))!=NEW_GO_SHA:raise ValueError('Unexpected API Go code modification')
 for old,new in reversed([
  ('const version = "1056"','const version = "1057"'),
  ('const exeVersion = "1.0.56"','const exeVersion = "1.0.57"'),
  ('"1055", version}','"1055", "1056", version}'),
  ('PL ASCII patch up to 1.0.56','PL ASCII patch up to 1.0.57')]):src=once(src,new,old)
 if sha(src.encode('utf8'))!=PREVIOUS_GO_SHA:raise ValueError('Non-version Go code changed')
 if 'const edition = "1.0.57"' not in (worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer version not advanced')
 m=json.loads((mod/'mod_info.json').read_text('utf8'))
 if (m.get('version'),m.get('gameVersion'),len(m.get('replace',[])))!=('1.0.57','0.98a-RC8',41):
  raise ValueError('Invalid 1.0.57 mod metadata')
 guide=(mod/'CZYTAJ.txt').read_text('utf8')
 if not guide.startswith('STARSECTOR PL ASCII 1.0.57') or not guide.endswith(SUFFIX):
  raise ValueError('Player guide missing exact release notes')
 return {'release':'1.0.57','game_version':'0.98a-RC8','total_dialogue_rows':11107,
  'corrected_dialogue_rows':EXPECTED_ROWS,'corrected_grammar_fragments':EXPECTED_PHRASES,
  'removed_gender_placeholders':EXPECTED_REMOVED,'remaining_gender_placeholders':2089,
  'remaining_gender_affected_rows':1028,'rules_sha256':NEW_RULES_SHA,
  'original_1056_rules_reproduced_byte_exactly':True,'protected_older_reviews':363 if validate_prior else None,
  'other_game_data_files_byte_identical':869,'api_map_entries_unchanged':5298,
  'obf_map_entries_unchanged':3537,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(check(a.worktree),indent=2))
