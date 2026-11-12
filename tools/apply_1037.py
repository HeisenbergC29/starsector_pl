#!/usr/bin/env python3
"""1.0.37: six context-scoped grammatical fixes for getHeOrShe callers.

Only translation CSV literals (not method bytecode), installer edition and metadata.
The shared getHimOrHer/getHisOrHer 'her' JVM constant is not touched.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

FIELDS=['source_class','english_literal','polish_ascii_draft','status']
STATUS='VERIFIED_GENDER_NEUTRAL_1037'
PREFIX='com.fs.starfarer.api.impl.campaign.'
CONTACT=PREFIX+'intel.contacts.ContactIntel'
DELIVERY=PREFIX+'intel.bar.events.DeliveryBarEvent'
SCIENTIST_BAR=PREFIX+'intel.bar.events.ScientistAICoreBarEvent'
SCIENTIST_INTEL=PREFIX+'intel.bar.events.ScientistAICoreIntel'
TRITACH_LOAN=PREFIX+'intel.bar.events.TriTachLoanBarEvent'
TRITACH_MAJOR=PREFIX+'intel.bar.events.TriTachMajorLoanBarEvent'
# Keyed on source class AND exact English CONSTANT_String. Old Polish value is
# asserted before any correction; a stale or shifted translation fails closed.
CORRECT={
 CONTACT:{' will periodically ':(' bedzie okresowo ',' okresowo ')},
 DELIVERY:{' does not appear too displeased. You consider that the initial offer ':
  (' nie wyglada na szczegolnie niezadowolonego. Uwazasz, ze poczatkowa oferta ',
   ' nie okazuje niezadowolenia. Uwazasz, ze poczatkowa oferta ')},
 SCIENTIST_BAR:{' was a bit unhinged, after all - ':
  (' jednak nie mial wszystkich po kolei - ',' jednak nie mysli trzezwo - ')},
 SCIENTIST_INTEL:{' was no-one important.':
  (' nie byl nikim waznym.',' nie jest nikim waznym.')},
 TRITACH_LOAN:{' seems thrown off-balance by your savvy, and never quite recovers that signature megacorp implacability.':
  (' wydaje sie wytracony z rownowagi twoja bystroscia i nie odzyskuje juz typowego dla megakorporacji chlodnego opanowania.',
   ' traci rezon pod wplywem twojej bystrosci i nie odzyskuje typowego dla megakorporacji chlodnego opanowania.')},
}
# Existing historical map key includes additional dialogue and does not exist
# as a CONSTANT_String. This is the actual visible string in the JAR.
NEW={TRITACH_MAJOR:{' says. ':' mowi. '}}
CALLS={
 CONTACT:('createSmallDescription',911),
 DELIVERY:('getNegotiatedText',11),
 SCIENTIST_BAR:('getMainText',18),
 SCIENTIST_INTEL:('createSmallDescription',193),
 TRITACH_LOAN:('getNegotiatedText',43),
 TRITACH_MAJOR:('getMainText2',10),
}

def one(s,old,new):
 if s.count(old)!=1:raise AssertionError(('one occurrence required',old,s.count(old)))
 return s.replace(old,new)

def rows(path):
 with path.open(encoding='utf8',newline='') as f:
  reader=csv.DictReader(f);assert reader.fieldnames==FIELDS
  return list(reader)

def mapping_update(root):
 base=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=base/'TLUMACZENIA_JAR_1036.csv';out=base/'TLUMACZENIA_JAR_1037.csv'
 assert not out.exists(),out
 rr=rows(old);assert len(rr)==5244
 lookup={(r['source_class'],r['english_literal']):r for r in rr}
 assert len(lookup)==len(rr)
 for cl,groups in CORRECT.items():
  for en,(before,after) in groups.items():
   r=lookup[(cl,en)];assert r['polish_ascii_draft']==before and r['status'] in (
    'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME')
   assert after!=before and after.isascii() and en.startswith(' ')==after.startswith(' ') and en.endswith(' ')==after.endswith(' ')
   assert en.count('\n')==after.count('\n')
   r['polish_ascii_draft']=after
 for cl,groups in NEW.items():
  for en,pl in groups.items():
   assert (cl,en) not in lookup and pl.isascii() and en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' ')
   rr.append(dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS))
 assert len(rr)==5245
 with out.open('w',encoding='utf8',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');wr.writeheader();wr.writerows(rr)
 return {'corrected':5,'added':1,'prior_rows':5244,'current_rows':len(rr)}

def apply(root):
 report=mapping_update(root)
 root=root.resolve();api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 p=api/'main.go';s=p.read_text('utf8')
 s=one(s,'const version = "1036"','const version = "1037"')
 s=one(s,'const exeVersion = "1.0.36"','const exeVersion = "1.0.37"')
 s=one(s,'"1032", "1033", version}','"1032", "1033", "1036", version}')
 s=one(s,'PL ASCII patch up to 1.0.36','PL ASCII patch up to 1.0.37')
 p.write_text(s,'utf8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 p.write_text(one(p.read_text('utf8'),'const edition = "1.0.36"','const edition = "1.0.37"'),'utf8')
 p=root/'mod/mod_info.json';m=json.loads(p.read_text('utf8'));assert m['version']=='1.0.36'
 m['version']='1.0.37';m['description']=one(m['description'],'1.0.36','1.0.37')
 p.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n','utf8')
 p=root/'mod/CZYTAJ.txt';s=p.read_text('utf8')
 s=one(s,'STARSECTOR PL ASCII 1.0.36','STARSECTOR PL ASCII 1.0.37')
 s+='\nPoprawiono 6 kontekstow dynamicznego on/ona w raportach, rozmowach i wydarzeniach. Test w grze Windows pozostaje do wykonania.\n'
 p.write_text(s,'utf8')
 return report

if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('worktree',type=Path);args=q.parse_args()
 print(json.dumps(apply(args.worktree),indent=2))
