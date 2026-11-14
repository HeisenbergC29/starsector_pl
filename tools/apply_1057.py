#!/usr/bin/env python3
"""1.0.57: 70 SHA-pinned, context-reviewed Polish reflexive-gesture corrections.

Only the text cell in a known rules.csv record may change. Nothing alters any
rule ID, script, condition, option, class mapping or JVM executable bytecode.
All originals and fully revised fields are recorded in the public audit ledger.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re
from pathlib import Path
from apply_1056 import field_spans,decode_field,encode_like,once,DYNAMIC

ROOT=Path(__file__).resolve().parent.parent
PLAN_FILE='docs/RULES_REFLEXIVE_REVIEW_1057.json'
BASE_RULES_SHA='a08330e67de037fc0df66447c039ec7ac6792340405d2983c04e31f2bfef4810'
LEDGER_SHA='ae5d3c1b52111f4e45d1f97c26282493a2fcd4c1d43580ebd5f16dab0902bdf3'
BASE_API_MAP_SHA='c45d1e8e33240b7716e94b9e5ca1f3ae7b74eb1314db38fb57f146b85b863848'
EXPECTED_ROWS=70
EXPECTED_PHRASES=74
EXPECTED_REMOVED=76
SUFFIX='\nW 70 dialogach poprawiono skladnie opisow gestow i ruchow ciala: usunieto 76 zbednych zmiennych dzierzawczych. Inne dane i logika gry sa nietkniete.\n'

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()

def read_plan(root:Path=ROOT)->dict:
 raw=(Path(root)/PLAN_FILE).read_bytes()
 if sha(raw)!=LEDGER_SHA:raise ValueError('Unapproved review-ledger modification')
 d=json.loads(raw)
 if (d.get('source_release'),d.get('proposed_release'),d.get('base_rules_sha256'))!=('1.0.56','1.0.57',BASE_RULES_SHA):
  raise ValueError('Wrong source version for approved 1057 plan')
 entries=d.get('records',[])
 if len(entries)!=EXPECTED_ROWS or len({x['id'] for x in entries})!=EXPECTED_ROWS:
  raise ValueError('Wrong or duplicate dialogue IDs')
 if sum(len(x['edits']) for x in entries)!=EXPECTED_PHRASES or sum(x['removed_gender_placeholders'] for x in entries)!=EXPECTED_REMOVED:
  raise ValueError('Review statistics were changed')
 expected={p['before']:p for p in d.get('patterns',[])}
 if len(expected)!=15 or len({(a,b) for e in entries for a,b in e['edits']})!=15:
  raise ValueError('Unreviewed transformation pattern')
 for r in entries:
  if r.get('kind')!='reflexive_body_gesture' or r['id'].startswith('#'):
   raise ValueError(('Forbidden or non-visible rule ID',r['id']))
  old,new=r['original_text'],r['revised_text']
  if sha(old.encode('ascii'))!=r['old_text_sha256'] or sha(new.encode('ascii'))!=r['new_text_sha256']:
   raise ValueError(('Review field checksum mismatch',r['id']))
  rendered=old
  for a,b in r['edits']:
   if a not in expected or b!=expected[a]['after']:
    raise ValueError(('Unexpected replacement pair',r['id'],a,b))
   rendered=once(rendered,a,b)
  if rendered!=new or len(DYNAMIC.findall(old))-len(DYNAMIC.findall(new))!=r['removed_gender_placeholders']:
   raise ValueError(('Bad contextual translation',r['id']))
 for source,p in expected.items():
  if sum(1 for r in entries for a,b in r['edits'] if a==source)!=p['occurrences']:
   raise ValueError(('Pattern-count mismatch',source))
 return {x['id']:x for x in entries}

def patch_rules(src:bytes,plan:dict)->tuple[bytes,dict]:
 if sha(src)!=BASE_RULES_SHA:raise ValueError('Requires exact v1.0.56 rules.csv')
 data=src.decode('ascii'); lines=data.splitlines(keepends=True)
 reader=csv.reader(io.StringIO(data,newline=''))
 previous=0;parts=[];seen=set();rows=0;phrases=0;removed=0
 for row in reader:
  segment=''.join(lines[previous:reader.line_num]);previous=reader.line_num
  spans=field_spans(segment)
  if len(row)!=len(spans):raise ValueError(('Invalid CSV lexical layout',rows))
  if rows==0 and row!=['id','trigger','conditions','script','text','options','notes']:
   raise ValueError('Unexpected CSV header')
  if rows and row[0] in plan:
   ident=row[0]
   if ident in seen:raise ValueError(('Duplicate dialogue ID',ident))
   seen.add(ident);approved=plan[ident]
   text=row[4]
   if text!=approved['original_text'] or sha(text.encode('ascii'))!=approved['old_text_sha256']:
    raise ValueError(('Unexpected original dialogue',ident))
   revised=text
   for old,new in approved['edits']:
    revised=once(revised,old,new)
   if revised!=approved['revised_text'] or sha(revised.encode('ascii'))!=approved['new_text_sha256']:
    raise ValueError(('Output not reviewed',ident))
   for marker in ('%s','%d','%f','\r\n','\n','"',' OR ','\t'):
    if text.count(marker)!=revised.count(marker):raise ValueError(('Technical markup altered',ident,marker))
   vars_=lambda s:[x for x in re.findall(r'\$[A-Za-z_0-9]+(?:\.[A-Za-z_0-9]+)*',s) if not DYNAMIC.fullmatch(x)]
   if vars_(text)!=vars_(revised):raise ValueError(('Other script variable changed',ident))
   delta=len(DYNAMIC.findall(text))-len(DYNAMIC.findall(revised))
   if delta!=approved['removed_gender_placeholders']:raise ValueError(('Gender marker mismatch',ident))
   lo,hi=spans[4]
   if decode_field(segment[lo:hi])!=text:raise ValueError(('Text quote mismatch',ident))
   new_segment=segment[:lo]+encode_like(segment[lo:hi],revised)+segment[hi:]
   changed=list(csv.reader(io.StringIO(new_segment,newline='')))
   if len(changed)!=1 or changed[0][:4]!=row[:4] or changed[0][5:]!=row[5:] or changed[0][4]!=revised:
    raise ValueError(('Non-text field altered',ident))
   segment=new_segment;phrases+=len(approved['edits']);removed+=delta
  parts.append(segment);rows+=1
 if rows!=11108 or previous!=len(lines) or seen!=set(plan):
  raise ValueError(('Incomplete review coverage',rows,len(seen),len(plan)-len(seen)))
 if (len(seen),phrases,removed)!=(EXPECTED_ROWS,EXPECTED_PHRASES,EXPECTED_REMOVED):
  raise ValueError('Output counters do not match review')
 out=''.join(parts).encode('ascii')
 return out,{'rows_total':11107,'changed_dialogue_rows':len(seen),'corrected_grammar_fragments':phrases,
  'removed_gender_placeholders':removed,'base_rules_sha256':sha(src),'new_rules_sha256':sha(out)}

def apply(worktree:Path,root:Path=ROOT)->dict:
 worktree=Path(worktree);plan=read_plan(root)
 rules=worktree/'mod/data/campaign/rules.csv'
 updated,report=patch_rules(rules.read_bytes(),plan)
 api=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old=api/'translations/TLUMACZENIA_JAR_1056.csv';new=api/'translations/TLUMACZENIA_JAR_1057.csv'
 if new.exists() or sha(old.read_bytes())!=BASE_API_MAP_SHA:
  raise ValueError('Cannot safely upgrade the v1.0.56 API map')
 source=api/'main.go';go=source.read_text('utf8')
 for a,b in [
  ('const version = "1056"','const version = "1057"'),
  ('const exeVersion = "1.0.56"','const exeVersion = "1.0.57"'),
  ('"1055", version}','"1055", "1056", version}'),
  ('PL ASCII patch up to 1.0.56','PL ASCII patch up to 1.0.57')]:go=once(go,a,b)
 installer=worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 ins=once(installer.read_text('utf8'),'const edition = "1.0.56"','const edition = "1.0.57"')
 manifest=worktree/'mod/mod_info.json';m=json.loads(manifest.read_text('utf8'))
 if m.get('version')!='1.0.56' or m.get('gameVersion')!='0.98a-RC8':raise ValueError('Wrong mod baseline')
 m['version']='1.0.57';m['description']=once(m['description'],'1.0.56','1.0.57')
 readme=worktree/'mod/CZYTAJ.txt';guide=once(readme.read_text('utf8'),'STARSECTOR PL ASCII 1.0.56','STARSECTOR PL ASCII 1.0.57')+SUFFIX
 # Only write after all textual conditions pass.
 rules.write_bytes(updated);new.write_bytes(old.read_bytes());source.write_text(go,encoding='utf8')
 installer.write_text(ins,encoding='utf8');manifest.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 readme.write_text(guide,encoding='utf8')
 return {'version':'1.0.57',**report,'api_map_entries':5298,'obf_map_entries':3537,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(apply(a.worktree),indent=2))
