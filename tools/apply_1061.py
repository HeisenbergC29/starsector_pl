#!/usr/bin/env python3
"""1.0.61: gate hauler intel time grammar; complete class-scoped historical review.

Only replace original, SHA-pinned Java CONSTANT_String literals in exactly one
named class. Review 25 previously DRAFT/OPTIONAL rows without double counting
older approved API reviews; preserve every game data file and JVM instructions.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once

CLASS='com.fs.starfarer.api.impl.campaign.intel.misc.GateHaulerIntel'
OLD='TLUMACZENIA_JAR_1060.csv'
NEW='TLUMACZENIA_JAR_1061.csv'
BASE_SHA='963634daecdbd86e007091f90788367d826ade750d4b16bf335dd88ce439b724'
DRAFT={'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
STATUS='REVIEWED_ORIGINAL_JVM_GATE_HAULER_1061_PENDING_WINDOWS'
NEW_LITERALS={'day':'dzien','days':'dni',' ':'. '}
REPAIRS={
 'Estimated %s ':'Szacowany czas przelotu: %s ',
 ' to complete transit':'',
 ' for transit':'',
 'Arrived at ':'Dotarl do celu: ',
 'Arriving at ':'Zbliza sie do celu: ',
 'The gate hauler has arrived to the ':'Holownik Bram dotarl do celu: ',
 'and is decelerating in order to attain a parking orbit.':'Wyhamowuje, aby wejsc na orbite postojowa.',
 'transiting deep space':'w przelocie przez gleboka przestrzen',
 "Once it's in open space, it's estimated that it will take %s ":'Po wyjsciu na otwarta przestrzen szacowany czas lotu: %s ',
 "The gate hauler is in transit, in deep space. It's estimated that it will take %s ":'Holownik Bram przemierza gleboka przestrzen. Szacowany czas do celu: %s ',
 ' until it arrives ':'. Cel: ',
 'to its destination, the ':'',
 'Status: dormant':'Stan: uspiony',
 'Status: activating':'Stan: uruchamianie',
 'Status: operational':'Stan: gotowy',
}
RELEASE_SUFFIX=('\nW panelu Holownika Bram poprawiono polskie jednostki czasu (dzien/dni), '
                'skladanie opisow trasy i celu oraz rodzaj gramatyczny statusu. '
                '25 historycznych tekstow zostalo zweryfikowanych w oryginalnym JVM. '
                'Nie zmieniono skryptow, identyfikatorow ani logiki gry.\n')

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()
def fp(row:dict)->str:return sha('\0'.join(row[x] for x in ('source_class','english_literal','polish_ascii_draft')).encode('utf8'))

def build(rows:list[dict])->tuple[list[dict],dict]:
 if len(rows)!=5309 or len({(r['source_class'],r['english_literal']) for r in rows})!=5309:
  raise ValueError('Not 1.0.60 API mapping')
 subset={r['english_literal']:r for r in rows if r['source_class']==CLASS}
 if len(subset)!=30 or set(NEW_LITERALS)&set(subset) or not set(REPAIRS)<=set(subset):
  raise ValueError('Original class mapping or new literal collisions')
 olddraft=[x for x in subset.values() if x['status'] in DRAFT]
 if len(olddraft)!=25:raise ValueError(('Historical review scope incorrect',len(olddraft)))
 changed=set();reviewed=[];out=[]
 for old in rows:
  row=dict(old)
  if row['source_class']==CLASS:
   english=row['english_literal']; prior=row['polish_ascii_draft']
   if row['status'] in DRAFT:
    reviewed.append({'source_class':CLASS,'english_literal':english,
      'old_polish_ascii':prior,'old_status':row['status'],
      'new_polish_ascii':REPAIRS.get(english,prior),
      'english_key_sha256':sha(english.encode('utf8')),
      'old_row_sha256':fp(old)})
   if english in REPAIRS:
    candidate=REPAIRS[english]
    if candidate==prior or any(prior.count(m)!=candidate.count(m) for m in ('%s','%d','%f','\r','\n','\t')):
     raise ValueError(('Invalid translation delta',english))
    row['polish_ascii_draft']=candidate;changed.add(english)
   if row['status'] in DRAFT or english in REPAIRS:
    row['status']=STATUS
   if not row['polish_ascii_draft'].isascii():raise ValueError('Non-ASCII Polish output')
  out.append(row)
 if len(reviewed)!=25 or changed!=set(REPAIRS):raise ValueError('Historical review or corrections incomplete')
 for en,pl in NEW_LITERALS.items():
  if not en.isascii() or not pl.isascii():raise ValueError('Unapproved charset')
  out.append({'source_class':CLASS,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
 if len(out)!=5312 or len({(r['source_class'],r['english_literal']) for r in out})!=5312:
  raise ValueError('1.0.61 mapping cardinality mismatch')
 for r in reviewed:r['new_row_sha256']=fp(next(x for x in out if x['source_class']==CLASS and x['english_literal']==r['english_literal']))
 return out,{'reviewed':reviewed,'changed_translations':len(changed),'new_translations':len(NEW_LITERALS)}

def apply(root:Path)->dict:
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';tr=api/'translations'
 a=tr/OLD;b=tr/NEW
 if b.exists() or sha(a.read_bytes())!=BASE_SHA:raise ValueError('Not verified 1.0.60 baseline or already applied')
 source=readmap(a)
 if encode(source)!=a.read_bytes():raise ValueError('CSV input changed or serialized differently')
 mapped,stats=build(source);encoded=encode(mapped)
 main=api/'main.go';txt=main.read_text('utf8')
 for x,y in [('const version = "1060"','const version = "1061"'),
 ('const exeVersion = "1.0.60"','const exeVersion = "1.0.61"'),
 ('"1059", version}','"1059", "1060", version}'),
 ('PL ASCII patch up to 1.0.60','PL ASCII patch up to 1.0.61')]:txt=once(txt,x,y)
 installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 ins=once(installer.read_text('utf8'),'const edition = "1.0.60"','const edition = "1.0.61"')
 info=root/'mod/mod_info.json';m=json.loads(info.read_text('utf8'))
 if (m['version'],m['gameVersion'])!=('1.0.60','0.98a-RC8'):raise ValueError('Wrong game metadata')
 m['version']='1.0.61';m['description']=once(m['description'],'1.0.60','1.0.61')
 readme=root/'mod/CZYTAJ.txt'
 guide=once(readme.read_text('utf8'),'STARSECTOR PL ASCII 1.0.60','STARSECTOR PL ASCII 1.0.61')+RELEASE_SUFFIX
 b.write_bytes(encoded);main.write_text(txt,'utf8');installer.write_text(ins,'utf8')
 info.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n','utf8');readme.write_text(guide,'utf8')
 return {'release':'1.0.61','historical_api_rows_reviewed':25,
  'changed_existing_translations':len(REPAIRS),'new_class_scoped_translations':len(NEW_LITERALS),
  'api_map_rows':len(mapped),'new_map_sha256':sha(encoded),'mod_data_changed':0,
  'new_JVM_instruction_changes':0,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(apply(a.worktree),indent=2))
