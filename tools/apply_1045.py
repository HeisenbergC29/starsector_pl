#!/usr/bin/env python3
"""Starsector PL 1.0.45: precise context-safe gender-pronoun repairs in rules.csv.

Apply to the exact 1.0.44 baseline. Touch only displayed text cells of 44
explicitly identified records; no technical fields, Java, or JAR translations.
Record the complete text hash before and after each change. This is an offline
translation review, NOT an in-game claim.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
from apply_1034 import rows_with_spans

PREVIOUS_SHA = 'cf1e35899c5cebd42430cf45242662a6c59389e3330c493c6b667bf2eafb918b'
PATCHES={}
def p(key,*edits):
    if key in PATCHES or not edits or any(a==b or not a.isascii() or not b.isascii() for a,b in edits):
        raise ValueError('invalid patch plan '+key)
    PATCHES[key]=edits

# Luddic Path contacts, and the direct consequences of encountered fleet mods.
p('PathMarketWeird1',('gdy $heOrShe wykrzykuje te slowa','gdy rozmowca wykrzykuje te slowa'))
p('PathMarketWeird2',('$HeOrShe rozpaczliwie splata $hisOrHer dlonie','Rozmowca rozpaczliwie splata dlonie'))
p('PathFleetWeirdMods0tithe',
  ('$HeOrShe ponownie patrzy przez kanal lacznosci','Wyznawca Sciezki ponownie patrzy przez kanal lacznosci'),
  ('$HisOrHer twarz wypelnia groza','Twarz wyznawcy wypelnia groza'),
  ('$HisOrHer wzrok wraca do kanalu lacznosci','Wzrok wyznawcy wraca do kanalu lacznosci'))
p('PathFleetWeirdMods0unknown',('wydusza $heOrShe','wydusza wyznawca Sciezki'))
p('PathFleetWeirdMods1',('gdy $heOrShe krzyczy','gdy wyznawca Sciezki krzyczy'),('wrzeszczy $heOrShe','wrzeszczy wyznawca Sciezki'))
p('PathFleetWeirdModsAgainStart',('dyszy $heOrShe','dyszy wyznawca Sciezki'))
p('PathFleetWeirdModsAgain2',('do zalogi $hisOrHer','do wlasnej zalogi'))

# Generic greetings and authority patrols; replace grammatical pronouns in
# explicit player-facing sentences, without assuming the NPC's sex.
p('greetingDefaultHostileWeakerDefiant',('oznajmia $heOrShe','oznajmia rozmowca'))
p('greetingDefaultInfamous',
  ('$heOrShe zerka na $hisOrHer ekran','rozmowca zerka na swoj ekran'),
  ('pod $hisOrHer nosem','pod nosem'),
  ('$HeOrShe prostuje $hisOrHer plecy','Rozmowca prostuje sie'),
  ('$heOrShe z zaklopotaniem odchrzakuje, zaslaniajac $hisOrHer usta','rozmowca z zaklopotaniem odchrzakuje, zaslaniajac usta'))
p('greetingHegemonyHostileWeakerDefiant',('oznajmia $heOrShe','oznajmia rozmowca'))
p('TTpatrolWeirdMods0',('$post przerywa $hisOrHer nienaturalnie radosny wstep','$post przerywa nienaturalnie radosny wstep'),('$HisOrHer wzrok','Wzrok rozmowcy'))
p('TTpatrolWeirdMods2',('$HeOrShe milknie','Rozmowca milknie'),('$HeOrShe zerka','Rozmowca zerka'),('$HisOrHer wzrok','Wzrok rozmowcy'))
p('TTpatrolWeirdMods2OMKI',('$HeOrShe milknie','Rozmowca milknie'),('$HeOrShe wpatruje','Rozmowca wpatruje'),('$HisOrHer wzrok','Wzrok rozmowcy'))
p('TTpatrolWeirdMods3b',('$heOrShe nie potrafi','rozmowca nie potrafi'),('wyznaje w koncu $heOrShe','wyznaje w koncu rozmowca'))
p('TTpatrolWeirdMods3OMKI',('mowi $heOrShe','mowi rozmowca'))
p('TTpatrolWeirdMods4',('$HeOrShe spoglada na $hisOrHer drugi ekran','Rozmowca spoglada na drugi ekran'),('$HeOrShe znow patrzy','Rozmowca znow patrzy'))
p('TTpatrolWeirdMods5a',('$HeOrShe znow odwraca wzrok','Rozmowca znow odwraca wzrok'),('na $hisOrHer twarzy','na twarzy rozmowcy'))
p('TTpatrolWeirdMods5b',('$HeOrShe spoglada','Rozmowca spoglada'))
p('greetingDiktatHostileWeakerDefiant',('mowi $heOrShe i zrywa polaczenie','mowi rozmowca i zrywa polaczenie'),('Wyraz twarzy $HisOrHer tezeje','Twarz rozmowcy tezeje'))
p('greetingLCHostileWeakerDefiant',('do $hisOrHer boga','do swojego boga'))

# Luddic Path tithe negotiation, keeping all prices and scenario variables.
p('payMegaTitheSel',('$heOrShe stwierdza','wyznawca Sciezki stwierdza'),('wyjasnia $heOrShe','wyjasnia rozmowca'))
p('payMegaTitheOtherSel',('do $hisOrHer zalogi','do swojej zalogi'),('$HeOrShe odwraca sie','Rozmowca odwraca sie'),('$heOrShe teraz wyraznie sie peszy','rozmowca teraz wyraznie sie peszy'),('mowi $heOrShe z przekonaniem','mowi rozmowca z przekonaniem'))
p('payMegaTitheConfirmSel',('mowi pogodnie $heOrShe','mowi pogodnie wyznawca Sciezki'),('ocierajac lze z oka $hisOrHer','ocierajac lze z oka'))
p('payMegaTitheNeverMindSel',('$HisOrHer zerka szybko','Wyznawca zerka szybko'))
p('gaVIPWorkingForKanta1',('zaskakuje to $himOrHer','zaskakuje to pirackiego kapitana'))
p('gaVIPWorkingForKanta2',('jakby $heOrShe wlasnie otrzymal','jakby wlasnie otrzymal'),('$HeOrShe probuje sie opanowac','Pirat probuje sie opanowac'),('cala $hisOrHer postawa','cala postawa pirata'))

# Luddic Path investigation: person-independent expressions, with the same
# speakers and the same original conditions/scripts retained.
p('lkePatherFleetOpenComm',('zaczyna $heOrShe','zaczyna rozmowca'))
p('lkePatherFleetStartLikePath',('$heOrShe na chwile usmiecha','Rozmowca na chwile usmiecha'))
p('lkePatherFleetStartJangSup',('$HeOrShe usmiecha','Rozmowca usmiecha'),('$HeOrShe przestaje','Rozmowca przestaje'))
p('lkePatherFleetStartCotton',('$HeOrShe usmiecha','Rozmowca usmiecha'),('$HeOrShe kreci $hisOrHer glowa','Rozmowca kreci glowa'),('$HeOrShe wzdycha','Rozmowca wzdycha'),('blaga $heOrShe','blaga rozmowca'))
p('LKEpatherFleetNotStoppingB',('mowi $heOrShe','mowi rozmowca'))
p('LKEpatherFleetAskCottonSay',('wiadomosc", $heOrShe spoglada na ciebie z ciekawoscia i obawa, gdy $heOrShe mowi.','wiadomosc". Rozmowca spoglada na ciebie z ciekawoscia i obawa.'))
p('LKEpatherFleetThreatNope',('mowi $heOrShe','mowi rozmowca'),('$HeOrShe zrywa','Rozmowca zrywa'))
p('LKEpatherFleetThreatA',('kreci $hisOrHer glowa','kreci glowa'))
p('LKEpatherFleetThreatB',('kreci $hisOrHer glowa','kreci glowa'),('$heOrShe zrywa','rozmowca zrywa'))
p('LKEpatherFleetCeaseLie',('$HeOrShe sklada $hisOrHer dlonie','Rozmowca sklada dlonie'))
p('LKEpatherFleetCeaseLie2',('$HeOrShe sklada $hisOrHer dlonie','Rozmowca sklada dlonie'))
p('LKEpatherFleetCeaseLie3',('$HeOrShe przez chwile sklada dlonie $hisOrHer','rozmowca przez chwile sklada dlonie'),('$HeOrShe opuszcza dlonie $hisOrHer','Rozmowca opuszcza dlonie'))
p('LKEpatherFleetServeFaith',('mowi $heOrShe','mowi rozmowca'))
p('LKEpatherFleetServeFaithA1',('$HeOrShe wpatruje','Rozmowca wpatruje'),('sklada $hisOrHer dlonie','sklada dlonie'),('$personName otwiera $hisOrHer oczy','$personName otwiera oczy'))
p('LKEpatherFleetServeFaithB1',('Spojrzenie $HisOrHer twardnieje','Spojrzenie rozmowcy twardnieje'),('syczy $heOrShe','syczy rozmowca'))
p('LKEpatherFleetServePath',('mowi $heOrShe','mowi rozmowca'),('$HeOrShe wzdycha i sklada $hisOrHer dlonie','Rozmowca wzdycha i sklada dlonie'))
p('LKEpatherFleetSPOpt2',('mowi $heOrShe, byc moze $heOrShe przypomina sobie','mowi rozmowca; byc moze przypomina sobie'),('$HeOrShe odwraca wzrok','Rozmowca odwraca wzrok'),('Swiadom, jak to zabrzmialo, $heOrShe szybko dodaje','Zauwazajac, jak to zabrzmialo, rozmowca szybko dodaje'))
p('LKEpatherFleetSPOpt3',('Skladajac $hisOrHer dlonie','Skladajac dlonie'),('przekonujesz $heOrShe','przekonujesz rozmowce'))

# Importantly, only the declared generic pronoun placeholders are removed. Do
# not remove distinct gameplay variables such as $personName/$rank/$post/$shipOrFleet.
GENDER=re.compile(r'\$(?:[Hh]eOrShe|[Hh]isOrHer|[Hh]imOrHer|[Hh]imOrHerself|[Mm]anOrWoman)\b')
def sha(data):return hashlib.sha256(data).hexdigest()
def patch_bytes(blob:bytes,require_hash=True):
    if require_hash and sha(blob)!=PREVIOUS_SHA:raise ValueError('Expected exact 1.0.44 rules.csv SHA')
    if not blob.isascii() or b'\n' in blob.replace(b'\r\n',b''):raise ValueError('Expected ASCII CRLF rules.csv')
    spans=rows_with_spans(blob)
    if spans[0][2]!=['id','trigger','conditions','script','text','options','notes']:
        raise ValueError('Unexpected rules.csv columns')
    found=set();deltas=[];ledger=[];changes=0;eliminated=0
    for a,b,r in spans[1:]:
        id=r[0]
        if id not in PATCHES:continue
        if id in found or len(r)!=7:raise ValueError('Duplicated/invalid ID '+id)
        found.add(id);old=r[4];new=old;block=blob[a:b]
        for before,after in PATCHES[id]:
            if new.count(before)!=1:raise ValueError(('Unexpected text context',id,before,new.count(before)))
            new=new.replace(before,after,1)
            rawbefore=before.replace('"','""').encode('ascii');rawafter=after.replace('"','""').encode('ascii')
            if block.count(rawbefore)!=1:raise ValueError(('Ambiguous raw context',id,before))
            block=block.replace(rawbefore,rawafter,1);changes+=1
        parsed=list(csv.reader(block.decode('ascii').splitlines(keepends=True)))
        if len(parsed)!=1 or len(parsed[0])!=7 or parsed[0][:4]!=r[:4] or parsed[0][5:]!=r[5:] or parsed[0][4]!=new:
            raise ValueError(('Non-text field change',id))
        n=len(GENDER.findall(old));n2=len(GENDER.findall(new))
        if n<1 or n2!=0:raise ValueError(('Residual gender placeholder',id,n,n2))
        eliminated+=n
        ledger.append({'id':id,'old_text_sha256':sha(old.encode('ascii')),'new_text_sha256':sha(new.encode('ascii')),'edits':len(PATCHES[id]),'removed_gender_references':n})
        deltas.append((a,b,block))
    if found!=PATCHES.keys():raise ValueError(('Missing IDs',sorted(PATCHES.keys()-found)))
    merged=bytearray();last=0
    for a,b,chunk in deltas:merged.extend(blob[last:a]);merged.extend(chunk);last=b
    merged.extend(blob[last:]);merged=bytes(merged)
    if not merged.isascii() or b'\n' in merged.replace(b'\r\n',b'') or len(rows_with_spans(merged))!=len(spans):
        raise ValueError('Invalid resulting rules.csv')
    report={'version':'1.0.45','rows_changed':len(deltas),'fragments_changed':changes,
            'gender_references_removed':eliminated,'before_sha256':sha(blob),'after_sha256':sha(merged)}
    return merged,report,ledger

def apply(root):
    root=Path(root);file=root/'mod/data/campaign/rules.csv'
    old=file.read_bytes();new,report,ledger=patch_bytes(old)
    m=root/'mod/mod_info.json';meta=json.loads(m.read_text('utf8'))
    if meta['version']!='1.0.44':raise ValueError('Invalid previous version')
    info=root/'mod/CZYTAJ.txt';v=info.read_text('utf8')
    if v.count('STARSECTOR PL ASCII 1.0.44')!=1:raise ValueError('Invalid previous readme')
    installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';src=installer.read_text('utf8')
    if src.count('const edition = "1.0.44"')!=1:raise ValueError('Invalid previous installer source')
    file.write_bytes(new)
    meta['version']='1.0.45';meta['description']=meta['description'].replace('1.0.44','1.0.45')
    m.write_text(json.dumps(meta,indent=2,ensure_ascii=True)+'\n','utf8')
    info.write_text(v.replace('STARSECTOR PL ASCII 1.0.44','STARSECTOR PL ASCII 1.0.45')+
                    '\nPoprawiono kolejne dynamiczne zdania w dialogach kontaktow, patroli i misji Sciezki Ludda. Weryfikacja graficzna w grze nadal wymagana.\n',encoding='utf8')
    installer.write_text(src.replace('const edition = "1.0.44"','const edition = "1.0.45"'),encoding='utf8')
    return report,ledger

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('worktree',type=Path);parser.add_argument('--ledger-out',type=Path)
    a=parser.parse_args();rep,ledger=apply(a.worktree)
    if a.ledger_out:a.ledger_out.write_text(json.dumps({'stats':rep,'approved':ledger},indent=2,ensure_ascii=True)+'\n',encoding='utf8')
    print(json.dumps(rep,indent=2))
