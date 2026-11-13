#!/usr/bin/env python3
"""Starsector PL 1.0.52: audited gendered bar-dialogue pronouns and composition.

All changes remain class-specific JVM CONSTANT_String translations; this version
introduces NO further executable bytecode edits beyond the previously authorized
1.0.51 personality tooltip exception.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path

OLD='TLUMACZENIA_JAR_1051.csv'
NEW='TLUMACZENIA_JAR_1052.csv'
OLD_SHA='099abe6d62264e6b1d4ff66b9aba196ecb7d11845b7d2b2207aab4a8b8f66aa4'
ROOT='com.fs.starfarer.api.impl.campaign.intel.bar.events.'
BASE=ROOT+'BaseBarEventWithPerson'
LUDDIC=ROOT+'LuddicPathBaseBarEvent'
SHIELD=ROOT+'PlanetaryShieldBarEvent'
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
STATUS='REVIEWED_BAR_DIALOGUE_CONTEXT_1052_OFFLINE_PENDING_WINDOWS'
ADDITIONS={
 (BASE,'man'):'mezczyzna',
 (BASE,'woman'):'kobieta',
 (BASE,'him'):'mu',
 (BASE,'his'):'jego',
 (BASE,'her'):'jej',
 (LUDDIC,'A '):'Widzisz, jak ',
 (LUDDIC,' eyes.'):' oczach.',
 (LUDDIC,' terms'):' warunki',
 (LUDDIC,' handle '):' sprobuje rozwiazac sytuacje, bo to ',
 (SHIELD,' a drink'):' drinka',
 (SHIELD,' temple. '):' skron. ',
 (SHIELD,' rest'):' odpoczynku',
 (SHIELD,' shakes '):' kreci glowa. Z ',
 (SHIELD,' head, \"Captain, '):' ust pada: \"Kapitanie, ',
}
CORRECTIONS={
 (LUDDIC,'You agree to the '):('Przystajesz na ','Akceptujesz warunki, ktore stawia '),
 (LUDDIC,"'s terms and make the necessary arrangements."):(
  'na jego warunki i dokonaj niezbednych ustalen.',', i dokonujesz niezbednych ustalen.'),
 (LUDDIC,'Offer for '):('Oferta dla ','Zamiast tego zaproponuj '),
 (LUDDIC,' to join your fleet instead'):(' zamiast tego dolaczyc do twojej floty',' dolaczenie do swojej floty'),
 (LUDDIC,'Suggest that '):('Zaproponuj, zeby ','Zaproponuj: niech '),
 (LUDDIC,' own problems'):(' wlasne problemy',' prywatne sprawy.'),
 (SHIELD,'Offer to apologize for the misunderstanding by buying '):(
  'Zaproponuj drinka na przeprosiny za nieporozumienie dla ',
  'Przepros za nieporozumienie, stawiajac '),
 (SHIELD,'Leave the old spacer to '):('Pozostaw starego kosmonaute, zeby ','Nie zaklocaj '),
 (SHIELD,'attacked with no mercy. "It weren\'t pirates, nor military," here the spacer loses '):(
  'atakowaly bez litosci. "To nie byli piraci ani wojsko" - tu kosmonauta traci ',
  'atakowaly bez litosci. "To nie byli piraci ani wojsko" - w '),
 (SHIELD,' cheer at a good story. "Ludd\'s hells, I swear to you it weren\'t anything human."'):(
  ' wiwatuje na czesc dobrej opowiesci. "Na piekla Ludda, przysiegam, to nie bylo nic ludzkiego."',
  ' glosie gasnie entuzjazm opowiesci. "Na piekla Ludda, przysiegam, to nie bylo nic ludzkiego."'),
}
EXPECTED_ORIGINAL_CLASS_SHA={
 BASE:'ad08d72a03f14bf6cd3dad21aa2026cab50347f403d45a900ce4bf6ff3303575',
 LUDDIC:'a30c6c7bc43db993441923cacc8d14c5744e7623b1a8cb7dc6bf8acb20f2a289',
 SHIELD:'2dd2afef38297bde6edaf8b790031a321d69b1aaf4fd5d4bc89ca75ecd7885e4',
}

def sha(data):return hashlib.sha256(data).hexdigest()
def once(s,a,b):
 if s.count(a)!=1:raise ValueError(('expected one occurrence',a,s.count(a)))
 return s.replace(a,b)
def readmap(path):
 with Path(path).open(encoding='utf-8',newline='') as f:
  rdr=csv.DictReader(f)
  if rdr.fieldnames!=FIELDS:raise ValueError('Unexpected CSV columns')
  return list(rdr)
def serialize(rows):
 f=io.StringIO(newline='');writer=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');writer.writeheader();writer.writerows(rows)
 return f.getvalue().encode('utf-8')

def make(rows):
 if len(rows)!=5269 or len({(r['source_class'],r['english_literal']) for r in rows})!=5269:raise ValueError('Wrong base map size/keys')
 previous={(r['source_class'],r['english_literal']):r for r in rows}
 if ADDITIONS.keys() & previous.keys():raise ValueError('Cannot add duplicate mapping')
 out=[];edits=[]
 for row in rows:
  r=row.copy();key=(row['source_class'],row['english_literal'])
  if key in CORRECTIONS:
   old,new=CORRECTIONS[key]
   if old!=r['polish_ascii_draft'] or r['status'] not in {'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED'}:
    raise ValueError(('Changed source translation/status',key,r['polish_ascii_draft'],r['status']))
   if old.count('%s')!=new.count('%s') or old.count('%d')!=new.count('%d'):
    raise ValueError(('Lost placeholder',key))
   r['polish_ascii_draft']=new;edits.append(key)
  out.append(r)
 if set(edits)!=set(CORRECTIONS):raise ValueError('Some verified corrections not found')
 for key,value in ADDITIONS.items():
  if not value.isascii() or not key[1].isascii():raise ValueError(('Non-ASCII new text',key))
  out.append(dict(zip(FIELDS,[key[0],key[1],value,STATUS])))
 if len(out)!=5283 or len({(r['source_class'],r['english_literal']) for r in out})!=len(out):raise ValueError('Broken 5283 map')
 return out

def apply(root):
 root=Path(root);folder=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations';src=folder/OLD;dst=folder/NEW
 if dst.exists():raise FileExistsError('1.0.52 overlay already installed')
 if sha(src.read_bytes())!=OLD_SHA:raise ValueError('Expected 1.0.51 map SHA')
 base=readmap(src)
 if serialize(base)!=src.read_bytes():raise ValueError('Input map not byte-exact roundtrippable')
 dst.write_bytes(serialize(make(base)))
 main=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go'
 code=main.read_text(encoding='utf8')
 code=once(code,'const version = "1051"','const version = "1052"')
 code=once(code,'const exeVersion = "1.0.51"','const exeVersion = "1.0.52"')
 code=once(code,'"1048", "1049", "1050", version}', '"1048", "1049", "1050", "1051", version}')
 code=once(code,'PL ASCII patch up to 1.0.51','PL ASCII patch up to 1.0.52')
 main.write_text(code,encoding='utf8')
 ins=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 ins.write_text(once(ins.read_text('utf8'),'const edition = "1.0.51"','const edition = "1.0.52"'),encoding='utf8')
 info=root/'mod/mod_info.json';obj=json.loads(info.read_text('utf8'))
 if obj['version']!='1.0.51' or obj['gameVersion']!='0.98a-RC8':raise ValueError('Wrong source mod version')
 obj['version']='1.0.52';obj['description']=once(obj['description'],'1.0.51','1.0.52')
 info.write_text(json.dumps(obj,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
 readme=root/'mod/CZYTAJ.txt'
 readme.write_text(once(readme.read_text('utf8'),'STARSECTOR PL ASCII 1.0.51','STARSECTOR PL ASCII 1.0.52')+
  '\nPoprawiono polskie zaimki i skladane dialogi w barach Sciezki Ludda oraz PlanetaryShieldBarEvent. Wspolne her oznacza jej w sprawdzonych kontekstach; instrukcje Java bez nowych zmian.\n',encoding='utf8')
 return {'version':'1.0.52','additions':len(ADDITIONS),'corrections':len(CORRECTIONS),'changed_classes':3,
    'map_rows':len(make(base)),'map_sha256':sha(dst.read_bytes()),'source_sha256':OLD_SHA,'new_executable_code_changes':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(apply(p.parse_args().worktree),indent=2))
