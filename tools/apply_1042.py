#!/usr/bin/env python3
"""Starsector 1.0.42: fix 15 double periods introduced by abbreviated units in 1.0.41.

Exactly 15 class-scoped translations; no bytecode/English/ID/status/game data changed.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path

OLD='TLUMACZENIA_JAR_1041.csv'
NEW='TLUMACZENIA_JAR_1042.csv'
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
PATTERN=re.compile(r'(%s (?:jedn\.|l\. sw\.))\.(?!\.)')
PLAN_SHA='fc7bf29cfc7f327342060c7a6eb36f3662d72d2cd097431c6141c9b32ff2a761'

def readmap(path):
 with path.open(encoding='utf8',newline='') as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=FIELDS:raise ValueError('unexpected mapping columns')
  return list(reader)

def plan(rows):
 affected=[]
 for row in rows:
  old=row['polish_ascii_draft']
  new,n=PATTERN.subn(r'\1',old)
  if not n:continue
  if n!=1:raise AssertionError(('multiple punctuation changes in same text',row['source_class']))
  if row['source_class'].startswith('data/') or row['english_literal'].count('%s')!=new.count('%s') or new.count('%s')!=old.count('%s'):raise AssertionError('source/format mismatch')
  if (old.startswith(' ')!=new.startswith(' ') or old.endswith(' ')!=new.endswith(' ') or old.count('\n')!=new.count('\n') or not new.isascii()):raise AssertionError('layout drift')
  affected.append((row['source_class'],row['english_literal'],old,new,row['status']))
 groups={'unit':sum('jedn..' in x[2] for x in affected),'light_year':sum('l. sw..' in x[2] for x in affected)}
 h=hashlib.sha256(json.dumps(affected,ensure_ascii=True,separators=(',',':')).encode('ascii')).hexdigest()
 if len(affected)!=15 or groups!={'unit':11,'light_year':4} or h!=PLAN_SHA:raise AssertionError(('unexpected exact inventory',len(affected),groups,h))
 if len({(a,b) for a,b,*_ in affected})!=15:raise AssertionError('duplicate source key')
 return affected,groups,h

def once(text,a,b):
 if text.count(a)!=1:raise AssertionError(('unexpected source occurrence',a,text.count(a)))
 return text.replace(a,b)

def apply(root):
 root=Path(root)
 td=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 if (td/NEW).exists():raise FileExistsError(td/NEW)
 rows=readmap(td/OLD)
 if len(rows)!=5257:raise AssertionError('wrong mapping release')
 affected,groups,h=plan(rows)
 keyed={(a,b):d for a,b,c,d,e in affected}
 for row in rows:
  dst=keyed.get((row['source_class'],row['english_literal']))
  if dst is not None:row['polish_ascii_draft']=dst
 with (td/NEW).open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
 def edit(path,pairs):
  old=path.read_text('utf8');new=old
  for a,b in pairs:new=once(new,a,b)
  path.write_text(new,encoding='utf8')
 edit(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go',[
  ('const version = "1041"','const version = "1042"'),
  ('const exeVersion = "1.0.41"','const exeVersion = "1.0.42"'),
  ('"1038", "1040", version}','"1038", "1040", "1041", version}'),
  ('PL ASCII patch up to 1.0.41','PL ASCII patch up to 1.0.42'),
 ])
 edit(root/'buildtools/NARZEDZIA_INSTALATOR/main.go',[('const edition = "1.0.41"','const edition = "1.0.42"')])
 info=root/'mod/mod_info.json';v=json.loads(info.read_text('utf8'))
 if v['version']!='1.0.41':raise AssertionError('incorrect prior metadata version')
 v['version']='1.0.42';v['description']=once(v['description'],'1.0.41','1.0.42')
 info.write_text(json.dumps(v,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 readme=root/'mod/CZYTAJ.txt'
 edit(readme,[('STARSECTOR PL ASCII 1.0.41','STARSECTOR PL ASCII 1.0.42')])
 with readme.open('a',encoding='utf8') as f:f.write('\nPoprawiono 15 przypadkow podwojnej kropki po skrotach jedn. i l. sw. z wersji 1.0.41. Kod gry i pozostale teksty niezmienione.\n')
 print(json.dumps({'release':'1.0.42','corrected_punctuation':len(affected),'groups':groups,'plan_sha256':h,'rows':len(rows)},indent=2))

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path)
 apply(a.parse_args().worktree)
