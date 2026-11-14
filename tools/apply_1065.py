#!/usr/bin/env python3
"""1.0.65: context-reviewed MarketCMD colony raid/bombardment UI strings.

Safe in the original JVM because all 111 mapped literals are verified actual
ldc/ldc_w strings, not a code/name/technical identifier rewrite.  Preserve all
5314 map keys and all mod/data bytes, and use grammatical templates with a
separate colon when inserted player-facing names cannot be declined.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once
CLASS='com.fs.starfarer.api.impl.campaign.rulecmd.salvage.MarketCMD'
OLD='TLUMACZENIA_JAR_1064.csv';NEW='TLUMACZENIA_JAR_1065.csv'
BASE_SHA='080333ba3c5d89f79a27e83737be8eb940c21a10446901ae01de98ef735a7588'
DRAFT={'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
STATUS='REVIEWED_ORIGINAL_JVM_MARKETCMD_1065_POST_1_1_GAME_TESTS'
# Original fragments are paired with the surrounding StringBuilder instructions.
REPAIRS={
 'Fleet capability for ground support':'Mozliwosci floty w zakresie wsparcia naziemnego',
 'Your ground forces commander estimates that given the relative force strengths,  the raid should disrupt all ':'Dowodca sil naziemnych ocenia, ze rajd powinien zaklocic dzialanie obiektu: ',
 ' operations for at least %s days.':' przez co najmniej %s dn.',
 ' operations are already disrupted, and a raid will have ':' - dzialanie obiektu jest juz zaklocone, wiec skutecznosc rajdu bedzie ',
 'reduced effect.':'mniejsza.',
 ' dominates the orbit and prevents any ':' kontroluje orbite i blokuje ',
 'hostile action, aside from a quick raid, unless it is dealt with.':'wrogie dzialania poza szybkim rajdem, dopoki zagrozenie nie zostanie usuniete.',
 'Aid the ':'Wesprzyj: ',
 'Engage the ':'Zaatakuj: ',
 ' and its defenders':' (wraz z obroncami)',
 'Requires at least ':'Minimalna wymagana skutecznosc rajdu: ',
 ' raid effectiveness.':'.',
 'Stability of ':'Stabilnosc kolonii: ',
 'Consider an orbital bombardment of ':'Rozwaz bombardowanie orbitalne. Cel: ',
 'Launch a raid against ':'Rozpocznij rajd. Cel: ',
 'Secretly raided ':'Przeprowadzono tajny rajd. Cel: ',
 'Suffer no penalty to your standing with ':'Bez pogorszenia relacji. Frakcja: ',
}
RELEASE_SUFFIX=(
 '\nPrzeglad rajdow, bombardowan i obrony kolonii: 104 historyczne teksty Java API '
 'w MarketCMD sprawdzono w oryginalnym JVM (87 nowych i 17 ponownie zweryfikowanych); '
 'poprawiono 17 fragmentow. Nazwy dynamiczne oddzielono dwukropkiem zamiast '
 'wymagac odmiany. Testy w uruchomionej grze beda wykonane dopiero po wersji 1.1.\n')

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def fp(r:dict)->str:return sha('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode())

def build(rows:list[dict])->tuple[list[dict],dict]:
 if len(rows)!=5314 or len({(r['source_class'],r['english_literal']) for r in rows})!=5314:
  raise ValueError('Wrong 1.0.64 API map cardinality')
 if sha(encode(rows))!=BASE_SHA:raise ValueError('Source map not byte identical to 1.0.64')
 selected=[r for r in rows if r['source_class']==CLASS]
 if len(selected)!=111 or sum(x['status'] in DRAFT for x in selected)!=104:
  raise ValueError('Expected exactly 111 MarketCMD map entries with 104 unreviewed')
 found={(x['source_class'],x['english_literal']):x for x in rows}
 if len(REPAIRS)!=17 or any((CLASS,k) not in found for k in REPAIRS):
  raise ValueError('Missing original JVM correction input')
 for key in REPAIRS:
  r=found[(CLASS,key)]
  if key=='Aid the ':
   if (r['status'],r['polish_ascii_draft'])!=('VERIFIED_ORIGINAL_LITERAL_1008','Pomoc dla '):
    raise ValueError('Unexpected previously reviewed Aid the original')
  elif r['status'] not in DRAFT:
   raise ValueError(('Unexpected correction selection',key,r['status']))
 out=[];reviews=[];changes=[]
 for src in rows:
  r=dict(src);key=src['english_literal']
  if src['source_class']==CLASS and key in REPAIRS:
   value=REPAIRS[key]
   if not value.isascii() or value==src['polish_ascii_draft']:
    raise ValueError(('Invalid new ASCII translation',key))
   for marker in ('%s','%d','%f','\r','\n','\t'):
    if src['polish_ascii_draft'].count(marker)!=value.count(marker):
     raise ValueError(('Technical placeholder changed',key,marker))
   r['polish_ascii_draft']=value;changes.append(key)
  if src['source_class']==CLASS and src['status'] in DRAFT:
   r['status']=STATUS
   reviews.append({'source_class':CLASS,'english_literal':key,'english_key_sha256':sha(key.encode()),
    'old_status':src['status'],'old_draft':src['polish_ascii_draft'],
    'new_draft':r['polish_ascii_draft'],'old_row_sha256':fp(src),'row_sha256':fp(r),
    'evidence':'original_JVM_MarketCMD_1065',
    'review_status':'reviewed_original_JVM_offline_game_tests_after_1_1'})
  out.append(r)
 if len(reviews)!=104 or len(changes)!=17 or set(changes)!=set(REPAIRS):
  raise ValueError('Incomplete approved review/delta')
 return out,{'reviews':reviews,'repaired':changes}

def apply(root:Path)->dict:
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';trans=api/'translations'
 old=trans/OLD;dest=trans/NEW
 if dest.exists() or sha(old.read_bytes())!=BASE_SHA:raise ValueError('Wrong baseline or already installed')
 rows=readmap(old)
 if encode(rows)!=old.read_bytes():raise ValueError('Unexpected map serialization')
 out,meta=build(rows);payload=encode(out)
 main=api/'main.go';source=main.read_text('utf8')
 for before,after in [
  ('const version = "1064"','const version = "1065"'),
  ('const exeVersion = "1.0.64"','const exeVersion = "1.0.65"'),
  ('"1063", version}','"1063", "1064", version}'),
  ('PL ASCII patch up to 1.0.64','PL ASCII patch up to 1.0.65')]:source=once(source,before,after)
 installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 ins=once(installer.read_text('utf8'),'const edition = "1.0.64"','const edition = "1.0.65"')
 info=root/'mod/mod_info.json';mod=json.loads(info.read_text('utf8'))
 if (mod.get('version'),mod.get('gameVersion'))!=('1.0.64','0.98a-RC8'):
  raise ValueError('Unexpected mod/game version')
 mod['version']='1.0.65';mod['description']=once(mod['description'],'1.0.64','1.0.65')
 guide=root/'mod/CZYTAJ.txt';txt=once(guide.read_text('utf8'),'STARSECTOR PL ASCII 1.0.64','STARSECTOR PL ASCII 1.0.65')+RELEASE_SUFFIX
 dest.write_bytes(payload);main.write_text(source,encoding='utf8');installer.write_text(ins,encoding='utf8')
 info.write_text(json.dumps(mod,ensure_ascii=True,indent=2)+'\n',encoding='utf8');guide.write_text(txt,encoding='utf8')
 return {'release':'1.0.65','previous_historical_reviews':530,'new_historical_reviews':87,'prior_historical_reviews_revisited':17,
   'historical_reviewed_total':617,'historical_unreviewed':3041,'repaired_fragments':17,
   'api_map_rows':len(out),'api_map_sha256':sha(payload),'changed_data_files':0,
   'new_executable_jvm_instructions':0,'native_gameplay_test_deferred_until_after_1_1':True}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(apply(p.parse_args().worktree),indent=2))
