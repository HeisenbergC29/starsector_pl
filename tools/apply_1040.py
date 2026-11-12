#!/usr/bin/env python3
"""1.0.40: localize 12 BaseGetCommodityBarEvent getManOrWoman() contexts.

Only class-scoped CONSTANT_String entries, version metadata, and installer version.
Does NOT change shared `her` or any executable JVM method bytecode.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

FIELDS=['source_class','english_literal','polish_ascii_draft','status']
B='com.fs.starfarer.api.impl.campaign.intel.bar.events.'
STATUS='VERIFIED_GENDERED_BAR_EVENT_1040'
NEW={
 B+'BaseGetCommodityBarEvent': {'man':'mezczyzna','woman':'kobieta'},
 B+'CorruptPLClerkSuppliesBarEvent': {'A ':'Przy barze stoi '},
}
CORRECT={
 B+'DeliveryBarEvent': {
  'At a corner table, a concerned-looking ':('Przy stoliku w rogu siedzi zatroskany ','Przy stoliku w rogu siedzi '),
  'Nod to the concerned ':('Podejdz do zatroskanego ','Porozmawiaj z '),
  ' glumly examines ':(' z ponura mina przyglada sie ',' i z ponura mina przyglada sie '),
 },
 B+'LuddicCraftBarEvent':{
  'A tough looking ':('Twardo wygladajacy ','Przy stoliku siedzi '),
  ' whose worn but well-tailored work suit bears the ':(' ktorego znoszony, lecz starannie skrojony stroj roboczy nosi ',' w znoszonym, lecz starannie skrojonym stroju roboczym z '),
  'sigil of a crafts guild sits at a corner table bearing the remnants of a spare meal.':('z godlem cechu rzemieslnikow siedzi przy stole w kacie, na ktorym zostaly resztki skromnego posilku.','godlem cechu rzemieslnikow. Na stole zostaly resztki skromnego posilku.'),
  'Strike up a conversation with the tough-looking ':('Zagadaj do groznie wygladajacego ','Porozmawiaj z '),
 },
 B+'LuddicFarmerBarEvent':{
  'A weathered-looking ':('Sterany zyciem ','Przy stole siedzi '),
  ' whose worn but well-tailored ':(' ktorego znoszony, lecz dobrze skrojony ',' w znoszonym, lecz dobrze skrojonym '),
  'work suit bears the sigil of a farming commune sits at a table drinking small-beer.':('w kombinezonie roboczym z godlem wspolnoty rolniczej siedzi przy stole i popija lekkie piwo.','stroju roboczym z godlem wspolnoty rolniczej i popija lekkie piwo.'),
  'Chat up the weathered-looking ':('Zagadaj do steranego zyciem ','Porozmawiaj z '),
 },
 B+'ScientistAICoreBarEvent':{
  'A disheveled ':('Rozczochrany ','W poblizu stoi '),
  ' in academic uniform is bothering some of the ':(' w akademickim mundurze zaczepia kilku ',' w akademickim mundurze i zaczepia kilku '),
 },
 B+'TriTachLoanBarEvent':{
  'Introduce yourself to the Tri-Tachyon ':('Przedstaw sie przedstawicielowi Tri-Tachyon ','Porozmawiaj z '),
  ' and try to land some investment credits':(' i sprobowac zdobyc kredyty na inwestycje',' i sprobuj uzyskac kredyty na inwestycje'),
  'The Tri-Tachyon ':('Przedstawiciel Tri-Tachyon ','W odpowiedzi '),
  "'s smile freezes in place as you launch into a sophisticated ":('usmiech zamiera na twarzy, gdy zaczynasz szczegolowy ',' milknie na chwile, gdy przedstawiasz rzeczowa '),
 },
 B+'TriTachMajorLoanBarEvent':{
  'As the negotiations conclude, the Tri-Tachyon ':('Kiedy negocjacje dobiegaja konca, przedstawiciel Tri-Tachyon ','Gdy negocjacje dobiegaja konca, '),
 },
}

def once(s,old,new):
 if s.count(old)!=1:raise ValueError(('not exactly once',old,s.count(old)))
 return s.replace(old,new)

def read(path):
 with path.open(encoding='utf8',newline='') as f:
  r=csv.DictReader(f)
  if r.fieldnames!=FIELDS:raise ValueError('Wrong CSV headings')
  return list(r)

def apply(root):
 root=root.resolve();dst=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';td=dst/'translations';src=td/'TLUMACZENIA_JAR_1038.csv';out=td/'TLUMACZENIA_JAR_1040.csv'
 if out.exists():raise ValueError('Do not overwrite release map')
 rows=read(src)
 if len(rows)!=5254:raise ValueError(('wrong source count',len(rows)))
 mapping={(r['source_class'],r['english_literal']):r for r in rows}
 if len(mapping)!=len(rows):raise ValueError('duplicate keys')
 nc=0
 for cl,entries in CORRECT.items():
  for en,(old,new) in entries.items():
   row=mapping[(cl,en)]
   if row['polish_ascii_draft']!=old:raise ValueError(('incorrect source',cl,en,row))
   if not new.isascii() or en.count('\n')!=new.count('\n'):raise ValueError(('unsafe replacement',cl,en))
   row['polish_ascii_draft']=new
   nc+=1
 nn=0
 for cl,entries in NEW.items():
  for en,pl in entries.items():
   if (cl,en) in mapping or en==pl or not pl.isascii():raise ValueError(('invalid new key',cl,en))
   rows.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS));nn+=1
 if (nn,nc)!=(3,18):raise ValueError(('unexpected count',nn,nc))
 with out.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
 # Keep only previous approved versions in the patcher. Versions 1.0.39 and 1.0.38 have identical Java libraries.
 p=dst/'main.go';v=p.read_text('utf8')
 v=once(v,'const version = "1038"','const version = "1040"')
 v=once(v,'const exeVersion = "1.0.38"','const exeVersion = "1.0.40"')
 v=once(v,'"1036", "1037", version}','"1036", "1037", "1038", version}')
 v=once(v,'PL ASCII patch up to 1.0.38','PL ASCII patch up to 1.0.40')
 p.write_text(v,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';p.write_text(once(p.read_text('utf8'),'const edition = "1.0.39"','const edition = "1.0.40"'),'utf8')
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
 if meta['version']!='1.0.39':raise ValueError('Wrong data baseline')
 meta['version']='1.0.40';meta['description']=once(meta['description'],'1.0.39','1.0.40')
 p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';v=p.read_text('utf8')
 v=once(v,'STARSECTOR PL ASCII 1.0.39','STARSECTOR PL ASCII 1.0.40')
 v+='\nPrzetlumaczono man/woman w osobnej rodzinie wydarzen barowych, dostosowujac zdania do obu plci. Wciaz wymagane sa testy Windows oraz naprawa pozostalych zaimkow.\n'
 p.write_text(v,'utf8')
 return {'version':'1.0.40','new_api':nn,'corrected_api':nc,'map_rows':len(rows)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(apply(a.worktree),indent=2))
