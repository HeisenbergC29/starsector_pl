#!/usr/bin/env python3
"""v1.0.58: SHA-anchored Polish speech-attribution fixes, data-only.

Changes exclusively approved rules.csv text cells. No script, conditions,
options, rule IDs or Java bytecode are translated/modified.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re
from pathlib import Path
from apply_1056 import DYNAMIC,field_spans,decode_field,encode_like,once

ROOT=Path(__file__).resolve().parents[1]
PLAN='docs/RULES_SPEECH_REVIEW_1058.json'
PLAN_SHA='25b3eca81e41717fbfda5dafb36eb6f5c929eb920885ca2e55c1f340bac989c7'
BASE_RULES_SHA='693b874b6738d792bbf5b74a9e247e594c607c1834a2822823a228511a311f6c'
BASE_API_MAP_SHA='c45d1e8e33240b7716e94b9e5ca1f3ae7b74eb1314db38fb57f146b85b863848'
EXPECTED_ROWS=122
EXPECTED_EDITS=136
SUFFIX='\nW 122 dialogach usunieto 136 zbednych zmiennych plciowych przy czasownikach wprowadzajacych wypowiedz. Zmieniono tylko teksty; mechanika gry i identyfikatory pozostaly bez zmian.\n'

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()

def read_plan(root:Path=ROOT)->dict:
 data=(Path(root)/PLAN).read_bytes()
 if sha(data)!=PLAN_SHA:raise ValueError('Unapproved 1058 review ledger bytes')
 d=json.loads(data)
 if (d.get('schema_version'),d.get('source_release'),d.get('proposed_release'),d.get('base_rules_sha256'))!=(1,'1.0.57','1.0.58',BASE_RULES_SHA):
  raise ValueError('Not an approved 1.0.57 -> 1.0.58 plan')
 rec=d.get('records',[])
 if len(rec)!=EXPECTED_ROWS or len({r['id'] for r in rec})!=EXPECTED_ROWS or sum(len(r['edits']) for r in rec)!=EXPECTED_EDITS:
  raise ValueError('Wrong number of unique IDs or edits')
 if d.get('removed_gender_placeholders')!=EXPECTED_EDITS or d.get('reviewed_previous_unique_rule_ids')!=433 or d.get('remaining_dynamic_placeholders')!=1953:
  raise ValueError('Inconsistent review accounting')
 for r in rec:
  if r['id'].startswith('#') or r['kind']!='speech_attribution_subject_elision' or r['removed_gender_placeholders']!=len(r['edits']):
   raise ValueError(('Unapproved row',r['id']))
  old,new=r['original_text'],r['revised_text']
  if not old.isascii() or not new.isascii() or sha(old.encode())!=r['old_text_sha256'] or sha(new.encode())!=r['new_text_sha256']:
   raise ValueError(('Bad reviewed text fingerprint',r['id']))
  spans=[];target=old
  for e in r['edits']:
   lo,hi=e['start'],e['end']; src,dst=e['before'],e['after']
   if lo<0 or hi>len(old) or lo>=hi or old[lo:hi]!=src or not src.endswith(' $heOrShe') and not src.endswith(' $HeOrShe'):
    raise ValueError(('Unexpected speech marker/offset',r['id']))
   if src[:-len(src.split()[-1])-1]!=dst or src.count('$')!=1 or old[:lo].count('"')%2!=0:
    raise ValueError(('Incorrect grammatical transformation',r['id']))
   spans.append((lo,hi))
  if spans!=sorted(spans) or any(a[1]>b[0] for a,b in zip(spans,spans[1:])):raise ValueError(('Overlapping text edit',r['id']))
  for e in reversed(r['edits']):target=target[:e['start']]+e['after']+target[e['end']:]
  if target!=new or len(DYNAMIC.findall(old))-len(DYNAMIC.findall(new))!=len(r['edits']):
   raise ValueError(('Text not exactly approved',r['id']))
 return {r['id']:r for r in rec}

def patch_rules(before:bytes,plan:dict)->tuple[bytes,dict]:
 if sha(before)!=BASE_RULES_SHA or len(plan)!=EXPECTED_ROWS:raise ValueError('Wrong pristine 1.0.57 dialogue baseline')
 raw=before.decode('ascii');lines=raw.splitlines(keepends=True)
 reader=csv.reader(io.StringIO(raw,newline=''))
 idx=0;pieces=[];seen=set();num=0;replaced=0
 for row in reader:
  segment=''.join(lines[idx:reader.line_num]);idx=reader.line_num
  spans=field_spans(segment)
  if len(spans)!=len(row):raise ValueError(('Unsupported source CSV quoting',num))
  if num==0 and row!=['id','trigger','conditions','script','text','options','notes']:
   raise ValueError('Unexpected dialogue columns')
  if num and row[0] in plan:
   ident=row[0];p=plan[ident]
   if ident in seen or row[4]!=p['original_text'] or sha(row[4].encode('ascii'))!=p['old_text_sha256']:
    raise ValueError(('Dialog ID duplicated or source content wrong',ident))
   seen.add(ident);text=row[4];revised=text
   for e in reversed(p['edits']):revised=revised[:e['start']]+e['after']+revised[e['end']:]
   if revised!=p['revised_text'] or sha(revised.encode('ascii'))!=p['new_text_sha256']:
    raise ValueError(('Unapproved output in dialogue',ident))
   for mark in ('%s','%d','%f','\r\n','\n','"',' OR ','\t'):
    if text.count(mark)!=revised.count(mark):raise ValueError(('Markup lost',ident,mark))
   others=lambda s:[x for x in re.findall(r'\$[A-Za-z_0-9]+(?:\.[A-Za-z_0-9]+)*',s) if not DYNAMIC.fullmatch(x)]
   if others(text)!=others(revised) or len(DYNAMIC.findall(text))-len(DYNAMIC.findall(revised))!=len(p['edits']):
    raise ValueError(('Variable behavior changed',ident))
   lo,hi=spans[4]
   if decode_field(segment[lo:hi])!=text:raise ValueError(('Text field quoting mismatch',ident))
   segment=segment[:lo]+encode_like(segment[lo:hi],revised)+segment[hi:]
   after=list(csv.reader(io.StringIO(segment,newline='')))
   if len(after)!=1 or after[0][:4]!=row[:4] or after[0][5:]!=row[5:] or after[0][4]!=revised:
    raise ValueError(('Rule metadata changed',ident))
   replaced+=len(p['edits'])
  pieces.append(segment);num+=1
 if num!=11108 or idx!=len(lines) or seen!=set(plan) or replaced!=EXPECTED_EDITS:
  raise ValueError(('Dialogue coverage incomplete',num,len(seen),replaced))
 out=''.join(pieces).encode('ascii')
 return out,{'version':'1.0.58','total_dialogues':11107,'corrected_dialogues':len(seen),'removed_gender_variables':replaced,'rules_before_sha256':sha(before),'rules_after_sha256':sha(out)}

def apply(worktree:Path,root:Path=ROOT)->dict:
 worktree=Path(worktree);plan=read_plan(root)
 rules=worktree/'mod/data/campaign/rules.csv';out,report=patch_rules(rules.read_bytes(),plan)
 api=worktree/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old=api/'translations/TLUMACZENIA_JAR_1057.csv';new=api/'translations/TLUMACZENIA_JAR_1058.csv'
 if new.exists() or sha(old.read_bytes())!=BASE_API_MAP_SHA:raise ValueError('Wrong API map baseline')
 source=api/'main.go';go=source.read_text('utf8')
 for a,b in [
  ('const version = "1057"','const version = "1058"'),
  ('const exeVersion = "1.0.57"','const exeVersion = "1.0.58"'),
  ('"1056", version}','"1056", "1057", version}'),
  ('PL ASCII patch up to 1.0.57','PL ASCII patch up to 1.0.58')]:go=once(go,a,b)
 installer=worktree/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 ins=once(installer.read_text('utf8'),'const edition = "1.0.57"','const edition = "1.0.58"')
 manifest=worktree/'mod/mod_info.json';m=json.loads(manifest.read_text('utf8'))
 if (m.get('version'),m.get('gameVersion'))!=('1.0.57','0.98a-RC8'):raise ValueError('Wrong mod version')
 m['version']='1.0.58';m['description']=once(m['description'],'1.0.57','1.0.58')
 guide=worktree/'mod/CZYTAJ.txt';intro=once(guide.read_text('utf8'),'STARSECTOR PL ASCII 1.0.57','STARSECTOR PL ASCII 1.0.58')+SUFFIX
 # Every precondition must pass before writing the first file.
 rules.write_bytes(out);new.write_bytes(old.read_bytes());source.write_text(go,encoding='utf8')
 installer.write_text(ins,encoding='utf8');manifest.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 guide.write_text(intro,encoding='utf8')
 return {**report,'api_map_entries':5298,'obf_map_entries':3537,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(apply(a.worktree),indent=2))
