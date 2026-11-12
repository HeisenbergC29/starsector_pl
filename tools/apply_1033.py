#!/usr/bin/env python3
"""Candidate Starsector PL 1.0.33: context-verified Misc.STORY -> PF.

Stage only after completing all 81 callsite reviews. No JVM executable-code edits.
"""
from __future__ import annotations
import argparse, csv, json, hashlib
from pathlib import Path
from story_pf_plan_1033 import API,OBF

FIELDS=['source_class','english_literal','polish_ascii_draft','status']
STATUS='VERIFIED_STORY_PF_1033'
PREV_OBF_SHA='291a0098153b058b5725a97a331d4e41763bef9ea33dbac42eea0d0a989f8722'
# filled after first independent patch of the original OBF jar
NEW_OBF_SHA='03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a'

def change_one(s,a,b):
 if s.count(a)!=1:raise AssertionError(('expected single occurrence',a,s.count(a)))
 return s.replace(a,b)

def apply_map(src,dest,edits):
 if dest.exists():raise FileExistsError(dest)
 with src.open(encoding='utf8',newline='') as f:
  rdr=csv.DictReader(f);assert rdr.fieldnames==FIELDS;rows=list(rdr)
 remaining={(cl,en) for cl,pairs in edits.items() for en in pairs}
 keys={(row['source_class'],row['english_literal']) for row in rows}
 edited=0
 for row in rows:
  cl,en=row['source_class'],row['english_literal']
  if en not in edits.get(cl,{}):continue
  pl=edits[cl][en]
  if row['polish_ascii_draft']==pl:raise AssertionError(('unchanged',cl,en))
  assert en.isascii() and pl.isascii(),(cl,en)
  row['polish_ascii_draft']=pl
  remaining.remove((cl,en));edited+=1
 for cl,en in sorted(remaining):
  if (cl,en) in keys:raise AssertionError(('conflict',cl,en))
  pl=edits[cl][en]
  assert en.isascii() and pl.isascii() and en!=pl
  rows.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 with dest.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
 return {'prior':len(rows)-len(remaining),'corrected':edited,'added':len(remaining),'total':len(rows)}

def main(root):
 o=root/'buildtools/NARZEDZIA_OBF'
 a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old_obf=o/'TLUMACZENIA_OBF_10130.csv';new_obf=o/'TLUMACZENIA_OBF_10133.csv'
 old_api=a/'translations/TLUMACZENIA_JAR_1032.csv';new_api=a/'translations/TLUMACZENIA_JAR_1033.csv'
 summary={'OBF':apply_map(old_obf,new_obf,OBF),'API':apply_map(old_api,new_api,API)}
 p=o/'main.go';s=p.read_text('utf8')
 s=change_one(s,'TLUMACZENIA_OBF_10129.csv TLUMACZENIA_OBF_10130.csv','TLUMACZENIA_OBF_10129.csv TLUMACZENIA_OBF_10130.csv TLUMACZENIA_OBF_10133.csv')
 s=change_one(s,'const currentPatchState = "patched 10130"','const currentPatchState = "patched 10133"')
 s=change_one(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"'+PREV_OBF_SHA+'": "10130",')
 s=change_one(s,'loadTranslations("TLUMACZENIA_OBF_10130.csv")','loadTranslations("TLUMACZENIA_OBF_10133.csv")')
 s=change_one(s,'state == currentPatchState || state == "patched 10129"','state == currentPatchState || state == "patched 10130" || state == "patched 10129"')
 s=change_one(s,'OBF 1.0.32 | stan:','OBF 1.0.33 | stan:')
 s=change_one(s,'1.0.30: Lokalizacja tekstow OBF','1.0.33: Lokalizacja tekstow OBF')
 s=change_one(s,'0.9.99-1.0.30; odmowa modyfikacji','0.9.99-1.0.33; odmowa modyfikacji')
 p.write_text(s,'utf8')
 p=o/'main_test.go';st=p.read_text('utf8')
 p.write_text(change_one(st,'alreadyThisRelease("patched 10130")','alreadyThisRelease("patched 10133")'),'utf8')
 p=a/'main.go';s=p.read_text('utf8')
 s=change_one(s,'const version = "1032"','const version = "1033"')
 s=change_one(s,'const exeVersion = "1.0.32"','const exeVersion = "1.0.33"')
 s=change_one(s,'"1029", "1030", version}','"1029", "1030", "1032", version}')
 s=change_one(s,'PL ASCII patch up to 1.0.32','PL ASCII patch up to 1.0.33')
 s=change_one(s,'const expectedOBFPatched10130 = "'+PREV_OBF_SHA+'"','const expectedOBFPatched10130 = "'+PREV_OBF_SHA+'"\nconst expectedOBFPatched10133 = "'+NEW_OBF_SHA+'"')
 s=change_one(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10130','hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10133 && hash(obf) != expectedOBFPatched10130')
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 p.write_text(change_one(p.read_text('utf8'),'const edition = "1.0.32"','const edition = "1.0.33"'),'utf8')
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
 assert meta['version']=='1.0.32'
 meta['version']='1.0.33';meta['description']=change_one(meta['description'],'1.0.32','1.0.33')
 p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';t=p.read_text('utf8')
 t=change_one(t,'STARSECTOR PL ASCII 1.0.32','STARSECTOR PL ASCII 1.0.33')
 t+='\nWprowadzono polski skrot PF (punkty fabularne) i poprawiono 81 powiazan kontekstowych z angielskim story point.\n'
 p.write_text(t,'utf8')
 print(json.dumps(summary,ensure_ascii=True,indent=2))
 return summary
if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('worktree',type=Path)
 main(pa.parse_args().worktree)
