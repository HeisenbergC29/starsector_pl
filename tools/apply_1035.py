#!/usr/bin/env python3
"""Patch 1.0.35: precisely reviewed player-visible dialogue strings only.

Uses byte-level CSV splice; leaves scripts, options, IDs, predicates and all
non-target records untouched. Run after tools/apply_1034.py.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from pathlib import Path
from apply_1034 import rows_with_spans

SOURCE='data/campaign/rules.csv'
OLD_SHA='ebcf0741e168dd7046259edeae506caceb6d93cd1f2f9c7ff315f9d52a13428d'
NEW_SHA='c09ff63ee5da19d93e17c66c4e8ed3f1beb0e805c885d6b32d67d878b5291e0d'
PATCHES={}

def p(key,*rules):
    assert key not in PATCHES and rules
    assert all(a != b and a.isascii() and b.isascii() for a,b in rules)
    PATCHES[key]=tuple(rules)

# Tri-Tachyon station contact and specialized ship-hull notices.
p('TTmarketWeirdMods1a',('$HeOrShe przerywa i zaczyna od nowa.','Rozmowca urywa wypowiedz i zaczyna od nowa.'))
p('TTmarketWeirdMods1b',('$HeOrShe oblizuje $hisOrHer wargi i zaczyna ponownie.','Rozmowca oblizuje wargi i zaczyna ponownie.'))
p('TTmarketWeirdMods1c',('$HeOrShe milknie i zaczyna od nowa.','Rozmowca milknie i zaczyna od nowa.'))
p('TTmarketWeirdMods2',(' $heOrShe mruga nerwowo ', ' rozmowca nerwowo mruga '),('dostalem polecenie, ktorego nigdy wczesniej nie widzialem','dotarlo do mnie polecenie, jakiego nigdy wczesniej nie widziano'))
p('TTmarketWeirdMods2OMKI',
  ('$HeOrShe pochyla sie blizej.', 'Rozmowca pochyla sie blizej.'),
  ('Na $hisOrHer twarzy pojawia sie zaklopotanie.', 'Na twarzy rozmowcy pojawia sie zaklopotanie.'),
  ('Niecierpliwy dzwonek przywoluje $himOrHer do porzadku.', 'Niecierpliwy dzwonek przywoluje rozmowce do porzadku.'),
  ('$heOrShe odchrzakuje.', 'Rozmowca odchrzakuje.'),
  ('otrzymalem dyrektywe, jakiej jeszcze nigdy nie widzialem', 'przyszla do mnie dyrektywa, jakiej jeszcze nigdy nie widziano'))
p('TTmarketWeirdMods3b',('odpowiada $heOrShe bez przekonania', 'odpowiada rozmowca bez przekonania'))
p('TTmarketWeirdMods3c',('odpowiada $heOrShe z szeroko otwartymi oczami','odpowiada rozmowca z szeroko otwartymi oczami'))
for key in ['TTmarketWeirdMods4','TTmarketWeirdMods4eochuBres']:
 p(key,
   ('$HeOrShe spoglada na TriPad trzymany w $hisOrHer dloniach.', 'Rozmowca spoglada na TriPad trzymany w dloniach.'),
   ('$HisOrHer spojrzenie wraca', 'Spojrzenie rozmowcy wraca'),
   ('$HeOrShe upewnia sie', 'Rozmowca upewnia sie'))
for key,verb in [('TTmarketWeirdMods6a','stuka w'),('TTmarketWeirdMods6b','dotyka'),('TTmarketWeirdMods6c','dotyka')]:
 if verb=='stuka w': action=('$HeOrShe stuka w $hisOrHer TriPad.', 'Rozmowca stuka w swoj TriPad.')
 else: action=('$HeOrShe dotyka $hisOrHer TriPada.', 'Rozmowca dotyka swojego TriPada.')
 rules=[('$HeOrShe wyglada na zaskoczonego.', 'Na twarzy rozmowcy maluje sie zaskoczenie.'),action]
 if key!='TTmarketWeirdMods6a':
  rules.append(('Zapomnij, ze cokolwiek powiedzialem.', 'Zapomnij o moich slowach.'))
 p(key,*rules)
p('TTmarketWeirdModsOutro2a',('mowi szybko $heOrShe', 'mowi szybko rozmowca'),('$HeOrShe usmiecha sie','Rozmowca usmiecha sie'))
p('TTmarketWeirdModsOutro2b',('$HeOrShe usmiecha sie nieszczerze, udajac, ze $heOrShe nie uslyszal aluzji zawartej w twoim pytaniu, po czym zrywa polaczenie.', 'Rozmowca usmiecha sie nieszczerze, ignorujac aluzje zawarta w twoim pytaniu, po czym zrywa polaczenie.'))
p('TTmarketWeirdModsOutro2aX',('mowi pospiesznie $heOrShe', 'mowi pospiesznie rozmowca'))
p('TTmarketWeirdModsOutro2c',('$HeOrShe szybko zrywa', 'Rozmowca szybko zrywa'))

# Luddic Church patrol: no conflation of the speaker and their crew.
for key in ['CGRmarketWeirdOutro','CGRmarketWeirdOutroCom','CGRmarketWeirdOutroFaith','CGRmarketWeirdOutroComFaith']:
 p(key,('mowi $heOrShe.', 'mowi rozmowca.'),
   ('$HeOrShe splata $hisOrHer dlonie', 'Rozmowca splata dlonie') if key!='CGRmarketWeirdOutroComFaith' else
   ('$HeOrShe sklada $hisOrHer dlonie', 'Rozmowca sklada dlonie'))
for key in ['CGRpatrolWeirdMods0unknown','CGRpatrolWeirdMods0']:
 p(key,('wydusza $heOrShe.', 'wydusza oficer.'))
for key in ['CGRpatrolWeirdModsUnknownEnd','CGRpatrolWeirdModsUnknownEndWeaker','CGRpatrolWeirdModsUnknownEndTrade','CGRpatrolWeirdModsEnd3','CGRpatrolWeirdModsEnd3b']:
 p(key,('Slowa $post sa skierowane do $hisOrHer zalogi','Slowa $post sa skierowane do zalogi patrolu'))
p('CGRpatrolWeirdMods1',('$HeOrShe oglada sie przez $hisOrHer ramie.', 'Oficer oglada sie przez ramie.'))
p('CGRpatrolWeirdMods2a',
  ('$HeOrShe krztusi sie slowami.', 'Oficer krztusi sie slowami.'),
  ('$HeOrShe daje przez ramie $hisOrHer jakis ponaglajacy znak.', 'Oficer daje przez ramie ponaglajacy znak.'),
  ('Wyraz twarzy $HisOrHer jest ponury.', 'Na twarzy oficera pojawia sie ponury wyraz.'))
p('CGRpatrolWeirdMods2b',('$HeOrShe wykonuje przez $hisOrHer ramie gest, jakby poganialo kogos za plecami.', 'Oficer wykonuje przez ramie gest, przywolujac kogos stojacego za plecami.'))
p('CGRpatrolWeirdMods2c',('$HeOrShe daje ponaglajacy znak reka komus stojacemu za $hisOrHer plecami.', 'Oficer daje ponaglajacy znak reka komus stojacemu z tylu.'))
p('CGRpatrolWeirdMods3',
 ('pyta $heOrShe.', 'pyta oficer.'),
 ('Twarz $HisOrHer zbladla, jakby wlasnie uslyszal wyrok.', 'Twarz oficera blednie, jak po uslyszeniu wyroku.'),
 ('Gdy $heOrShe ponownie patrzy w kamere, $heOrShe ma juz spojrzenie wroga stojacego po drugiej stronie frontu.',
  'Gdy oficer ponownie patrzy w kamere, widzisz w oczach wrogosc, jak u kogos stojacego po drugiej stronie frontu.'))
for key in ['CGRpatrolWeirdModsOpt3aSel','CGRpatrolWeirdModsOpt3bSel']:
 p(key,('odpowiada $heOrShe.', 'odpowiada oficer.'))
p('CGRpatrolWeirdModsOpt3dSel',('$heOrShe wypluwa slowa', 'oficer wypluwa slowa'))

# Luddic curator dialogue: make clauses complete rather than replacing 'her' globally.
p('lppHookCurateCalled',('Czy $heOrShe ukrywa cos za $hisOrHer pokazem poboznosci?', 'Czy za tym pokazem poboznosci kryje sie cos wiecej?'))
p('lppHookCurateSegue',('$HeOrShe przyglada ci sie wyczekujaco; milczenie $hisOrHer zdaje sie pytac', 'Kustosz przyglada ci sie wyczekujaco; milczenie zdaje sie pytac'))
p('lppHookCurateAgnosticOut',('""jej ewolucji, jesli tak wolisz"", dodaje $heOrShe.', '""jej ewolucji, jesli tak wolisz"".'))
p('lppHookCurateInfoDump',
  ('$HeOrShe odchrzakuje, czyszczac $hisOrHer gardlo', 'Kustosz odchrzakuje'),
  ('$heOrShe przybiera cierpliwy ton', 'kustosz przybiera cierpliwy ton'))
for key in ['lppHookCurateHowManyA','lppHookCurateHowManyB']:
 p(key,('mowi $heOrShe po chwili zastanowienia', 'mowi kustosz po chwili zastanowienia'))
p('lppHookCurateCredits',('dodaje wyrozumiale $heOrShe', 'dodaje wyrozumiale kustosz'))
for key in ['lppHookCurateVisit','lppHookCuratePilgrimage']:
 p(key,('$HeOrShe wzrusza ramionami', 'Kustosz wzrusza ramionami'))
for key in ['lppHookCurateFascinating','lppHookCurateShrineCoordinates1']:
 p(key,('$HeOrShe niezgrabnie obsluguje', 'Kustosz niezgrabnie obsluguje'),
   ('Pokaz $himOrHer, jak to zrobic', 'Pokaz kustoszowi, jak to zrobic'))
p('lppHookCurateUpload2',('mowi pokornie $heOrShe.', 'mowi pokornie kustosz.'))
p('lppHookCurateSeeyaCynical',('jakby $heOrShe nie wiedzial, jaka droge wybierzesz.', 'jakby twoje zamiary pozostawaly zagadka.'))
p('lppHookCurateSeeyaPather',('jakby $heOrShe obawial sie o twoja przyszla droge.', 'z wyraznym niepokojem o twoja przyszla droge.'))
p('lppHookCurateCottonAsk',('$HeOrShe wypuszcza powietrze.', 'Kustosz wypuszcza powietrze.'))
p('lppHookCurateCottonWontSay',('poprawia $hisOrHer szaty.', 'poprawia szaty.'),('$heOrShe unika twojego wzroku', 'kustosz unika twojego wzroku'))
p('lppHookCurateCottonTalk',('$HeOrShe siada z westchnieniem', 'Kustosz siada z westchnieniem'))
p('lppHookCurateCottonTalk2',('poprawia $hisOrHer szate.', 'poprawia szate.'))
p('lppHookCurateCottonJoin',('Poprawia $hisOrHer szaty.', 'Poprawia szaty.'),('$heOrShe unika twojego wzroku', 'kustosz unika twojego wzroku'))
p('lppHookCurateCottonKill',('Duchowny wzdycha i pociera $hisOrHer oczy, jakby nagle dopadl $himOrHer silny bol glowy, po czym odzywa sie.', 'Duchowny wzdycha, pociera oczy i krzywi sie z naglego bolu glowy, po czym odzywa sie.'))
p('lppHookCurateCottonKill2a',('mowi $heOrShe z bolem w glosie.', 'mowi kustosz z bolem w glosie.'))

# Shared, short greeting branches. No changes to spoken dialogue IDs/choice IDs.
p('convDefaultGreeting2',('$HeOrShe podnosi wzrok.', 'Rozmowca podnosi wzrok.'))
p('convDefaultGreeting2official',('$HeOrShe rzuca ci spojrzenie.', 'Rozmowca rzuca ci spojrzenie.'))
p('convDefaultGreeting2business',('pyta $HeOrShe.', 'pyta rozmowca.'),('Powinienem pobierac oplate za kazda minute.', 'Za kazda minute powinna byc dodatkowa oplata.'))
p('convDefaultGreeting2villain',('$HeOrShe przybiera mine pelna falszywej troski.', 'Rozmowca przybiera mine pelna falszywej troski.'))
for key in ['convDefaultGreeting2soldier','convDefaultGreeting2faithful','convDefaultGreeting2pather']:
 p(key,(' $heOrShe.', ' rozmowca.'))
p('convDefaultGreeting2scientist',('$HeOrShe zerka na ciebie.', 'Rozmowca zerka na ciebie.'))

# Every changed row must have all targeted gender-variable placeholders removed.
OPTION_IDS=frozenset({'lppHookCurateFascinating','lppHookCurateShrineCoordinates1'})
PRONOUN=re.compile(rb'\$(?:[A-Za-z_]*)(?:[Hh]eOrShe|[Hh]imOrHer|[Hh]isOrHer|[Mm]anOrWoman|[Hh]imOrHerself)\b')

def sha(b): return hashlib.sha256(b).hexdigest()

def patch_bytes(blob: bytes, *, expected_hash=OLD_SHA):
 if sha(blob)!=expected_hash:raise ValueError('Unrecognized original rules.csv checksum')
 if not blob.isascii():raise ValueError('Non-ASCII rules.csv')
 spans=rows_with_spans(blob)
 assert spans[0][2]==['id','trigger','conditions','script','text','options','notes']
 found={};pairs=0;prior_refs=0;after_refs=0;chunks=[]
 for start,end,row in spans[1:]:
  key=row[0]
  if key not in PATCHES:continue
  if key in found:raise ValueError('Duplicate dialogue ID '+key)
  found[key]=True
  if len(row)!=7:raise ValueError(('Malformed CSV row',key))
  if row[5] and PRONOUN.search(row[5].encode('ascii')) and key not in OPTION_IDS:raise ValueError(('Variable in options in selected ID',key))
  prior_refs+=len(PRONOUN.findall((row[4]+' '+row[5]).encode('ascii')))
  oldchunk=blob[start:end];current=oldchunk
  for source,target in PATCHES[key]:
   a,b=source.encode('ascii'),target.encode('ascii')
   if current.count(a)!=1:raise ValueError((key,source,current.count(a)))
   current=current.replace(a,b,1);pairs+=1
  # Non-target fields must remain unchanged even if a string replacement crosses CSV columns.
  parsed=list(csv.reader(current.decode('ascii').splitlines(keepends=True)))
  if len(parsed)!=1:raise ValueError(('CSV record split',key))
  if len(parsed[0])!=7:raise ValueError(('CSV field count',key))
  if parsed[0][:4]!=row[:4] or parsed[0][6:]!=row[6:]:raise ValueError(('Non-text field touched',key))
  if key not in OPTION_IDS and parsed[0][5]!=row[5]:raise ValueError(('Unexpected options change',key))
  if key in OPTION_IDS:
   before=[ln.partition(':')[0] for ln in row[5].splitlines()]
   after=[ln.partition(':')[0] for ln in parsed[0][5].splitlines()]
   if before!=after or len(before)!=1:raise ValueError(('Option IDs modified',key))
  remain=PRONOUN.findall((parsed[0][4]+' '+parsed[0][5]).encode('ascii'))
  if remain:raise ValueError(('Unresolved variable',key,remain))
  after_refs+=len(remain)
  chunks.append((start,end,current))
 if set(found)!=set(PATCHES):raise ValueError(('Missing IDs',sorted(set(PATCHES)-set(found))))
 output=bytearray();last=0
 for start,end,chunk in chunks:
  output.extend(blob[last:start]);output.extend(chunk);last=end
 output.extend(blob[last:]);ret=bytes(output)
 if len(rows_with_spans(ret))!=len(spans):raise ValueError('CSV row count changed')
 if not ret.isascii() or b'\n' in ret.replace(b'\r\n',b''):raise ValueError('Invalid newlines or encoding')
 return ret,dict(changed_rows=len(chunks),exact_replacements=pairs,gender_variables_removed=prior_refs-after_refs,remaining_variables_in_changed_rows=after_refs,sha256=sha(ret))

def main(root):
 file=root/'mod'/SOURCE
 result,report=patch_bytes(file.read_bytes())
 if report['sha256']!=NEW_SHA:raise ValueError('Wrong final checksum')
 file.write_bytes(result)
 mod=root/'mod';info=mod/'mod_info.json';meta=json.loads(info.read_text('utf8'))
 assert meta['version']=='1.0.34'
 meta['version']='1.0.35'; meta['description']=meta['description'].replace('1.0.34','1.0.35')
 info.write_text(json.dumps(meta,indent=2,ensure_ascii=True)+'\n','utf8')
 p=mod/'CZYTAJ.txt';r=p.read_text('utf8');assert 'STARSECTOR PL ASCII 1.0.34' in r
 p.write_text(r.replace('STARSECTOR PL ASCII 1.0.34','STARSECTOR PL ASCII 1.0.35')+'\nPrzeredagowano kolejne dialogi z zaimkami dynamicznymi: porty Tri-Tachyon, patrole Ludda i kustosz sanktuarium.\n','utf8')
 ins=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';old=ins.read_text('utf8')
 assert old.count('const edition = "1.0.34"')==1
 ins.write_text(old.replace('const edition = "1.0.34"','const edition = "1.0.35"'),'utf8')
 print(json.dumps(report,indent=2))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('worktree',type=Path)
 main(parser.parse_args().worktree)
