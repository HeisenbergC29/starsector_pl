#!/usr/bin/env python3
"""Starsector PL 1.0.49: class-scoped grammar fixes, including the shared English 's' plural suffix.

One new CONSTANT_String translation ('s' -> '') is authorized ONLY for SalvorsTallyIntel;
its six ldc callsites were independently inspected on original JVM instructions.
Do not confuse this with shared 'her' in BaseBarEventWithPerson, which remains open.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

OLD='TLUMACZENIA_JAR_1048.csv';NEW='TLUMACZENIA_JAR_1049.csv'
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
OLD_SHA='2f85b133be0d3087321d16dd71080f5214cf9e2932cc60381ecbab521b273289'
PLAN_PATH=Path(__file__).resolve().parent.parent/'docs/API_TEXT_CORRECTIONS_1049.json'
SALVOR='com.fs.starfarer.api.impl.campaign.intel.misc.SalvorsTallyIntel'
def sha(b):return hashlib.sha256(b).hexdigest()
def once(text,old,new):
 if text.count(old)!=1:raise ValueError(('expected one match',old,text.count(old)))
 return text.replace(old,new)
def readmap(path):
 with Path(path).open(encoding='utf8',newline='') as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=FIELDS:raise ValueError('Unexpected API map columns')
  return list(reader)
def serialize(rows):
 import io
 s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
 return s.getvalue().encode('utf8')
def plan(rows,plan_path=PLAN_PATH):
 plan=json.loads(Path(plan_path).read_text('utf8'))
 if plan['version']!='1.0.49' or plan['base_map_sha256']!=OLD_SHA:raise ValueError('Review plan wrong version')
 items=plan['changes'];keys=set();existing={};added=[]
 if len(rows)!=5260 or len(items)!=14:raise ValueError('Wrong review scope')
 for obj in items:
  cl,en,orig,dest,status=[obj[k] for k in ('source_class','english_literal','previous_polish','new_polish','status')]
  key=cl,en
  if key in keys or not cl.startswith('com.fs.starfarer.') or not dest.isascii():raise ValueError('Duplicate/invalid review key')
  keys.add(key)
  if orig is None:
   if (cl,en,dest)!=(SALVOR,'s','') or added:raise ValueError('Unexpected new JVM suffix translation')
   added.append(obj)
  else:
   if orig==dest or not orig.isascii():raise ValueError('Ineffective/new non-ASCII')
   for token in ('%s','%d','%f','%%','\t','\n'):
    if orig.count(token)!=dest.count(token) or orig.count(token)!=en.count(token):raise ValueError(('Marker changed',key,token))
   if orig[:1].isspace()!=dest[:1].isspace() or orig[-1:].isspace()!=dest[-1:].isspace():raise ValueError('Boundary whitespace changed')
   existing[key]=obj
 if len(existing)!=13 or len({x[0] for x in keys})!=7 or len(added)!=1:raise ValueError('Incorrect target inventory')
 index={(r['source_class'],r['english_literal']):r for r in rows}
 if len(index)!=len(rows):raise ValueError('Source map has duplicate keys')
 if (SALVOR,'s') in index:raise ValueError('Suffix already patched')
 for key,obj in existing.items():
  if key not in index:raise ValueError(('Missing translation to fix',key))
  r=index[key]
  if r['polish_ascii_draft']!=obj['previous_polish'] or r['status']!=obj['status']:raise ValueError(('Wrong original translation/status',key))
 return existing,added[0],items

def generate(root,plan_path=PLAN_PATH):
 root=Path(root);table=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations';old=table/OLD;new=table/NEW
 if new.exists():raise FileExistsError(new)
 if sha(old.read_bytes())!=OLD_SHA:raise ValueError('Wrong old map baseline')
 rows=readmap(old)
 if serialize(rows)!=old.read_bytes():raise ValueError('CSV input not roundtrippable byte-for-byte')
 edits,extra,items=plan(rows,plan_path)
 for r in rows:
  obj=edits.get((r['source_class'],r['english_literal']))
  if obj is not None:r['polish_ascii_draft']=obj['new_polish']
 rows.append(dict(source_class=extra['source_class'],english_literal=extra['english_literal'],polish_ascii_draft=extra['new_polish'],status=extra['status']))
 new.write_bytes(serialize(rows))
 def change(path,pairs):
  f=root/path;before=f.read_text('utf8');after=before
  for a,b in pairs:after=once(after,a,b)
  f.write_text(after,encoding='utf8')
 change('buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go',[
   ('const version = "1048"','const version = "1049"'),
   ('const exeVersion = "1.0.48"','const exeVersion = "1.0.49"'),
   ('"1046", "1047", version}', '"1046", "1047", "1048", version}'),
   ('PL ASCII patch up to 1.0.48','PL ASCII patch up to 1.0.49')])
 change('buildtools/NARZEDZIA_INSTALATOR/main.go',[('const edition = "1.0.48"','const edition = "1.0.49"')])
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
 if meta['version']!='1.0.48' or meta['gameVersion']!='0.98a-RC8':raise ValueError('Invalid mod metadata baseline')
 meta['version']='1.0.49';meta['description']=once(meta['description'],'1.0.48','1.0.49')
 p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 change('mod/CZYTAJ.txt',[('STARSECTOR PL ASCII 1.0.48','STARSECTOR PL ASCII 1.0.49')])
 with (root/'mod/CZYTAJ.txt').open('a',encoding='utf8') as f:
  f.write('\nPoprawiono liczbe i odmiane w zestawieniu odzysku, opisach misji, piechoty morskiej i zasiegu czujnikow. Usunieto angielska koncowke -s dopisywana do polskich etykiet odzysku. Wersja 1.1 nadal nieukonczona.\n')
 return {'release':'1.0.49','existing_rows_fixed':len(edits),'new_suffix_map_rows':1,
         'changed_classes':7,'map_rows':len(rows),'map_sha256':sha(new.read_bytes()),
         'original_map_sha256':OLD_SHA,'data_files_unchanged':870,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--plan',type=Path,default=PLAN_PATH)
 a=p.parse_args();print(json.dumps(generate(a.worktree,a.plan),indent=2))
