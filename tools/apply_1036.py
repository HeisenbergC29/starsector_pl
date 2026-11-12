#!/usr/bin/env python3
"""Starsector PL 1.0.36: translate the sole getHimOrHerself() caller.

Localized JVM literal strings only. Do not modify game bytecode, Java
method implementations, identifiers, or data/campaign/rules.csv.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

FIELDS=['source_class','english_literal','polish_ascii_draft','status']
STATUS='VERIFIED_REFLEXIVE_PRONOUN_1036'
BASE='com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson'
EVENT='com.fs.starfarer.api.impl.campaign.intel.bar.events.PlanetaryShieldBarEvent'
NEW={
 BASE:{'himself':'on','herself':'ona'},
}
CORRECT={
 EVENT:{
  ' did not live the experience in such ':' po tych wydarzeniach jest w znacznie gorszym stanie',
  'stride as ':' niz ',
  ', and has taken to drinking themselves senseless ':', a od tamtej pory upija sie do nieprzytomnosci ',
  'I wouldn\'t wish my fate on you or anyone. Besides, I have no idea." A pause, then, ':
    'Tego losu nie zycze tobie ani nikomu innemu. Poza tym nie mam pojecia." Po chwili ciszy ',
 }
}

def one(s,a,b):
 if s.count(a)!=1:raise AssertionError(('single replacement expected',a,s.count(a)))
 return s.replace(a,b)

def rows(path):
 with path.open(encoding='utf8',newline='') as f:
  r=csv.DictReader(f);assert r.fieldnames==FIELDS
  return list(r)

def update_mapping(src,dst):
 assert not dst.exists()
 rr=rows(src);assert len(rr)==5242
 index={(r['source_class'],r['english_literal']):r for r in rr}
 assert len(index)==len(rr)
 for cl,items in CORRECT.items():
  for en,pl in items.items():
   r=index[(cl,en)]
   assert r['status']=='DRAFT_ONLY_NOT_INSTALLED' and en!=pl and pl.isascii()
   r['polish_ascii_draft']=pl # preserve source and historic status, audit in the review ledger
 for cl,items in NEW.items():
  for en,pl in items.items():
   assert (cl,en) not in index and pl.isascii() and en!=pl
   rr.append({'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
 assert len(rr)==5244
 with dst.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rr)
 return {'old':5242,'new':5244,'added':2,'corrected':4}

def main(root):
 a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 report=update_mapping(a/'translations/TLUMACZENIA_JAR_1033.csv', a/'translations/TLUMACZENIA_JAR_1036.csv')
 p=a/'main.go';s=p.read_text('utf8')
 s=one(s,'const version = "1033"','const version = "1036"')
 s=one(s,'const exeVersion = "1.0.33"','const exeVersion = "1.0.36"')
 s=one(s,'"1030", "1032", version}','"1030", "1032", "1033", version}')
 s=one(s,'PL ASCII patch up to 1.0.33','PL ASCII patch up to 1.0.36')
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';s=p.read_text('utf8')
 p.write_text(one(s,'const edition = "1.0.35"','const edition = "1.0.36"'),'utf8')
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'));assert meta['version']=='1.0.35'
 meta['version']='1.0.36';meta['description']=one(meta['description'],'1.0.35','1.0.36')
 p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
 s=one(s,'STARSECTOR PL ASCII 1.0.35','STARSECTOR PL ASCII 1.0.36')
 s+='\nPoprawiono skladane zdanie o starym kosmonaucie i pilocie dla obu plci, bez zmian kodu Java.\n'
 p.write_text(s,'utf8')
 print(json.dumps(report,indent=2))
 return report
if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('worktree',type=Path)
 main(pa.parse_args().worktree)
