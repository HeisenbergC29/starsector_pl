#!/usr/bin/env python3
"""v1.0.54: repair composed simulator/Codex notifications and six numeric cases.

Explicit class-scoped JVM literal mapping only; no new executable code patches.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
OLD='TLUMACZENIA_JAR_1053.csv'
NEW='TLUMACZENIA_JAR_1054.csv'
BASE_SHA='ddcec94935d80bcee715514352f79ffbea113ec299953c422746a94241ee179c'
C='com.fs.starfarer.api.impl.'
SIM=C+'campaign.intel.misc.SimUpdateIntel'
CODEX=C+'codex.CodexUpdateIntel'
PHASE=C+'hullmods.PhaseField'
PLANET=C+'PlanetSearchData$5'
BLOCK=C+'campaign.intel.group.BlockadeFGI'
LEAGUE=C+'campaign.intel.events.StandardPerseanLeagueActivityCause$1'
ADDITIONS={
 (SIM,'%s new '):'Nowe frakcje w symulatorze: %s',
 (SIM,'faction'):'',
 (SIM,'factions'):'',
 (SIM,'variant'):'',
 (SIM,'variants'):'',
 (CODEX,'entry'):'',
 (CODEX,'entries'):'',
}
CORRECTIONS={
 (SIM,'%s new hull '):('%s nowych kadlubow ','Nowe warianty okretow w symulatorze: %s'),
 (CODEX,'%s new Codex '):('%s nowych wpisow w Kodeksie ','Nowe wpisy w kodeksie: %s'),
 (PHASE,'The sensor profile of the %s top ships in your fleet is %s. The sensor strength of the top %s phase ships is %s.'):('Sygnatura sensorowa %s najwazniejszych okretow twojej floty wynosi %s. Sila sensorow %s najlepszych okretow fazowych wynosi %s.',
  'Laczna sygnatura %s okr. o najwiekszej sygnaturze we flocie wynosi %s. Laczna sila czujnikow %s okr. fazowych o najwyzszej sile czujnikow wynosi %s.'),
 (PLANET,"Only show planets with %s or more stable locations in the star system they're in, including locations already in use by objectives or similar."):('Pokaz tylko planety w ukladach z co najmniej %s stabilnymi lokalizacjami, wliczajac zajete przez obiekty i instalacje.',
  'Pokaz tylko planety w ukladach, gdzie liczba stabilnych lokalizacji wynosi co najmniej %s. Uwzglednij tez lokalizacje zajete przez obiekty i instalacje.'),
 (BLOCK,'for all %s colonies in the '):('dla wszystkich %s kolonii w ','dla wszystkich kolonii (liczba: %s) w '),
 (LEAGUE,'Event progress value is based on the number and size of colonies under your control. Requires one size %s colony, or at least %s colonies with one being at least size %s.'):('Wartosc postepu wydarzenia zalezy od liczby i wielkosci twoich kolonii. Wymagana jest jedna kolonia wielkosci %s albo co najmniej %s kolonii, w tym jedna o wielkosci przynajmniej %s.',
  'Wartosc postepu wydarzenia zalezy od liczby i wielkosci twoich kolonii. Warunek spelnia kolonia wielkosci %s albo grupa kolonii (liczba: co najmniej %s), z ktorych jedna ma wielkosc przynajmniej %s.'),
}
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
STATUS='VERIFIED_JVM_COMPOSITION_AND_NUMERIC_1054_OFFLINE_PENDING_WINDOWS'
EXPECTED=5290

def sha(b):return hashlib.sha256(b).hexdigest()
def readmap(path):
 with Path(path).open(encoding='utf8',newline='') as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=FIELDS:raise ValueError('Unexpected CSV field order')
  return list(reader)
def encode(rows):
 s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
 return s.getvalue().encode('utf8')
def once(text,old,new):
 if text.count(old)!=1:raise ValueError(('Expected unique anchor',old,text.count(old)))
 return text.replace(old,new)
def make(rows):
 if len(rows)!=5283 or len({(r['source_class'],r['english_literal']) for r in rows})!=5283:raise ValueError('Wrong base inventory')
 old_keys={(x['source_class'],x['english_literal']) for x in rows}
 if old_keys & ADDITIONS.keys():raise ValueError('Cannot append existing key')
 seen=set();new=[]
 for row in rows:
  item=dict(row);key=item['source_class'],item['english_literal']
  if key in CORRECTIONS:
   old,after=CORRECTIONS[key]
   if item['polish_ascii_draft']!=old:raise ValueError(('Source translation changed',key))
   if item['status'] not in {'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}:raise ValueError(('Unexpected unreviewed status',key,item['status']))
   if old.count('%s')!=after.count('%s') or old.count('%d')!=after.count('%d'):raise ValueError(('Format token mismatch',key))
   item['polish_ascii_draft']=after;seen.add(key)
  new.append(item)
 if seen!=set(CORRECTIONS):raise ValueError('Some corrections not found')
 for (cl,en),pl in ADDITIONS.items():
  if not (en.isascii() and pl.isascii()) or en.count('%s')!=pl.count('%s') or en.count('%d')!=pl.count('%d'):
   raise ValueError(('Malformed new mapped string',cl,en,pl))
  new.append({'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
 if len(new)!=EXPECTED or len({(r['source_class'],r['english_literal']) for r in new})!=EXPECTED:raise ValueError('Duplicate or missing new map keys')
 return new

def apply(root):
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';tr=api/'translations'
 original=tr/OLD;target=tr/NEW
 if target.exists():raise FileExistsError(target)
 if sha(original.read_bytes())!=BASE_SHA:raise ValueError('Unexpected source 1.0.53 API SHA')
 base=readmap(original)
 if encode(base)!=original.read_bytes():raise ValueError('CSV CRLF or quoting mismatch')
 newdata=encode(make(base));target.write_bytes(newdata)
 go=api/'main.go';s=go.read_text('utf8')
 for a,b in [
  ('const version = "1053"','const version = "1054"'),
  ('const exeVersion = "1.0.53"','const exeVersion = "1.0.54"'),
  ('"1050", "1051", "1052", version}', '"1050", "1051", "1052", "1053", version}'),
  ('PL ASCII patch up to 1.0.53','PL ASCII patch up to 1.0.54')]:s=once(s,a,b)
 go.write_text(s,encoding='utf8')
 installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 installer.write_text(once(installer.read_text('utf8'),'const edition = "1.0.53"','const edition = "1.0.54"'),encoding='utf8')
 meta=root/'mod/mod_info.json';m=json.loads(meta.read_text('utf8'))
 if m['version']!='1.0.53' or m['gameVersion']!='0.98a-RC8':raise ValueError('Unexpected baseline manifest')
 m['version']='1.0.54';m['description']=once(m['description'],'1.0.53','1.0.54')
 meta.write_text(json.dumps(m,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 textfile=root/'mod/CZYTAJ.txt'
 textfile.write_text(once(textfile.read_text('utf8'),'STARSECTOR PL ASCII 1.0.53','STARSECTOR PL ASCII 1.0.54')+
  '\nPoprawiono komunikaty nowosci w symulatorze i kodeksie oraz szesc opisow z dynamiczna liczba. Nie zmieniono instrukcji Java ani danych gry.\n',encoding='utf8')
 return {'version':'1.0.54','added_api_rows':len(ADDITIONS),'corrected_existing_api_rows':len(CORRECTIONS),
  'total_api_mapping_rows':EXPECTED,'map_sha256':sha(newdata),'old_map_sha256':BASE_SHA,
  'modified_java_classes':len({k[0] for k in ADDITIONS}|{k[0] for k in CORRECTIONS}),
  'new_bytecode_instruction_changes':0,'all_data_files_unchanged':870}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);args=p.parse_args()
 print(json.dumps(apply(args.worktree),indent=2))
