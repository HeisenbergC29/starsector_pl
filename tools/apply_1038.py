#!/usr/bin/env python3
"""Starsector PL 1.0.38: grammatically complete HistorianData/HistorianBarEvent.

Only class-scoped Java CONSTANT_String translations, metadata and patcher edition.
In HistorianData `her` is shared across getHimOrHer/getHisOrHer, but Polish
`jej` is valid in BOTH independently verified assembled contexts. This does
not imply that any other class's shared `her` may be replaced.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

FIELDS=['source_class','english_literal','polish_ascii_draft','status']
BASE='com.fs.starfarer.api.impl.campaign.intel.bar.events.historian.'
DATA=BASE+'HistorianData'
BAR=BASE+'HistorianBarEvent'
DONATION=BASE+'DonationOffer'
STATUS='VERIFIED_HISTORIAN_COMPOSED_1038'
NEW={
 DATA:{'man':'mezczyzna','woman':'kobieta','him':'mu','her':'jej','his':'jego'},
 BAR:{'An old ':'Przy stoliku siedzi ',' wants':' ma do zaoferowania',' for ':' za '},
 DONATION:{' pursue':' zbadac'},
}
CORRECT={
 BAR:{
  'Go over to the ':('Podejdz do ','Porozmawiaj z '),
  ' with the paper book and see what ':(' z papierowa ksiazka i zobaczyc, co ', ' z papierowa ksiazka, zeby dowiedziec sie, co '),
  ' sits alone at a table, ':(' siedzi samotnie przy stoliku, ',' w podeszlym wieku i samotnie czyta '),
  'leafing through what looks like a genuine hardcopy paper book. As you walk by, ':('przerzucajac kartki czegos, co wyglada na prawdziwa papierowa ksiazke. Gdy przechodzisz obok, ','papierowa ksiazke. Gdy przechodzisz obok, '),
  ' looks up and offers the seat across from ':(' podnosi wzrok i wskazuje miejsce naprzeciwko ',' podnosi wzrok i wskazuje wolne miejsce, a ty dziekujesz '),
  'A weary expression passes over the ':('Zmeczenie przebiega przez twarz ','Przez chwile '),
  "'s face for just a moment before ":('na moment przez twarz, zanim ',' wyglada na osobe zmeczona, ale zaraz '),
  ' resumes an energetic demeanor.':(' odzyskuje zywy, energiczny wyraz twarzy.',' znow nabiera wigoru.'),
  'know for sure where I\'ll end up in a couple of months."':('nie wiem, gdzie bede za kilka miesiecy."','wiem na pewno, gdzie bede za kilka miesiecy."'),
  ' face at this.':(' twarzy na te slowa.',' twarzy, gdy to slyszy.'),
  ' leans in as if conspiring, "':(' nachyla sie konspiracyjnie: "',' nachyla sie konspiracyjnie: '),
 },
 DONATION:{
  '... some promising leads that a ':('... pewne obiecujace tropy, do ktorych dotarcie umozliwilaby darowizna ','... obiecujace tropy, ktore darowizna w wysokosci '),
 },
}

def once(source,old,new):
 if source.count(old)!=1:raise AssertionError(('exact one replacement',repr(old),source.count(old)))
 return source.replace(old,new)

def rows(p):
 with p.open('r',encoding='utf8',newline='') as f:
  r=csv.DictReader(f)
  assert r.fieldnames==FIELDS
  return list(r)

def apply(root):
 root=root.resolve();trans=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=trans/'TLUMACZENIA_JAR_1037.csv';out=trans/'TLUMACZENIA_JAR_1038.csv'
 assert not out.exists()
 rr=rows(old);assert len(rr)==5245
 seen={(r['source_class'],r['english_literal']):r for r in rr}
 assert len(seen)==len(rr)
 for cl,mapping in CORRECT.items():
  for en,(before,after) in mapping.items():
   x=seen[(cl,en)];assert x['polish_ascii_draft']==before
   assert x['status'] in ('DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME','potwierdzone_CONST_String_0989'),(cl,en,x['status'])
   assert after.isascii() and (en.startswith(' ')==after.startswith(' ') or en=="'s face for just a moment before ") and (en.endswith(' ')==after.endswith(' ') or en==' leans in as if conspiring, "')
   assert en.count('\n')==after.count('\n')
   x['polish_ascii_draft']=after
 for cl,mapping in NEW.items():
  for en,pl in mapping.items():
   assert (cl,en) not in seen and en!=pl and pl.isascii()
   assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' ')
   rr.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 assert len(rr)==5254
 with out.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rr)
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 p=api/'main.go';s=p.read_text('utf8')
 s=once(s,'const version = "1037"','const version = "1038"')
 s=once(s,'const exeVersion = "1.0.37"','const exeVersion = "1.0.38"')
 s=once(s,'"1033", "1036", version}','"1033", "1036", "1037", version}')
 s=once(s,'PL ASCII patch up to 1.0.37','PL ASCII patch up to 1.0.38')
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';p.write_text(once(p.read_text('utf8'),'const edition = "1.0.37"','const edition = "1.0.38"'),'utf8')
 p=root/'mod/mod_info.json';d=json.loads(p.read_text('utf8'));assert d['version']=='1.0.37'
 d['version']='1.0.38';d['description']=once(d['description'],'1.0.37','1.0.38')
 p.write_text(json.dumps(d,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
 s=once(s,'STARSECTOR PL ASCII 1.0.37','STARSECTOR PL ASCII 1.0.38')
 s+='\nPoprawiono kompletne polskie teksty spotkania z historykiem, w tym odmiane i rodzaj zaimkow. Natywny test Windows nadal wymagany.\n'
 p.write_text(s,'utf8')
 return {'version':'1.0.38','new_api':9,'corrected_api':12,'api_rows':len(rr)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 a=p.parse_args();print(json.dumps(apply(a.worktree),indent=2))
