#!/usr/bin/env python3
"""Independent byte-exact validation of 110 v1.0.56 text-only rules edits."""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
from apply_1056 import ROOT,PLAN_FILE,BASE_RULES_SHA,EXPECTED_ENTRIES,decode_field,encode_like,field_spans,read_plan,sha,once,DYNAMIC

EXPECTED_LEDGER_SHA='049542fe20c36c6b1ba87ef70398eeef66ecfc1dc6955361d96661447710cc62'
NEW_RULES_SHA='a08330e67de037fc0df66447c039ec7ac6792340405d2983c04e31f2bfef4810'
BASE_API_MAIN_SHA='ba6b462ec6042c87fe4a77df0132cba5a3cc846f56a6f41922754ee82f36c377'
NEW_API_MAIN_SHA='48dbe1e45d40215b2ab155f25a6204adca0ad67b2f4979c808712af902232862'
API_MAP_SHA='c45d1e8e33240b7716e94b9e5ca1f3ae7b74eb1314db38fb57f146b85b863848'
BASE_README_SHA='0a951b8738912b2f12831162fa312a420aae859e27bef29053c0eec67f80bf6f'
OTHER_DATA_SHA='5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1'
SUFFIX='\nW 110 dialogach usunieto zbedne zmienne zalazne od plci z narracji (mowi, odpowiada, okreslenia twarzy i gestow). Skrypty, warunki i opcje dialogow niezmienione.\n'

def invert_rules(installed:bytes,plan:dict)->bytes:
 if sha(installed)!=NEW_RULES_SHA:raise ValueError('Incorrect 1.0.56 rules SHA')
 lines=installed.decode('ascii').splitlines(keepends=True)
 reader=csv.reader(io.StringIO(installed.decode('ascii'),newline=''))
 previous=0;pieces=[];seen=set();n=0
 for row in reader:
  rec=''.join(lines[previous:reader.line_num]);previous=reader.line_num
  bounds=field_spans(rec)
  if len(bounds)!=len(row):raise ValueError(('Malformed CSV record',n))
  if n>0 and row[0] in plan:
   entry=plan[row[0]];name=row[0]
   if name in seen:raise ValueError(('Duplicate reviewed rule ID',name))
   seen.add(name)
   old,new=entry['original_text'],entry['revised_text']
   if row[4]!=new or sha(row[4].encode('ascii'))!=entry['new_text_sha256'] or sha(old.encode('ascii'))!=entry['old_text_sha256']:
    raise ValueError(('Unapproved text deviation',name))
   if len(DYNAMIC.findall(old))!=1 or DYNAMIC.search(new):raise ValueError(('Incorrect gender tokens',name))
   lo,hi=bounds[4]
   if decode_field(rec[lo:hi])!=new:raise ValueError(('Broken field lexical encoding',name))
   rec=rec[:lo]+encode_like(rec[lo:hi],old)+rec[hi:]
   reversed_csv=list(csv.reader(io.StringIO(rec,newline='')))
   if len(reversed_csv)!=1 or reversed_csv[0][:4]!=row[:4] or reversed_csv[0][5:]!=row[5:] or reversed_csv[0][4]!=old:
    raise ValueError(('Non-text column changed',name))
  pieces.append(rec);n+=1
 if n!=11108 or seen!=set(plan) or previous!=len(lines):raise ValueError('Rule review coverage incomplete')
 reconstruction=''.join(pieces).encode('ascii')
 if sha(reconstruction)!=BASE_RULES_SHA:raise ValueError('Non-reviewed bytes of rules.csv changed')
 return reconstruction

def other_data_digest(mod:Path)->tuple[str,int]:
 files=sorted(p for p in (mod/'data').rglob('*') if p.is_file() and p.name!='rules.csv')
 h=hashlib.sha256()
 for p in files:
  h.update(p.relative_to(mod/'data').as_posix().encode('ascii')+b'\0'+bytes.fromhex(sha(p.read_bytes())))
 return h.hexdigest(),len(files)

def check(worktree:Path,repo:Path=ROOT,validate_prior:bool=True)->dict:
 worktree=Path(worktree);plan_raw=(repo/PLAN_FILE).read_bytes()
 if sha(plan_raw)!=EXPECTED_LEDGER_SHA:raise ValueError('Reviewed plan bytes changed')
 plan=read_plan(repo/PLAN_FILE)
 previously_reviewed=set()
 if validate_prior:
  for filename in ('RULES_PRONOUN_REVIEW_1034.json','RULES_PRONOUN_REVIEW_1035.json','RULES_PRONOUN_REVIEW_1039.json','RULES_POSSESSIVE_REVIEW_1043.json','RULES_GENDER_REVIEW_1044.json','RULES_GENDER_REVIEW_1045.json'):
   doc=json.loads((repo/'docs'/filename).read_text('utf8'))
   these=[row['id'] for row in doc.get('reviewed',doc.get('approved',[]))]
   if len(these)!=len(set(these)) or set(these).intersection(previously_reviewed):raise ValueError(('Earlier review ledger duplicate',filename))
   previously_reviewed.update(these)
  if len(previously_reviewed)!=253 or set(plan).intersection(previously_reviewed):
   raise ValueError(('Current 110 review IDs overlap 253 previously reviewed IDs',len(previously_reviewed),set(plan)&previously_reviewed))
 for key,record in plan.items():
  if sha(record['original_text'].encode('ascii'))!=record['old_text_sha256'] or sha(record['revised_text'].encode('ascii'))!=record['new_text_sha256']:
   raise ValueError(('Plan text hash mismatch',key))
  text=record['original_text']
  for old,new in record['edits']:text=once(text,old,new)
  if text!=record['revised_text']:raise ValueError(('Edited text does not match plan',key))
 rules=worktree/'mod/data/campaign/rules.csv'
 invert_rules(rules.read_bytes(),plan)
 mod=worktree/'mod'
 data_digest,count=other_data_digest(mod)
 if count!=869 or data_digest!=OTHER_DATA_SHA:raise ValueError(('Other 869 data files modified',count,data_digest))
 api=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 amap=api/'translations/TLUMACZENIA_JAR_1055.csv';bmap=api/'translations/TLUMACZENIA_JAR_1056.csv'
 if sha(amap.read_bytes())!=API_MAP_SHA or bmap.read_bytes()!=amap.read_bytes():raise ValueError('API mapping changed')
 s=(api/'main.go').read_text('utf8')
 if sha(s.encode('utf8'))!=NEW_API_MAIN_SHA:raise ValueError('API Go code changed outside version markers')
 for from_,to in reversed([('const version = "1055"','const version = "1056"'),('const exeVersion = "1.0.55"','const exeVersion = "1.0.56"'),('"1053", "1054", version}','"1053", "1054", "1055", version}'),('PL ASCII patch up to 1.0.55','PL ASCII patch up to 1.0.56')]):
  s=once(s,to,from_)
 if sha(s.encode('utf8'))!=BASE_API_MAIN_SHA:raise ValueError('API main Go source unexpectedly changed')
 guide=(mod/'CZYTAJ.txt').read_text('utf8')
 if not guide.startswith('STARSECTOR PL ASCII 1.0.56') or not guide.endswith(SUFFIX):raise ValueError('Player guide header/suffix changed')
 original_guide=once(guide[:-len(SUFFIX)],'STARSECTOR PL ASCII 1.0.56','STARSECTOR PL ASCII 1.0.55')
 if sha(original_guide.encode('utf8'))!=BASE_README_SHA:raise ValueError('Other player guide content changed')
 m=json.loads((mod/'mod_info.json').read_text('utf8'))
 if m.get('version')!='1.0.56' or m.get('gameVersion')!='0.98a-RC8' or len(m.get('replace',[]))!=41:
  raise ValueError('Mod metadata mismatch')
 if 'const edition = "1.0.56"' not in (worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer version not updated')
 return {'version':'1.0.56','rows_total':11107,'changed_dialogue_rows':EXPECTED_ENTRIES,'removed_gender_variables':EXPECTED_ENTRIES,
  'remaining_gender_tokens':2165,'remaining_affected_rows':1029,'rules_sha256':NEW_RULES_SHA,
  'unchanged_other_game_data':869,'unchanged_api_map_entries':5298,'obf_map_entries':3537,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('worktree',type=Path);args=parser.parse_args();print(json.dumps(check(args.worktree),indent=2))
