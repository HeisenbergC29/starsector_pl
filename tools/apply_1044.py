#!/usr/bin/env python3
"""1.0.44: contextual replacement of gendered $manOrWoman in selected rules.csv.

Scope: only a curated list of text fragments in unique dialogue records; no
conditions, scripts, identifiers, option labels or executable Java changes.
"""
from __future__ import annotations
import argparse, hashlib, csv, json
from pathlib import Path
from apply_1034 import rows_with_spans

PREVIOUS_SHA='a43f8a4f5acf91e67c7331c7828e3152564f2e224ea2a6bb46e49b9d6374f8a0'
PATCHES={}
def p(key,*edits):
    if key in PATCHES or not edits or any(not x.isascii() or not y.isascii() or x==y for x,y in edits):
        raise ValueError('invalid patch '+key)
    PATCHES[key]=edits

p('GAKA_TTStart',('podchodzi do ciebie $manOrWoman w nieskazitelnym stroju','podchodzi do ciebie osoba w nieskazitelnym stroju'))
p('genericGreetingNeedTOff',('$manOrWoman zaczyna cos mowic','Osoba po drugiej stronie lacza zaczyna cos mowic'))
p('genericGreetingNeedNoPatrols',('$manOrWoman zaczyna mowic','Osoba po drugiej stronie lacza zaczyna mowic'))
p('genericGreetingNeedNoPatrolsUW',('$manOrWoman zaczyna mowic','Osoba po drugiej stronie lacza zaczyna mowic'))
p('proComTextRemoteBarUnderworld',('Podchodzisz do $manOrWoman, gdy','Podchodzisz do rozmowcy, gdy'),('$HisOrHer oko drga','Oko rozmowcy drga'))
p('cpcOfferTextBar1',('elegancko ubrany $manOrWoman nagle konczy','elegancko ubrana osoba nagle konczy'))
p('cpcOfferTextBarCoilGun',('$manOrWoman zbyt gwaltownie odklada datapad','Rozmowca zbyt gwaltownie odklada datapad'))
p('psbOfferTextBar',('$manOrWoman skupia juz cala uwage na tobie','rozmowca skupia juz cala uwage na tobie'))
p('ssatOfferTextBarUW',('ten $manOrWoman ma powiazania','ta osoba ma powiazania'))
for id in ('extrOfferTextBar1','extrOfferTextBar2','extrOfferTextBar3'):
    p(id,('$manOrWoman siedzi w cieniu','Osoba siedzi w cieniu'),('$manOrWoman kladzie','Rozmowca kladzie'))
p('LOCRMcontact1',('Na twarzy $manOrWoman maluje sie','Na twarzy rozmowcy maluje sie'))
p('LOCRPcontact1',('Twarz $manOrWoman pojawia sie','Twarz rozmowcy pojawia sie'))
p('LOCRPwhyAreYouHere',('Na twarzy $manOrWoman pojawia sie','Na twarzy rozmowcy pojawia sie'))
p('LOCRLaskHowManyB',('$manOrWoman podnosi na ciebie pelne nadziei spojrzenie','Rozmowca podnosi na ciebie pelne nadziei spojrzenie'))
p('AVIPTblurbBar',('Bardzo elegancko ubrany $manOrWoman zasypuje','Bardzo elegancko ubrana osoba zasypuje'))
p('AVIPTtextBarAccept',('$manOrWoman na kilka sekund przestaje cie zagadywac','rozmowca na kilka sekund przestaje cie zagadywac'))
p('AVIPTtextBarDecline',('elegancko ubrany $manOrWoman powoli nakreca $himOrHerself do kolejnej, nieco innej wscieklosci','elegancko ubrana osoba powoli wpada w kolejny napad wscieklosci'))
p('AVIPTtextBarDeclineRude',('Elegancko ubrany $manOrWoman, postawiony wprost przed sprawa','Elegancko ubrana osoba, postawiona wprost przed sprawa'),('Usta $HisOrHer otwieraja sie','Usta rozmowcy otwieraja sie'))
p('sitmBlurbBar1',('Krzykliwie ubrana osoba $manOrWoman w','Krzykliwie ubrana osoba w'))
p('sitmContactMissionAcceptBar',('Placisz, a $manOrWoman znajduje wymowke','Placisz, a rozmowca znajduje wymowke'))
p('LOCRPnotLuddies',('$manOrWoman energicznie przytakuje','Rozmowca energicznie przytakuje'))
p('LOCRLaskPaymentA',('$manOrWoman patrzy w gore z nadzieja','Rozmowca patrzy w gore z nadzieja'))
p('LOCRLaskPaymentB',('$manOrWoman patrzy w gore z nadzieja','Rozmowca patrzy w gore z nadzieja'))

PREFIXES=('$manOrWoman','$ManOrWoman','$himOrHerself','$HimOrHerself','$HisOrHer','$hisOrHer')
def sha(b):return hashlib.sha256(b).hexdigest()
def patch_bytes(source,strict=True):
    if strict and sha(source)!=PREVIOUS_SHA: raise ValueError('Requires exact 1.0.43 rules.csv')
    if not source.isascii() or b'\n' in source.replace(b'\r\n',b''): raise ValueError('ASCII/CRLF violation')
    rows=rows_with_spans(source)
    if rows[0][2]!=['id','trigger','conditions','script','text','options','notes']:raise ValueError('Unexpected CSV columns')
    edits=[];ledger=[];seen=set();removed=0
    for start,end,row in rows[1:]:
        key=row[0]
        if key not in PATCHES:continue
        if key in seen or len(row)!=7:raise ValueError('Duplicate/broken row '+key)
        seen.add(key)
        oldtext=row[4];newtext=oldtext
        for old,new in PATCHES[key]:
            if newtext.count(old)!=1:raise ValueError('Expected phrase exactly once in '+key+': '+old)
            newtext=newtext.replace(old,new,1)
        chunk=source[start:end]
        # Replace only the raw CSV text cell by performing exact escaped edits and
        # checking that every non-text column remains byte-equivalent after parsing.
        revised=chunk
        for old,new in PATCHES[key]:
            a=old.replace('"','""').encode('ascii');b=new.replace('"','""').encode('ascii')
            if revised.count(a)!=1:raise ValueError('Raw occurrence mismatch '+key)
            revised=revised.replace(a,b,1)
        reparse=list(csv.reader(revised.decode('ascii').splitlines(keepends=True)))
        if len(reparse)!=1 or len(reparse[0])!=7 or reparse[0][:4]!=row[:4] or reparse[0][5:]!=row[5:] or reparse[0][4]!=newtext:
            raise ValueError('Non-display field modified '+key)
        left=sum(oldtext.count(x) for x in PREFIXES);right=sum(newtext.count(x) for x in PREFIXES)
        if left-right<1:raise ValueError('No gender references removed '+key)
        removed+=left-right
        ledger.append({'id':key,'old_text_sha256':sha(oldtext.encode('ascii')),'new_text_sha256':sha(newtext.encode('ascii')),'edits':len(PATCHES[key]),'removed':left-right})
        edits.append((start,end,revised))
    if seen!=set(PATCHES):raise ValueError(('Missing IDs',sorted(set(PATCHES)-seen)))
    out=bytearray();last=0
    for a,b,x in edits:out.extend(source[last:a]);out.extend(x);last=b
    out.extend(source[last:]);out=bytes(out)
    if len(rows_with_spans(out))!=len(rows) or not out.isascii() or b'\n' in out.replace(b'\r\n',b''):
        raise ValueError('Illegal CSV structural change')
    return out,{'version':'1.0.44','rows_changed':len(edits),'fragments_changed':sum(map(len,PATCHES.values())),'gender_references_removed':removed,'before_sha256':sha(source),'after_sha256':sha(out)},ledger

def apply(root):
    root=Path(root);p=root/'mod/data/campaign/rules.csv';old=p.read_bytes();new,report,ledger=patch_bytes(old);p.write_bytes(new)
    info=root/'mod/mod_info.json';meta=json.loads(info.read_text('utf8'))
    if meta['version']!='1.0.43' or meta['description'].count('1.0.43')!=1:raise ValueError('Bad predecessor version')
    meta['version']='1.0.44';meta['description']=meta['description'].replace('1.0.43','1.0.44');info.write_text(json.dumps(meta,indent=2,ensure_ascii=True)+'\n','utf8')
    f=root/'mod/CZYTAJ.txt';contents=f.read_text('utf8')
    if contents.count('STARSECTOR PL ASCII 1.0.43')!=1:raise ValueError('Bad readme version')
    f.write_text(contents.replace('STARSECTOR PL ASCII 1.0.43','STARSECTOR PL ASCII 1.0.44')+'\nPoprawiono odmiane zdaniowa w kolejnych 25 dialogach, usuwajac polaczenia z angielskim $manOrWoman oraz inne niebezpieczne zaimki.\n',encoding='utf8')
    f=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';contents=f.read_text('utf8')
    if contents.count('const edition = "1.0.43"')!=1:raise ValueError('Wrong installer version')
    f.write_text(contents.replace('const edition = "1.0.43"','const edition = "1.0.44"'),encoding='utf8')
    return report,ledger

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path);ap.add_argument('--ledger-out',type=Path)
    a=ap.parse_args();report,ledger=apply(a.worktree)
    if a.ledger_out: a.ledger_out.write_text(json.dumps({'stats':report,'approved':ledger},indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2))