#!/usr/bin/env python3
"""Starsector PL 1.0.56: 110 exact gender-neutral dialogue text edits.

Each rule is pinned by ID and by SHA-256 of its entire original text field.
Patch at the CSV-cell byte level. IDs, conditions, scripts, options and notes
remain byte-for-byte unchanged. Never blindly translate dynamic identifiers.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BASE_RULES_SHA='e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a'
PLAN_FILE='docs/RULES_NEUTRAL_REVIEW_1056.json'
EXPECTED_ENTRIES=110
DYNAMIC=re.compile(r'\$[A-Za-z_0-9]*(?:heOrShe|hisOrHer|himOrHer|himOrHerself|manOrWoman)\b',re.I)

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()
def once(s:str,a:str,b:str)->str:
 if s.count(a)!=1:raise ValueError(('Expected unique source anchor',a[:100],s.count(a)))
 return s.replace(a,b)

def field_spans(s:str)->list[tuple[int,int]]:
 """Find original lexical CSV fields without re-encoding untouched cells."""
 found=[];start=0;quoted=False;i=0
 while i<len(s):
  ch=s[i]
  if ch=='"':
   if quoted and i+1<len(s) and s[i+1]=='"':i+=2;continue
   quoted=not quoted
  elif ch==',' and not quoted:
   found.append((start,i));start=i+1
  elif ch in '\r\n' and not quoted:
   found.append((start,i));break
  i+=1
 if i==len(s) and not s.endswith(('\r','\n')):found.append((start,len(s)))
 if quoted or len(found) not in (6,7):raise ValueError(('Unsafe CSV record structure',len(found),quoted))
 return found

def decode_field(raw:str)->str:
 if raw.startswith('"') and raw.endswith('"'):return raw[1:-1].replace('""','"')
 return raw

def encode_like(raw:str,value:str)->str:
 if raw.startswith('"') and raw.endswith('"'):
  return '"'+value.replace('"','""')+'"'
 if any(c in value for c in ',\r\n"'):
  raise ValueError('Unquoted CSV cell would require serialization changes')
 return value

def read_plan(path:Path)->dict:
 raw=path.read_bytes();plan=json.loads(raw)
 if plan.get('base_rules_sha256')!=BASE_RULES_SHA or plan.get('proposed_release')!='1.0.56':
  raise ValueError('Invalid or mismatched 1.0.56 review plan')
 records=plan['records'];keys=[r['id'] for r in records]
 if len(records)!=EXPECTED_ENTRIES or len(set(keys))!=len(keys):raise ValueError('Review ledger count/IDs invalid')
 if sum(r['kind']=='speech_tag_elision' for r in records)!=71 or sum(r['kind']=='possessive_neutralization' for r in records)!=39:
  raise ValueError('Review ledger group sizes changed')
 return {r['id']:r for r in records}

def patch_rules(src:bytes,plan:dict)->tuple[bytes,dict]:
 if len(plan)!=EXPECTED_ENTRIES:raise ValueError('Inconsistent review map cardinality')
 if sha(src)!=BASE_RULES_SHA:raise ValueError('Requires exact v1.0.55 rules.csv input')
 data=src.decode('ascii');lines=data.splitlines(keepends=True)
 reader=csv.reader(io.StringIO(data,newline=''))
 before=0;pieces=[];seen=set();num_rows=0;removed=0
 for row in reader:
  segment=''.join(lines[before:reader.line_num]);before=reader.line_num
  slices=field_spans(segment)
  if len(row)!=len(slices):raise ValueError(('CSV lexical/parser disagreement',num_rows))
  for ix,(start,end) in enumerate(slices):
   if decode_field(segment[start:end])!=row[ix]:raise ValueError(('CSV content discrepancy',num_rows,ix))
  if num_rows==0:
   if row!=['id','trigger','conditions','script','text','options','notes']:raise ValueError('Unexpected CSV header')
  elif row[0] in plan:
   ident=row[0];p=plan[ident]
   if ident in seen:raise ValueError(('Duplicate reviewed ID',ident))
   seen.add(ident)
   text=row[4]
   if sha(text.encode('ascii'))!=p['old_text_sha256']:raise ValueError(('Review entry original text mismatch',ident))
   initial=DYNAMIC.findall(text)
   if len(initial)!=1:raise ValueError(('Wrong number of gender placeholders',ident,initial))
   for a,b in p['edits']:
    text=once(text,a,b)
   if sha(text.encode('ascii'))!=p['new_text_sha256']:raise ValueError(('Review entry translated text mismatch',ident))
   if DYNAMIC.findall(text):raise ValueError(('Unremoved gender placeholder',ident))
   if (len(initial)-len(DYNAMIC.findall(text)))!=1:raise ValueError(('Gender counts changed',ident))
   if any(text.count(marker)!=row[4].count(marker) for marker in ['%s','%d','%f','\r\n','\n','"',' OR ','\t']):
    raise ValueError(('Dialogue structural tokens changed',ident))
   dyn=lambda t:re.findall(r'\$[A-Za-z_0-9]+(?:\.[A-Za-z_0-9]+)*',t)
   a=[x for x in dyn(row[4]) if not DYNAMIC.fullmatch(x)]
   b=[x for x in dyn(text) if not DYNAMIC.fullmatch(x)]
   if a!=b:raise ValueError(('Other dialogue variables changed',ident,a,b))
   lo,hi=slices[4];segment=segment[:lo]+encode_like(segment[lo:hi],text)+segment[hi:]
   changed=list(csv.reader(io.StringIO(segment,newline='')))
   if len(changed)!=1 or changed[0][:4]!=row[:4] or changed[0][5:]!=row[5:] or changed[0][4]!=text:
    raise ValueError(('CSV data outside text field changed',ident))
   removed+=1
  pieces.append(segment);num_rows+=1
 if before!=len(lines) or num_rows!=11108 or seen!=set(plan):raise ValueError(('Review coverage failure',num_rows,len(seen),set(plan)-seen))
 out=''.join(pieces).encode('ascii')
 if len(list(csv.reader(io.StringIO(out.decode('ascii'),newline=''))))!=11108:raise ValueError('CSV row count drift')
 return out,{'changed_rows':len(seen),'removed_gender_placeholders':removed,'rows':num_rows-1,'before_sha256':sha(src),'after_sha256':sha(out)}

def apply(worktree:Path,repo_root:Path=ROOT)->dict:
 worktree=Path(worktree);plan=read_plan(repo_root/PLAN_FILE)
 csvpath=worktree/'mod/data/campaign/rules.csv'
 after,result=patch_rules(csvpath.read_bytes(),plan)
 csvpath.write_bytes(after)
 api=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 translation=api/'translations';oldmap=translation/'TLUMACZENIA_JAR_1055.csv';newmap=translation/'TLUMACZENIA_JAR_1056.csv'
 if newmap.exists():raise FileExistsError('The immutable 1056 API map is already installed')
 if sha(oldmap.read_bytes())!='c45d1e8e33240b7716e94b9e5ca1f3ae7b74eb1314db38fb57f146b85b863848':raise ValueError('Wrong baseline API map')
 newmap.write_bytes(oldmap.read_bytes())  # API text not changed in this release
 source=api/'main.go';s=source.read_text('utf8')
 for a,b in [
  ('const version = "1055"','const version = "1056"'),
  ('const exeVersion = "1.0.55"','const exeVersion = "1.0.56"'),
  ('"1053", "1054", version}','"1053", "1054", "1055", version}'),
  ('PL ASCII patch up to 1.0.55','PL ASCII patch up to 1.0.56')]:
  s=once(s,a,b)
 source.write_text(s,encoding='utf8')
 inst=worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=inst.read_text('utf8')
 inst.write_text(once(s,'const edition = "1.0.55"','const edition = "1.0.56"'),encoding='utf8')
 manifest=worktree/'mod/mod_info.json';info=json.loads(manifest.read_text('utf8'))
 if info.get('version')!='1.0.55' or info.get('gameVersion')!='0.98a-RC8':raise ValueError('Wrong prior mod manifest')
 info['version']='1.0.56';info['description']=once(info['description'],'1.0.55','1.0.56')
 manifest.write_text(json.dumps(info,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 guide=worktree/'mod/CZYTAJ.txt';text=guide.read_text('utf8')
 text=once(text,'STARSECTOR PL ASCII 1.0.55','STARSECTOR PL ASCII 1.0.56')
 text+='\nW 110 dialogach usunieto zbedne zmienne zalazne od plci z narracji (mowi, odpowiada, okreslenia twarzy i gestow). Skrypty, warunki i opcje dialogow niezmienione.\n'
 guide.write_text(text,encoding='utf8')
 return {'version':'1.0.56',**result,'unchanged_api_map_entries':5298,'unchanged_obf_map_entries':3537,'native_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(apply(a.worktree),indent=2))
