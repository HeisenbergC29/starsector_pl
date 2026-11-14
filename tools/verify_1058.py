#!/usr/bin/env python3
"""Independent, byte-exact verification of 122 dialogue speech attributions."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re
from pathlib import Path
from apply_1056 import DYNAMIC,field_spans,decode_field,encode_like,once
from apply_1058 import ROOT,PLAN,read_plan,patch_rules,sha,BASE_RULES_SHA,BASE_API_MAP_SHA,EXPECTED_ROWS,EXPECTED_EDITS,SUFFIX
from verify_1056 import other_data_digest
from verify_1057 import PRIOR_LEDGER_NAMES

NEW_RULES_SHA='4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04'
OTHER_DATA_SHA='5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1'
PREV_GO_SHA='56cdcdf6a08e4a07e9a5cabc667c48b262ea5638a9fc0dc1420fefdf5f814b2c'

def reverse_rules(installed:bytes,plan:dict)->bytes:
 if sha(installed)!=NEW_RULES_SHA:raise ValueError('Unapproved installed rules.csv bytes')
 s=installed.decode('ascii');lines=s.splitlines(keepends=True)
 rdr=csv.reader(io.StringIO(s,newline=''))
 previous=0;parts=[];matched=set();rows=0
 for row in rdr:
  record=''.join(lines[previous:rdr.line_num]);previous=rdr.line_num
  bounds=field_spans(record)
  if len(bounds)!=len(row):raise ValueError(('CSV record damaged',rows))
  if rows and row[0] in plan:
   id=row[0];entry=plan[id]
   if id in matched or row[4]!=entry['revised_text'] or sha(row[4].encode())!=entry['new_text_sha256']:
    raise ValueError(('Text changed after review',id))
   matched.add(id);lo,hi=bounds[4]
   if decode_field(record[lo:hi])!=row[4]:raise ValueError(('Lexical field mismatch',id))
   rebuilt=record[:lo]+encode_like(record[lo:hi],entry['original_text'])+record[hi:]
   fields=list(csv.reader(io.StringIO(rebuilt,newline='')))
   if len(fields)!=1 or fields[0][:4]!=row[:4] or fields[0][5:]!=row[5:] or fields[0][4]!=entry['original_text']:
    raise ValueError(('Changed non-text fields',id))
   record=rebuilt
  parts.append(record);rows+=1
 if rows!=11108 or matched!=set(plan) or previous!=len(lines):
  raise ValueError(('Missed reviewed ID or changed row count',rows,len(matched)))
 result=''.join(parts).encode('ascii')
 if sha(result)!=BASE_RULES_SHA or patch_rules(result,plan)[0]!=installed:
  raise ValueError('Cannot byte-exactly reverse 1.0.58 to 1.0.57')
 return result

def check(worktree:Path,root:Path=ROOT,validate_prior:bool=True)->dict:
 worktree=Path(worktree);root=Path(root);plan=read_plan(root)
 if validate_prior:
  protected=set()
  for name in (*PRIOR_LEDGER_NAMES,'RULES_REFLEXIVE_REVIEW_1057.json'):
   d=json.loads((root/'docs'/name).read_text('utf8'))
   rr=d.get('approved',d.get('reviewed',d.get('records',[])))
   keys=[r['id'] for r in rr]
   if len(keys)!=len(set(keys)) or protected.intersection(keys):raise ValueError(('Duplicate prior review ID',name))
   protected.update(keys)
  if len(protected)!=433 or protected.intersection(plan):raise ValueError(('Reviewed dialogue overlap',len(protected),protected.intersection(plan)))
 mod=worktree/'mod';rules=(mod/'data/campaign/rules.csv').read_bytes()
 reverse_rules(rules,plan)
 digest,count=other_data_digest(mod)
 if (count,digest)!=(869,OTHER_DATA_SHA):raise ValueError(('Unexpected changes to 869 other game data',count,digest))
 rdr=list(csv.DictReader(io.StringIO(rules.decode('ascii'),newline='')))
 if len(rdr)!=11107:raise ValueError('Changed number of dialogue records')
 remaining=sum(len(DYNAMIC.findall(r['text'])) for r in rdr)
 affected=sum(bool(DYNAMIC.search(r['text'])) for r in rdr)
 if (remaining,affected)!=(1953,1006):raise ValueError(('Unexplained dynamic marker changes',remaining,affected))
 api=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 a=(api/'translations/TLUMACZENIA_JAR_1057.csv').read_bytes();b=(api/'translations/TLUMACZENIA_JAR_1058.csv').read_bytes()
 if sha(a)!=BASE_API_MAP_SHA or a!=b:raise ValueError('API class map was modified')
 go=(api/'main.go').read_text('utf8')
 for src,target in reversed([
  ('const version = "1057"','const version = "1058"'),
  ('const exeVersion = "1.0.57"','const exeVersion = "1.0.58"'),
  ('"1056", version}','"1056", "1057", version}'),
  ('PL ASCII patch up to 1.0.57','PL ASCII patch up to 1.0.58')]):go=once(go,target,src)
 if sha(go.encode('utf8'))!=PREV_GO_SHA:raise ValueError('Executable patcher Go code changed beyond version metadata')
 if 'const edition = "1.0.58"' not in (worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer version mismatch')
 manifest=json.loads((mod/'mod_info.json').read_text('utf8'))
 if (manifest.get('version'),manifest.get('gameVersion'),len(manifest.get('replace',[])))!=('1.0.58','0.98a-RC8',41):
  raise ValueError('Wrong mod metadata')
 guide=(mod/'CZYTAJ.txt').read_text('utf8')
 if not guide.startswith('STARSECTOR PL ASCII 1.0.58') or not guide.endswith(SUFFIX):raise ValueError('Changed player guidance')
 return {'version':'1.0.58','total_dialogue_rows':11107,'new_reviewed_dialogue_rows':EXPECTED_ROWS,
  'speech_attributions_corrected':EXPECTED_EDITS,'unique_reviewed_cumulative':555,'removed_gender_placeholders_cumulative':742,
  'remaining_gender_placeholders':remaining,'remaining_affected_rows':affected,
  'rules_sha256':NEW_RULES_SHA,'previous_1057_rules_reproduced_byte_exact':True,
  'other_game_data_files_unchanged':869,'unchanged_api_map_entries':5298,'obf_map_entries':3537,
  'historical_api_reviews_unresolved':3267,'jvm_getter_contexts_unresolved':186,'native_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(check(a.worktree),indent=2))
