#!/usr/bin/env python3
"""Starsector PL 1.0.34: reviewed gender-neutral rules.csv text, no Java changes.

Applies only to displayed text (plus one displayed option label), never to
triggers, conditions, scripts, technical IDs or other game fields.

Run after apply_1033.py. The commercial original resources stay private.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path

# All translations ASCII. The identity of each row and the input phrase are
# checked independently to avoid broad replacement of dynamic variables.
PATCHES = {
 'gaTJMissionText3a': [
  ('Badacz chce wrocic do domu, $gaTJ_heOrShe zdolal nawiazac kontakt, a my przygotowalismy caly system',
   'Badacz chce wrocic do domu; kontakt zostal nawiazany, a my przygotowalismy caly system'),
 ],
 'gaTJMissionText3b': [
  ('Badacz chce wrocic do domu, $gaTJ_heOrShe zdolal wyslac kilka wiadomosci, a my przygotowalismy caly system',
   'Badacz chce wrocic do domu; otrzymalismy kilka wiadomosci i przygotowalismy caly system'),
 ],
 'gaTJPlanetContact': [
  ('wykrzykuje $gaTJ_heOrShe.', 'wykrzykuje naukowiec.'),
  ('Jestem akademik $gaTJ_researcherName i jestem gotow odleciec.',
   'Nazywam sie $gaTJ_researcherName, pracuje dla Akademii i moge odleciec.'),
  ('$gaTJ_HeOrShe smieje sie z nutka szalenstwa.', 'Naukowiec smieje sie z nutka szalenstwa.'),
  ('Zrobilem kopie wszystkich archiwow bazy i...', 'Mam kopie wszystkich archiwow bazy i...'),
  ('$gaTJ_heOrShe usmiecha sie szeroko', 'naukowiec usmiecha sie szeroko'),
  ('Ukrylem wahadlowiec w oslonietym hangarze i wkrotce spotkam cie na orbicie.',
   'Wahadlowiec czeka w oslonietym hangarze. Wkrotce spotkamy sie na orbicie.'),
  ('Za plecami $gaTJ_himOrHer rozlega sie szalenczy alarm. Badacz zerka przez $gaTJ_hisOrHer ramie.',
   'Za plecami naukowca rozlega sie szalenczy alarm. Badacz zerka przez ramie.'),
 ],
 'gaTJPlanetContact3': [
  ('mowi $gaTJ_heOrShe z panika w $gaTJ_hisOrHer oczach', 'mowi naukowiec z panika w oczach'),
  ('$gaTJ_heOrShe grzebie w kieszeni $gaTJ_hisOrHer kombinezonu prozniowego',
   'naukowiec grzebie w kieszeni kombinezonu prozniowego'),
 ],
 'gaTJPlanetContactHaveTJ': [
  ('Slyszalem pogloski. Myslalem, ze to tylko kosmiczne opowiesci.',
   'Dotarly do mnie pogloski. Brzmialy jak kosmiczne opowiesci.'),
  ('$gaTJ_HeOrShe kreci $gaTJ_hisOrHer glowa, ponuro pogodzony z tym, ze $gaTJ_heOrShe zostal uratowany przez kapitana, ktorego glownemu reaktorowi najwyrazniej brakuje oslon.',
   'Naukowiec kreci glowa z ponura rezygnacja. Trudno uwierzyc, ze ratunek nadszedl od kapitana, ktorego glowny reaktor najwyrazniej nie ma oslon.'),
 ],
 'gaTJPlanetContactTakeChip': [
  ('$gaTJ_heOrShe wzdryga sie.', 'naukowiec wzdryga sie.'),
 ],
 'gaTJPlanetContactTakeNN': [
  ('$gaTJ_heOrShe robi krok naprzod', 'naukowiec robi krok naprzod'),
 ],
 'gaFCAskAroundKapteynBar1': [
  ('$gaFC_KBAheOrShe upija dlugi lyk.', 'osoba w plaszczu upija dlugi lyk.'),
 ],
 'gaFCAskAroundKapteynBar3': [
  ('$gaFC_KBAHeOrShe usmiecha sie przebiegle.', 'Osoba w plaszczu usmiecha sie przebiegle.'),
 ],
 'gaFCAskAroundKapteynBarProfit': [
  ('$gaFC_KBAHeOrShe wzrusza ramionami.', 'Osoba w plaszczu wzrusza ramionami.'),
 ],
 'gaFCAskAroundKapteynBarDone': [
  ('$gaFC_KBAHeOrShe salutuje ironicznie', 'Osoba w plaszczu salutuje ironicznie'),
  ('$gaFC_KBAHeOrShe odwraca sie', 'Rozmowca odwraca sie'),
  ('popija $gaFC_KBAhisOrHer drink', 'popija swoj drink'),
 ],
 'gaFCAskAroundKapteynBarMore': [
  ('$gaFC_KBAHeOrShe wzdycha.', 'Osoba w plaszczu wzdycha.'),
  ('$gaFC_KBAHeOrShe stuka w datapad $gaFC_KBAhisOrHer', 'Rozmowca stuka w swoj datapad'),
 ],
 'gaFCKapteynBarBribe1': [
  ('$gaFC_KBAHeOrShe natychmiast przechodzi do ratowania sytuacji.',
   'Osoba w plaszczu natychmiast probuje ratowac sytuacje.'),
  ('$gaFC_KBAHeOrShe bierze gleboki oddech.', 'Po chwili bierze gleboki oddech.'),
  ('$gaFC_KBAHeOrShe oproznia drinka jednym haustem.', 'Rozmowca oproznia drinka jednym haustem.'),
  ('$gaFC_KBAHeOrShe wstaje i kieruje sie do wyjscia.', 'Osoba w plaszczu wstaje i kieruje sie do wyjscia.'),
 ],
 'lptBlurbBar1': [
  ('$lpt_manOrWoman w starannie wykonanych szatach', 'Osoba w starannie wykonanych szatach'),
 ],
 'lptOfferTextBarRich': [
  ('sklada $lpt_hisOrHer dlonie', 'sklada dlonie'),
  ('Wyraz $lpt_hisOrHer pewnosci siebie i jakosc ubrania wskazuja, ze $lpt_heOrShe pochodzi',
   'Pewnosc siebie i jakosc ubrania wskazuja, ze ta osoba pochodzi'),
  ('mowi $lpt_heOrShe.', 'mowi pielgrzym.'),
 ],
 'lptOfferTextBarPoor': [
  ('$lpt_heOrShe usmiecha sie krzywo i sklada $lpt_hisOrHer zrogowaciale dlonie',
   'osoba ta usmiecha sie krzywo i sklada zrogowaciale dlonie'),
  ('mowi $lpt_heOrShe z uklonem', 'mowi pielgrzym z uklonem'),
  ('$lpt_HeOrShe patrzy na ciebie z nadzieja.', 'Pielgrzym patrzy na ciebie z nadzieja.'),
 ],
 'LPTcheckCompletionContRichOneOff': [
  ('pozegnal $lpt_hisOrHer grupe', 'pozegnal cala grupe'),
  ('przekonuje $lpt_heOrShe.', 'przekonuje przywodca pielgrzymow.'),
  ('Kiedys bylem niewierzacy.', 'Kiedys wiara byla mi obca.'),
  ('$lpt_HeOrShe obdarza cie idealnym usmiechem', 'Przywodca pielgrzymow obdarza cie idealnym usmiechem'),
  ('wsiada do promu, ktory $lpt_heOrShe wynajal, ktory zabierze $lpt_himOrHer i $lpt_hisOrHer towarzyszy do sanktuarium.',
   'wsiada do wynajetego promu, ktory zabierze wszystkich pielgrzymow do sanktuarium.'),
 ],
 'LPTcheckNonMarketContRichOneOff': [
  ('pozegnal $lpt_hisOrHer grupe', 'pozegnal cala grupe'),
  ('przekonuje $lpt_heOrShe, a $lpt_heOrShe gestykuluje.',
   'przekonuje przywodca pielgrzymow, zywo gestykulujac.'),
  ('Kiedys sam bylem niewierzacy.', 'Kiedys wiara byla mi obca.'),
  ('$lpt_HeOrShe obdarza cie idealnym usmiechem.', 'Przywodca pielgrzymow obdarza cie idealnym usmiechem.'),
  ('$lpt_HeOrShe wykonuje pobozny gest', 'Po chwili wykonuje pobozny gest'),
  ('ktory zabierze $lpt_himOrHer i $lpt_hisOrHer grupe do sanktuarium.',
   'ktory zabierze wszystkich pielgrzymow do sanktuarium.'),
 ],
 'locrlfBlurbBar': [
  ('$locrlf_manOrWoman obserwuje', 'Osoba z TriPadem obserwuje'),
 ],
 'locrlfOfferOptionBar': [
  ('Zapytaj, czy $locrlf_manOrWoman potajemnie robiacy notatki potrzebuje pomocy',
   'Zapytaj osobe potajemnie robiaca notatki, czy potrzebuje pomocy'),
 ],
 'locrlfOfferTextBarAgain': [
  (' $locrlf_HeOrShe podskakuje nieco', ' - osoba z TriPadem podskakuje nieco'),
  ('$locrlf_HeOrShe scisza $locrlf_hisOrHer glos', 'Nastepnie scisza glos'),
  ('$locrlf_HeOrShe wzdycha.', 'Po chwili wzdycha.'),
 ],
 'locrlfOfferTextBarAgainB': [
  (' $locrlf_HeOrShe podskakuje nieco', ' - osoba z TriPadem podskakuje nieco'),
  ('$locrlf_HeOrShe scisza $locrlf_hisOrHer glos', 'Nastepnie scisza glos'),
  ('$locrlf_HeOrShe wzdycha.', 'Po chwili wzdycha.'),
 ],
 'locrlfOfferTextBar': [
  (' $locrlf_HeOrShe podskakuje nieco', ' - osoba z TriPadem podskakuje nieco'),
  ('$locrlf_heOrShe scisza $locrlf_hisOrHer glos', 'osoba przy stoliku scisza glos'),
  ('$locrlf_HisOrHer oczy rozszerzaja sie z niepokoju.',
   'W oczach rozmowcy pojawia sie niepokoj.'),
 ],
 'locrlfOfferTextBar2': [
  ('$locrlf_HeOrShe pokazuje $locrlf_hisOrHer tani datapad.',
   'Osoba z TriPadem pokazuje ci swoj tani datapad.'),
 ],
 'locrlfOfferBarCynicalRewardAsk': [
  ('Przez twarz $hisOrHer przebiega fala poczucia winy, szybko stlumiona.',
   'Na twarzy posrednika pojawia sie na moment wyraz poczucia winy.'),
  ('$locrlf_HeOrShe niecierpliwie stuka $locrlf_hisOrHer reka w blat baru.',
   'Po chwili osoba ta niecierpliwie stuka reka w blat baru.'),
 ],
 'locrlfOfferBarAcceptFirst': [
  ('identyfikator lacznosci $locrlf_hisOrHer oraz', 'wlasny identyfikator lacznosci oraz'),
 ],
 'locrlfOfferCynicalRewardAsk': [
  ('Przez twarz $hisOrHer przebiega fala poczucia winy, szybko stlumiona.',
   'Na twarzy posrednika pojawia sie na moment wyraz poczucia winy.'),
  ('$HeOrShe niecierpliwie stuka palcami $hisOrHer o komunikator $hisOrHer.',
   'Osoba przy stoliku niecierpliwie stuka palcami w komunikator.'),
 ],
}

ALLOWED_FIELDS = {name: {'options'} if name=='locrlfOfferOptionBar' else {'text'} for name in PATCHES}
# Prevent accidental edits to any unreviewed dynamic-dialogue variables.
SOURCE='data/campaign/rules.csv'
OLD_SHA='c24d09cb29da3cccd01b40e2b8d318988000ebb132ad0de105fdf916e7b00e38'
NEW_SHA='ebcf0741e168dd7046259edeae506caceb6d93cd1f2f9c7ff315f9d52a13428d'

class RawLines:
 def __init__(self,b):self.b=b;self.pos=0
 def __iter__(self):return self
 def __next__(self):
  if self.pos==len(self.b):raise StopIteration
  end=self.b.find(b'\n',self.pos)
  if end<0:end=len(self.b)
  else:end+=1
  line=self.b[self.pos:end];self.pos=end
  return line.decode('ascii')

def rows_with_spans(b):
 reader=RawLines(b);spans=[];begin=0
 for row in csv.reader(reader):
  spans.append((begin,reader.pos,row));begin=reader.pos
 assert begin==len(b)
 return spans

def translate_bytes(b):
 if not b.isascii():raise ValueError('rules.csv contains non-ASCII bytes')
 if hashlib.sha256(b).hexdigest()!=OLD_SHA:raise ValueError('Unexpected prior rules.csv SHA')
 rows=rows_with_spans(b)
 header=rows[0][2];assert header==['id','trigger','conditions','script','text','options','notes']
 selections={}
 for begin,end,row in rows[1:]:
  key=row[0]
  if key in PATCHES:
   if key in selections:raise ValueError(('duplicate ID',key))
   selections[key]=(begin,end,row)
 if set(selections)!=set(PATCHES):raise ValueError(('missing unique IDs',set(PATCHES)-set(selections)))
 blobs=[];last=0;replacement_count=0
 for key,(begin,end,row) in sorted(selections.items(),key=lambda item:item[1][0]):
  chunk=b[begin:end]
  changed=chunk
  for old,new in PATCHES[key]:
   old_b=old.encode('ascii');new_b=new.encode('ascii')
   if changed.count(old_b)!=1:raise ValueError((key,old,changed.count(old_b)))
   if old==new:raise ValueError('no-op')
   changed=changed.replace(old_b,new_b,1);replacement_count+=1
  blobs.append((begin,end,changed));
 result=bytearray();last=0
 for begin,end,changed in blobs:
  result.extend(b[last:begin]);result.extend(changed);last=end
 result.extend(b[last:]);out=bytes(result)
 before=rows;after=rows_with_spans(out)
 if len(before)!=len(after):raise AssertionError('CSV row count changed')
 fields=set();changed_rows=[];bypassed=0
 for (b0,b1,old),(a0,a1,new) in zip(before,after):
  if old[0]!=new[0]:raise AssertionError('CSV row order or id changed')
  diffs={header[j] for j,(x,y) in enumerate(zip(old,new)) if x!=y}
  if diffs:
   fields |= diffs
   if old[0] not in ALLOWED_FIELDS or diffs!=ALLOWED_FIELDS[old[0]]:
    raise AssertionError(('unexpected field',old[0],diffs))
   changed_rows.append(old[0]);bypassed+=sum(x.count('$') for x in old[4:6])-sum(x.count('$') for x in new[4:6])
 if set(changed_rows)!=set(PATCHES):raise AssertionError('not all curated rows changed')
 if out.count(b'\r\n')!=b.count(b'\r\n'):raise AssertionError('CRLF changed')
 if any(v not in {'text','options'} for v in fields):raise AssertionError('non-display field changed')
 if hashlib.sha256(out).hexdigest()!=NEW_SHA:raise AssertionError('Unreviewed resulting rules.csv bytes')
 return out,{'rows':len(rows)-1,'changed_rows':len(changed_rows),'edits':replacement_count,'removed_variable_references':bypassed,'fields':sorted(fields),'rules_sha_before':hashlib.sha256(b).hexdigest(),'rules_sha_after':hashlib.sha256(out).hexdigest()}

def unique(s,old,new):
 if s.count(old)!=1:raise ValueError(('expected one metadata version',old,s.count(old)))
 return s.replace(old,new,1)

def apply(root):
 mod=root/'mod';p=mod/SOURCE
 b=p.read_bytes();out,report=translate_bytes(b)
 p.write_bytes(out)
 info_path=mod/'mod_info.json';info=json.loads(info_path.read_text(encoding='utf8'))
 if info['version']!='1.0.33':raise ValueError('apply after 1.0.33 only')
 info['version']='1.0.34';info['description']=unique(info['description'],'1.0.33','1.0.34')
 if len(info['replace'])!=41:raise AssertionError('unexpected replace list')
 info_path.write_text(json.dumps(info,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
 readme=mod/'CZYTAJ.txt';s=readme.read_text(encoding='utf8')
 s=unique(s,'STARSECTOR PL ASCII 1.0.33','STARSECTOR PL ASCII 1.0.34')
 s+='\nPoprawiono wybrane dialogi Akademii Galatia i pielgrzymow Ludda bez dynamicznych zaimkow EN. Testy Windows w dzialajacej grze nadal wymagane.\n'
 readme.write_text(s,encoding='utf8')
 installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 installer.write_text(unique(installer.read_text(encoding='utf8'),'const edition = "1.0.33"','const edition = "1.0.34"'),encoding='utf8')
 print(json.dumps(report,indent=2));return report

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path);apply(ap.parse_args().worktree)
