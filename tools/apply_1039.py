#!/usr/bin/env python3
"""Starsector PL 1.0.39: conservative pronoun-free player-facing dialogue edits.

Run after apply_1038. Byte-only CSV splices: other fields and rows unchanged.
Do not treat removed rules variables as repaired JVM getter calls.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
from apply_1034 import rows_with_spans

SOURCE='data/campaign/rules.csv'
OLD_SHA='c09ff63ee5da19d93e17c66c4e8ed3f1beb0e805c885d6b32d67d878b5291e0d'
NEW_SHA='fd7697b869bc4951204a7e90583ab8526ae1d046ba715454048b7cbaedcd3751'
PATCHES={}
def p(key,*parts):
    assert key not in PATCHES and parts and all(a!=b and a.isascii() and b.isascii() for a,b in parts)
    PATCHES[key]=parts

# Ordinary fleet greetings, corporation patrols, inspections.
p('greetingDefaultInfamousFriendly',('$HeOrShe wyglada na zaklopotanego.','Na twarzy rozmowcy maluje sie zaklopotanie.'))
p('greetingTTHostileWeakerDefiant',('mowi $heOrShe.','oswiadcza oficer.'))
p('TTpatrolWeirdMods1a',('mowi $heOrShe.','odpowiada oficer.'))
for key in ('TTpatrolWeirdMods3a','TTpatrolWeirdMods3c'):
    p(key,('$HeOrShe odchrzakuje, zaslaniajac $hisOrHer usta.','Oficer odchrzakuje, zaslaniajac usta.'))
p('TTpatrolWeirdMods6',('$HeOrShe udaje kaszel','Oficer udaje kaszel'))
for key in ('customsInspectionConvStart','customsInspectionResultToll'):
    p(key,('$hisOrHer konsoli','konsoli'))
p('lppJangalaProtestMarinesHelp',('kreci $hisOrHer glowa','kreci glowa'),('mowi $heOrShe z irytacja','dodaje z irytacja'))
p('lppJangalaProtestInfoHegCom',('mowi $heOrShe, wskazujac protest','mowi oficer, wskazujac protest'))

# Luddic pilgrimage/Chalcedon. Keep character-specific spoken text untouched.
p('LKEchalVIPdemandBornanew',('Na twarzy $hisOrHer nie widac rozpoznania.','Na twarzy rozmowcy nie widac oznak rozpoznania.'))
p('LKEchalVIPdemandRecruiter',('wypluwa $heOrShe.','cedzi rozmowca.'))
p('LKEchalcedonThreatSedgeA',('mowi $heOrShe, pocac sie.','mowi rozmowca, ocierajac pot z czola.'))
p('LKEchalcedonThreatSedgeC',('mowi $heOrShe z rozpaczliwym usmiechem','mowi rozmowca z rozpaczliwym usmiechem'))
p('lkeChalcedonVIPstartChurch',('zaczyna $heOrShe z odrobina podejrzliwosci w glosie','zaczyna rozmowca z odrobina podejrzliwosci w glosie'),('$HeOrShe usmiecha sie uspokajajaco','Rozmowca usmiecha sie uspokajajaco'))
p('lkeChalcedonVIPreason1',('$heOrShe usmiecha sie','rozmowca usmiecha sie'))
p('lkeChalcedonVIPreason3',('$HeOrShe unosi brew','Rozmowca unosi brew'))
p('lkeChalcedonLookingRecruiterC',('$HeOrShe wydaje z siebie wymuszony smiech','Rozmowca smieje sie z przymusem'))
p('lkeChalcedonLookingBornanewA3b',('mowi nerwowo $heOrShe','mowi nerwowo rozmowca'))
p('lkePatherFleetDefault',('$HeOrShe usmiecha sie ponuro','Dowodca usmiecha sie ponuro'))
p('LKEpatherFleetNotStopping',('mowi $heOrShe niemal ze zdumieniem','mowi dowodca niemal ze zdumieniem'))
p('LKEpatherFleetAskCottonContact',('$HeOrShe nerwowo przeciera $hisOrHer czolo','Rozmowca nerwowo przeciera czolo'))
p('LKEmazalotAskPortmasterPath',('mowi $heOrShe, odczytujac cos z terminala','mowi urzednik, odczytujac cos z terminala'))
p('LKEmazalotAskPMYaribayB1',('Na twarzy $heOrShe pojawia sie pusty wyraz kogos, kto zamierza odpowiadac na pytania doslownie i ani slowem wiecej.','Na twarzy urzednika pojawia sie wyraz sugerujacy, ze odpowie tylko na bezposrednie pytania.'))
p('LKEmazalotAskPMresp5Opt',('$heOrShe wyglada na uspokojonego','rozmowca odzyskuje spokoj'))
p('LKEmazQMTryYaribayForget',('$heOrShe przez chwile wyglada na zdezorientowanego','Kwatermistrz przez chwile milknie w zaklopotaniu'))
p('LKEmazalotAskAdministrator0',('$HeOrShe zwraca wiecej uwagi na terminal niz na polaczenie','Administrator zwraca wiecej uwagi na terminal niz na polaczenie'))
p('LKEmazalotAskAdminBugged',('$HeOrShe spoglada na terminal, a potem na ciebie','Administrator spoglada na terminal, a potem na ciebie'))
p('LKEmazAdminAskBugC',('$HeOrShe przewraca $hisOrHer oczami','Administrator przewraca oczami'))

# Faith, contacts and data-sale responses.
p('BFFIstationBuyer1',('Twarz $HisOrHer wykrzywia pogarda','Twarz rozmowcy wykrzywia pogarda'))
p('BFFIstationConfront1',('$HeOrShe usmiecha sie drwiaco','rozmowca usmiecha sie drwiaco'))
p('BFFIpsRuseOpenNice2',('$HeOrShe wyraznie nie jest zadowolony z twoich warunkow','Wyraz twarzy rozmowcy zdradza niezadowolenie z twoich warunkow'))
p('BFFIpsRuseOpenNiceAlmost',('$HeOrShe patrzy na ciebie przychylniej','Rozmowca patrzy na ciebie przychylniej'))
p('BFFIpsRuseNiceB',('$HeOrShe kiwa glowa','Rozmowca kiwa glowa'))
p('BFFIpsRuseNiceC',('wzdycha $heOrShe','wzdycha rozmowca'))
p('BFFIpsRuseNiceE',('$HeOrShe kreci $hisOrHer glowa','Rozmowca kreci glowa'))
p('BFFIpsRuseOpenMeanAlmost',('W oczach $HisOrHer pojawiaja sie lzy, a rece $hisOrHer nerwowo sie splataja. Jeszcze jeden argument powinien przekonac $himOrHer...', 'W oczach rozmowcy pojawiaja sie lzy, a dlonie nerwowo sie splataja. Jeszcze jeden argument powinien przelamac opor...'))
p('BFFIpsRuseMeanC',('mowi z zalem $heOrShe','mowi z zalem rozmowca'))
p('buyHTDataConfirmSelSpacer',('mowi $heOrShe, kiwajac glowa','mowi rozmowca, kiwajac glowa'),('dodaje $heOrShe z mrugnieciem','dodaje rozmowca z mrugnieciem'))
p('buyHTDataConfirmSelAristo',('mowi $heOrShe i uruchamia','mowi rozmowca i uruchamia'))
p('buyHTDataNeverMindSel',('$HeOrShe spokojnie przyjmuje','Rozmowca spokojnie przyjmuje'))
p('buyHTDataNeverMindSelSpacer',('mowi zyczliwie $heOrShe','mowi zyczliwie rozmowca'))
p('buyHTDataNeverMindSelFaithful',('mowi zyczliwie $heOrShe','mowi zyczliwie rozmowca'))
p('buyHTDataNeverMindSelVillain',('mowi $heOrShe','mowi rozmowca'))
p('buyHTDataNeverMindSelBusiness',('mowi $heOrShe','mowi rozmowca'))

# Tri-Tachyon loan and Galatia mission exchanges.
p('ttli_greetingSoonMajor',('jakby $heOrShe oczekiwal tej rozmowy','jakby ta rozmowa byla od dawna zaplanowana'))
p('ttli_greetingLaterMajor',('$HeOrShe zamierza cos powiedziec','Wydaje sie, ze chce cos powiedziec'))
p('ttli_payLoanResp',('mowi $heOrShe z szerokim usmiechem','mowi inwestor z szerokim usmiechem'))
p('ttli_payLoanRespMajor',('mowi $heOrShe','mowi inwestor'))
p('ttli_notPayingTextMajor',('$HeOrShe lekko przechyla $hisOrHer glowe, a na $hisOrHer czole pojawia sie zmarszczka','Inwestor lekko przechyla glowe, a na czole pojawia sie zmarszczka'),('mowi $heOrShe','mowi inwestor'))
p('gaFCFikenhildBotherVIPoptCsel',('$HeOrShe przytakuje, a na twarz $hisOrHer wraca znajomy wyraz urzedniczego zniecierpliwienia','Urzednik przytakuje, a na twarzy ponownie pojawia sie znajomy wyraz zniecierpliwienia'))
p('gaFCFikenhildBotherPM4a',('mowi $heOrShe bez cienia sarkazmu','mowi urzednik bez cienia sarkazmu'),('ze moglem pomoc','ze udalo sie pomoc'))
p('gaFCFikenhildBotherQM4a',('$HeOrShe wzrusza ramionami','Kwatermistrz wzrusza ramionami'))
p('gaFCFikenhildBotherQM4b',('$HeOrShe wzrusza ramionami','Kwatermistrz wzrusza ramionami'))
p('gaFCIsirahMercRespondThreats',('najemnik przekrzywia $hisOrHer glowe','najemnik przekrzywia glowe'))
p('gaFCKapteynAdminGreetAgain',('Bos piratow wyglada na zirytowanego, gdy tylko $heOrShe pojawia sie na ekranie.', 'Bos piratow sprawia wrazenie rozgniewanego od pierwszej chwili rozmowy.'))
p('gaFCLaicailleQuartermasterBother4',('odpowiada stanowczo $HeOrShe, po czym wylacza $hisOrHer strone polaczenia','odpowiada stanowczo kwatermistrz i rozlacza sie'))
p('gaFCarchonAskDemOptsCsel',('odpowiada ostroznie $heOrShe','odpowiada ostroznie archont'))
p('gaFCarchBack',('$HeOrShe wyglada na zdezorientowanego','Na twarzy archonta widac dezorientacje'))
p('gaFCarchPLexcuseAgain',('mowi $heOrShe','mowi archont'))
p('gaFCArchonSearchRestEasy',('mowi ostro $heOrShe','mowi ostro archont'),('ze moglem pomoc','ze udalo sie pomoc'))
p('gaFCLaicaileVisitStartAlamangYes',('$HeOrShe unosi brew','Archont unosi brew'))

PRONOUN=re.compile(rb'\$(?:[A-Za-z_]*)(?:[Hh]eOrShe|[Hh]imOrHer|[Hh]isOrHer|[Mm]anOrWoman|[Hh]imOrHerself)\b')

def sha(blob):return hashlib.sha256(blob).hexdigest()

def patch_bytes(blob,expected_sha=OLD_SHA):
    if sha(blob)!=expected_sha:raise ValueError('Input rules.csv SHA mismatch')
    if not blob.isascii():raise ValueError('Nonascii data')
    spans=rows_with_spans(blob)
    assert spans[0][2]==['id','trigger','conditions','script','text','options','notes']
    changes=[];hits={};before=after=replace_count=0
    for start,end,row in spans[1:]:
        key=row[0]
        if key not in PATCHES:continue
        if key in hits:raise ValueError(('Duplicate ID',key))
        hits[key]=True
        if len(row)!=7:raise ValueError(('Malformed row',key))
        before+=len(PRONOUN.findall((row[4]+' '+row[5]).encode('ascii')))
        block=blob[start:end]
        for a,b in PATCHES[key]:
            aa,bb=a.encode('ascii'),b.encode('ascii')
            if block.count(aa)!=1:raise ValueError(('Missing or repeated literal',key,a,block.count(aa)))
            block=block.replace(aa,bb,1)
            replace_count+=1
        parsed=list(csv.reader(block.decode('ascii').splitlines(keepends=True)))
        if len(parsed)!=1 or len(parsed[0])!=7:raise ValueError(('Invalid resultant record',key))
        if parsed[0][:4]!=row[:4] or parsed[0][5:]!=row[5:]:raise ValueError(('Touched technical/non-text columns',key))
        remain=PRONOUN.findall(parsed[0][4].encode('ascii'))
        if remain:raise ValueError(('Unfixed gender placeholders in changed row',key,remain))
        after+=len(remain)
        changes.append((start,end,block))
    if hits.keys()!=PATCHES.keys():raise ValueError(('Missing IDs',set(PATCHES)-set(hits)))
    current=bytearray();last=0
    for a,b,c in changes:
        current.extend(blob[last:a]);current.extend(c);last=b
    current.extend(blob[last:])
    out=bytes(current)
    if not out.isascii() or b'\n' in out.replace(b'\r\n',b''):raise ValueError('Bad ASCII/CRLF')
    if len(rows_with_spans(out))!=len(spans):raise ValueError('CSV row count changed')
    return out,dict(changed_rows=len(changes),precise_replacements=replace_count,removed_pronoun_placeholders=before-after,remaining=after,sha256=sha(out))

def apply(root):
    file=root/'mod'/SOURCE
    p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf8'))
    if meta['version']!='1.0.38':raise ValueError('Wrong base version')
    blob,stats=patch_bytes(file.read_bytes())
    if stats['sha256']!=NEW_SHA:raise ValueError('Unexpected patch result SHA')
    file.write_bytes(blob)
    meta['version']='1.0.39';meta['description']=meta['description'].replace('1.0.38','1.0.39')
    p.write_text(json.dumps(meta,indent=2,ensure_ascii=True)+'\n','utf8')
    p=root/'mod/CZYTAJ.txt';v=p.read_text('utf8')
    if v.count('STARSECTOR PL ASCII 1.0.38')!=1:raise ValueError('Old README header absent')
    p.write_text(v.replace('STARSECTOR PL ASCII 1.0.38','STARSECTOR PL ASCII 1.0.39')+'\nKolejne dialogi patroli, Kosciola Ludda i Akademii zostaly uwolnione od angielskich zmiennych zaimkowych.\n','utf8')
    p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';v=p.read_text('utf8')
    if v.count('const edition = "1.0.38"')!=1:raise ValueError('Old installer version absent')
    p.write_text(v.replace('const edition = "1.0.38"','const edition = "1.0.39"'),'utf8')
    return stats

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);opts=a.parse_args()
    print(json.dumps(apply(opts.worktree),indent=2))
