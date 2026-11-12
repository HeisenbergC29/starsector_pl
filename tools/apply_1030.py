#!/usr/bin/env python3
"""Reproduce Starsector PL 1.0.30 (precise UI and a whole assembled bounty sentence).

MUST run after apply_1029. Never changes technical IDs or executable JVM methods.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

STATUS='VERIFIED_VISIBLE_SENTENCE_1030'
PREV_OBF_SHA='fe13bdd519414be15e290ab1fcf84724524ea5e2f133b1bae6ce4e12ad90e71a'
# Insert only after independent private original-JAR OBF patch + SHA verification.
NEW_OBF_SHA='291a0098153b058b5725a97a331d4e41763bef9ea33dbac42eea0d0a989f8722'
OBF={
 'com.fs.starfarer.coreui.O':{'Name:':'Nazwa:'},
 'com.fs.starfarer.ui.impl.StandardTooltipV2$15':{'Price: ':'Cena: '},
}
API={
 'com.fs.starfarer.api.impl.campaign.intel.PersonBountyIntel':{'He is':'On','She is':'Ona'},
 'com.fs.starfarer.api.impl.campaign.abilities.InterdictionPulseAbility':{'Interdict! (':'Zaklocenie! (','s)':' s)'},
}
CORRECTION={
 'source_class':'com.fs.starfarer.api.impl.campaign.intel.PersonBountyIntel',
 'english_literal':' rumored to be ',
 'from_polish':' wedlug poglosek przebywa ',
 'to_polish':' podobno ',
}
FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def replace_once(s,a,b):
 assert s.count(a)==1,(repr(a),s.count(a))
 return s.replace(a,b)

def rows(p):
 with p.open('r',encoding='utf8',newline='') as f:
  r=csv.DictReader(f);assert r.fieldnames==FIELDS
  return list(r)

def write_map(path, old, additions, edit=None):
 original=rows(old)
 known={(r['source_class'],r['english_literal']) for r in original}
 if edit:
  affected=[r for r in original if (r['source_class'],r['english_literal'])==(edit['source_class'],edit['english_literal'])]
  assert len(affected)==1 and affected[0]['polish_ascii_draft']==edit['from_polish']
  affected[0]['polish_ascii_draft']=edit['to_polish'];affected[0]['status']=STATUS
 extra=[]
 for cl,pairs in additions.items():
  for en,pl in pairs.items():
   assert en!=pl and en.isascii() and pl.isascii()
   assert (cl,en) not in known
   assert (en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' ')) or (en=='s)' and pl==' s)')
   assert en.count('\n')==pl.count('\n')
   extra.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 assert not path.exists(),path
 with path.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(original+extra)
 return len(original),len(extra)

def main(root):
 o=root/'buildtools/NARZEDZIA_OBF'
 a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old_o,n_o=write_map(o/'TLUMACZENIA_OBF_10130.csv',o/'TLUMACZENIA_OBF_10129.csv',OBF)
 old_a,n_a=write_map(a/'translations/TLUMACZENIA_JAR_1030.csv',a/'translations/TLUMACZENIA_JAR_1029.csv',API,CORRECTION)
 assert (old_o,n_o,old_a,n_a)==(3508,2,5215,4)
 p=o/'main.go';s=p.read_text('utf8')
 s=replace_once(s,'TLUMACZENIA_OBF_10128.csv TLUMACZENIA_OBF_10129.csv','TLUMACZENIA_OBF_10128.csv TLUMACZENIA_OBF_10129.csv TLUMACZENIA_OBF_10130.csv')
 s=replace_once(s,'const currentPatchState = "patched 10129"','const currentPatchState = "patched 10130"')
 s=replace_once(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"'+PREV_OBF_SHA+'": "10129",')
 s=replace_once(s,'loadTranslations("TLUMACZENIA_OBF_10129.csv")','loadTranslations("TLUMACZENIA_OBF_10130.csv")')
 s=replace_once(s,'state == currentPatchState || state == "patched 10128"','state == currentPatchState || state == "patched 10129" || state == "patched 10128"')
 s=replace_once(s,'OBF 1.0.29 | stan:','OBF 1.0.30 | stan:')
 s=replace_once(s,'1.0.29: Lokalizacja tekstow OBF','1.0.30: Lokalizacja tekstow OBF')
 s=replace_once(s,'0.9.99-1.0.29; odmowa modyfikacji','0.9.99-1.0.30; odmowa modyfikacji')
 p.write_text(s,'utf8')
 p=o/'main_test.go';p.write_text(replace_once(p.read_text('utf8'),'alreadyThisRelease("patched 10129")','alreadyThisRelease("patched 10130")'),'utf8')
 p=a/'main.go';s=p.read_text('utf8')
 s=replace_once(s,'const version = "1029"','const version = "1030"')
 s=replace_once(s,'const exeVersion = "1.0.29"','const exeVersion = "1.0.30"')
 s=replace_once(s,'"1027", "1028", version}','"1027", "1028", "1029", version}')
 s=replace_once(s,'PL ASCII patch up to 1.0.29','PL ASCII patch up to 1.0.30')
 s=replace_once(s,'const expectedOBFPatched10129 = "'+PREV_OBF_SHA+'"','const expectedOBFPatched10129 = "'+PREV_OBF_SHA+'"\nconst expectedOBFPatched10130 = "'+NEW_OBF_SHA+'"')
 s=replace_once(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10129','hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10130 && hash(obf) != expectedOBFPatched10129')
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 p.write_text(replace_once(p.read_text('utf8'),'const edition = "1.0.29"','const edition = "1.0.30"'),'utf8')
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
 assert meta['version']=='1.0.29'
 meta['version']='1.0.30';meta['description']=replace_once(meta['description'],'1.0.29','1.0.30')
 p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8');s=replace_once(s,'STARSECTOR PL ASCII 1.0.29','STARSECTOR PL ASCII 1.0.30')
 s+='\nPoprawiono caly skladany opis polozenia poszukiwanej osoby oraz kolejne etykiety UI. Wersja 1.1 pozostaje nieukonczona.\n'
 p.write_text(s,'utf8')
 print('1.0.30, maps OBF',old_o,'+',n_o,'API',old_a,'+',n_a,'(1 semantic correction)')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path); main(p.parse_args().worktree)
