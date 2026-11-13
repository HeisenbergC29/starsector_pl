#!/usr/bin/env python3
"""Starsector PL 1.0.50: eight class-specific, text-only duration fragments.

Fixes BaseIntelPlugin's shared UI timing strings without touching Java bytecode,
identifier literals or any other API translation. 'day(s)' is also returned by
getDaysString() in downstream notifications such as PromoteOfficerIntel.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
OLD='TLUMACZENIA_JAR_1049.csv';NEW='TLUMACZENIA_JAR_1050.csv'
OLD_SHA='3ae9e6c3e8675139a9aa3bc91ca88f32fc2b65301f5b7657e8936c85d81c5420'
CLASS='com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin'
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
CHANGES={'day':'dzien','days':'dni','month':'mies.','months':'mies.',
         'cycle':'cyk.','cycles':'cyk.',' and ':' i ',' ago.':' temu.'}
EXPECTED_LDC={'day':4,'days':4,'month':2,'months':2,'cycle':1,'cycles':1,' and ':2,' ago.':1}
STATUS='REVIEWED_SHARED_DYNAMIC_DURATION_1050'
def sha(b):return hashlib.sha256(b).hexdigest()
def once(t,a,b):
 if t.count(a)!=1:raise ValueError(('Expected exactly one',a,t.count(a)))
 return t.replace(a,b)
def readmap(p):
 with Path(p).open('r',encoding='utf8',newline='') as f:
  r=csv.DictReader(f)
  if r.fieldnames!=FIELDS:raise ValueError('Source map columns changed')
  return list(r)
def serialize(rows):
 s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
 return s.getvalue().encode('utf8')
def plan(rows):
 if len(rows)!=5261:raise ValueError('Expected 5261 previous API rows')
 ids={(r['source_class'],r['english_literal']) for r in rows}
 if len(ids)!=5261:raise ValueError('Duplicate prior mapping keys')
 if any((CLASS,x) in ids for x in CHANGES):raise ValueError('One of the duration fragments was already patched')
 if len(CHANGES)!=8 or sum(EXPECTED_LDC.values())!=17:raise ValueError('Duration plan drift')
 if not all(a.isascii() and b.isascii() and a.strip() and b.strip() and a[:1].isspace()==b[:1].isspace() and a[-1:].isspace()==b[-1:].isspace() for a,b in CHANGES.items()):raise ValueError('Unapproved duration change')
 return [dict(source_class=CLASS,english_literal=eng,polish_ascii_draft=pl,status=STATUS) for eng,pl in CHANGES.items()]
def generate(root):
 root=Path(root);folder=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=folder/OLD;new=folder/NEW
 if new.exists():raise FileExistsError(new)
 if sha(old.read_bytes())!=OLD_SHA:raise ValueError('Unexpected 1.0.49 map SHA')
 rows=readmap(old)
 if serialize(rows)!=old.read_bytes():raise ValueError('Input map did not round-trip byte-exactly')
 changes=plan(rows);new.write_bytes(serialize(rows+changes))
 def change(path,pairs):
  p=root/path;s=p.read_text('utf8')
  for before,after in pairs:s=once(s,before,after)
  p.write_text(s,encoding='utf8')
 change('buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go',[
  ('const version = "1049"','const version = "1050"'),
  ('const exeVersion = "1.0.49"','const exeVersion = "1.0.50"'),
  ('"1047", "1048", version}','"1047", "1048", "1049", version}'),
  ('PL ASCII patch up to 1.0.49','PL ASCII patch up to 1.0.50')])
 change('buildtools/NARZEDZIA_INSTALATOR/main.go',[('const edition = "1.0.49"','const edition = "1.0.50"')])
 p=root/'mod/mod_info.json';info=json.loads(p.read_text('utf8'))
 if info['version']!='1.0.49' or info['gameVersion']!='0.98a-RC8':raise ValueError('Wrong prior mod release')
 info['version']='1.0.50';info['description']=once(info['description'],'1.0.49','1.0.50')
 p.write_text(json.dumps(info,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
 change('mod/CZYTAJ.txt',[('STARSECTOR PL ASCII 1.0.49','STARSECTOR PL ASCII 1.0.50')])
 with (root/'mod/CZYTAJ.txt').open('a',encoding='utf8') as out:
  out.write('\nPoprawiono 8 wspolnych fragmentow czasu w dzienniku floty i opisach intel: dni, miesiace, cykle oraz skladanie z "i" / "temu". Poprawka nie zmienia identyfikatorow ani kodu gry. Wersja 1.1 nadal w opracowaniu.\n')
 return {'version':'1.0.50','map_rows':5269,'new_class_scoped_fragments':8,'changed_classes':1,
         'expected_duration_ldc_uses':17,'new_map_sha256':sha(new.read_bytes()),
         'english_tokens_unchanged':True,'java_bytecode_unchanged':True,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(generate(a.worktree),indent=2))
