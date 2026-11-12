#!/usr/bin/env python3
"""Strict 1.0.40 JVM constant-pool/12 gendered-calls review (not native gameplay)."""
from __future__ import annotations
import argparse,csv,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
from collections import Counter
from apply_1040 import B,NEW,CORRECT,STATUS,FIELDS,read
from verify_story_1033 import proof_class_files,class_entries,texts

ORIGINAL_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
EXPECTED_PATCH_SHA='5e76f0ba08927564b35ded6ffa5dfba7c32134df152394c7cca19f5e96bf3ef5'
BASE=B+'BaseGetCommodityBarEvent'
OTHER=B+'BaseBarEventWithPerson'
COUNTS={'CorruptPLClerkSuppliesBarEvent':1,'DeliveryBarEvent':3,'LuddicCraftBarEvent':2,'LuddicFarmerBarEvent':2,'ScientistAICoreBarEvent':1,'TriTachLoanBarEvent':2,'TriTachMajorLoanBarEvent':1}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_map(root):
 root=Path(root);trans=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 before=read(trans/'TLUMACZENIA_JAR_1038.csv');after=read(trans/'TLUMACZENIA_JAR_1040.csv')
 assert len(before)==5254 and len(after)==5257
 changes={(cl,en):(old,new) for cl,q in CORRECT.items() for en,(old,new) in q.items()}
 assert len(changes)==18
 seen=[]
 for a,b in zip(before,after):
  key=(a['source_class'],a['english_literal'])
  if key in changes:
   old,new=changes[key]
   assert (a['polish_ascii_draft'],b['polish_ascii_draft'])==(old,new),(key,a,b)
   assert a['status']==b['status'] and a['status']
   seen.append(key)
  else:assert a==b,('unapproved edit',key)
 assert set(seen)==set(changes)
 add={(cl,en):pl for cl,q in NEW.items() for en,pl in q.items()}
 assert len(add)==3
 for r in after[len(before):]:
  key=(r['source_class'],r['english_literal'])
  assert key in add and r['polish_ascii_draft']==add[key] and r['status']==STATUS
 assert len({(r['source_class'],r['english_literal']) for r in after})==5257
 assert all(r['polish_ascii_draft'].isascii() for r in after)
 assert not any(r['source_class']==BASE and r['english_literal'] in ('her','him','his','himself','herself') for r in after)
 assert not any(r['source_class']==OTHER and r['english_literal'] in ('her','him','his','man','woman') for r in after)
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go';v=api.read_text('utf8')
 assert 'const version = "1040"' in v and '"1037", "1038", version}' in v
 assert 'const edition = "1.0.40"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.40' and meta['gameVersion']=='0.98a-RC8'
 assert len(meta['replace'])==41
 data=list((root/'mod/data').rglob('*'));files=[p for p in data if p.is_file()]
 assert len(files)==870 and all(p.read_bytes().isascii() for p in files)
 return {'api_map_rows':len(after),'new_api':3,'corrected_api':18,'data_files':870}

def composed(root):
 path=Path(root)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1040.csv'
 mapping={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in read(path)}
 def t(cls,en):return mapping.get((B+cls,en),en)
 tests=[]
 for gender,name in [('male','mezczyzna'),('female','kobieta')]:
  patterns={
   'CorruptPLClerkSuppliesBarEvent':[
     t('CorruptPLClerkSuppliesBarEvent','A ')+name+t('CorruptPLClerkSuppliesBarEvent',' in the port authority uniform is discreetely trying to catch your eye.')],
   'DeliveryBarEvent':[
    t('DeliveryBarEvent','At a corner table, a concerned-looking ')+name+t('DeliveryBarEvent',' glumly examines '),
    t('DeliveryBarEvent','At a corner table, a concerned-looking ')+name+t('DeliveryBarEvent',' in'),
    t('DeliveryBarEvent','Nod to the concerned ')+name],
   'LuddicCraftBarEvent':[
    t('LuddicCraftBarEvent','A tough looking ')+name+t('LuddicCraftBarEvent',' whose worn but well-tailored work suit bears the ')+t('LuddicCraftBarEvent','sigil of a crafts guild sits at a corner table bearing the remnants of a spare meal.'),
    t('LuddicCraftBarEvent','Strike up a conversation with the tough-looking ')+name],
   'LuddicFarmerBarEvent':[
    t('LuddicFarmerBarEvent','A weathered-looking ')+name+t('LuddicFarmerBarEvent',' whose worn but well-tailored ')+t('LuddicFarmerBarEvent','work suit bears the sigil of a farming commune sits at a table drinking small-beer.'),
    t('LuddicFarmerBarEvent','Chat up the weathered-looking ')+name],
   'ScientistAICoreBarEvent':[
    t('ScientistAICoreBarEvent','A disheveled ')+name+t('ScientistAICoreBarEvent',' in academic uniform is bothering some of the ')],
   'TriTachLoanBarEvent':[
    t('TriTachLoanBarEvent','Introduce yourself to the Tri-Tachyon ')+name+t('TriTachLoanBarEvent',' and try to land some investment credits'),
    t('TriTachLoanBarEvent','The Tri-Tachyon ')+name+t('TriTachLoanBarEvent',"'s smile freezes in place as you launch into a sophisticated ")+'argumentacje na rzecz zmiany warunkow.'],
   'TriTachMajorLoanBarEvent':[
    t('TriTachMajorLoanBarEvent','As the negotiations conclude, the Tri-Tachyon ')+name+t('TriTachMajorLoanBarEvent',' leans back, rolling the stem of ')],
  }
  assert sum(map(len,patterns.values()))==12
  for cls,seq in patterns.items():
   assert len(seq)==COUNTS[cls]
   for i,phrase in enumerate(seq):
    assert phrase.isascii() and name in phrase and '  ' not in phrase,(gender,cls,i,phrase)
    assert not any(x in phrase for x in ('zatroskany kobieta','Twardo wygladajacy','Sterany zyciem','Rozczochrany kobieta','Przedstawiciel Tri-Tachyon kobieta',' i sprobowac zdobyc','Zagadaj do ')),(gender,cls,i,phrase)
    assert phrase.startswith(('Przy ', 'Porozmawiaj z ', 'W poblizu stoi ', 'W odpowiedzi ', 'Gdy negocjacje dobiegaja konca, ')),(gender,cls,i,phrase)
    tests.append((gender,cls,i,phrase))
 assert len(tests)==24
 return {'verified_getManOrWoman_callsites':12,'gendered_snippets':24,'classes':7,'examples':{'craft_female':next(x[3] for x in tests if x[0]=='female' and x[1]=='LuddicCraftBarEvent' and x[2]==0), 'loan_female':next(x[3] for x in tests if x[0]=='female' and x[1]=='TriTachLoanBarEvent' and x[2]==1)}}

def verify_jar(root,original,patched):
 assert sha(original)==ORIGINAL_SHA
 assert sha(patched)==EXPECTED_PATCH_SHA
 mapping={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in read(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1040.csv')}
 proof=proof_class_files(original,patched,mapping)
 assert proof['modified_classes']==938 and proof['mapped_string_constants']==5255 and proof['executables_untouched']
 with zipfile.ZipFile(original) as a,zipfile.ZipFile(patched) as b:
  for cl,entries in NEW.items():
   p=cl.replace('.','/')+'.class';prev=texts(class_entries(a.read(p))[0]);nxt=texts(class_entries(b.read(p))[0]);
   for en,pl in entries.items(): assert en in prev and pl in nxt,(cl,en,pl)
  for cl,entries in CORRECT.items():
   p=cl.replace('.','/')+'.class';prev=texts(class_entries(a.read(p))[0]);nxt=texts(class_entries(b.read(p))[0]);
   for en,(was,now) in entries.items():assert en in prev and now in nxt and was not in nxt,(cl,en,now)
  for cls in (BASE,OTHER):
   p=cls.replace('.','/')+'.class';orig=class_entries(a.read(p))[0];post=class_entries(b.read(p))[0]
   her_index=188 if cls==BASE else 143
   assert orig[her_index]==post[her_index],('Shared her constant changed',cls)
 counts={}
 for name,expected in COUNTS.items():
  cls=B+name
  for jar in (original,patched):
   output=subprocess.run(['javap','-c','-p','-classpath',str(jar),cls],capture_output=True,text=True,check=True).stdout
   hits=re.findall(r'^\s*\d+:\s+invokevirtual\s+#[0-9]+\s+// Method getManOrWoman:',output,re.M)
   assert len(hits)==expected,(name,len(hits),expected)
  counts[name]=expected
 assert sum(counts.values())==12
 return {'original_api_sha256':sha(original),'patched_api_sha256':sha(patched),**proof,'callsite_counts':counts,'shared_her_indexes_untouched':True}

def check(root,original_api=None,patched_api=None,prior_zip=None):
 root=Path(root);d={**validate_map(root),**composed(root)}
 if prior_zip:
  with zipfile.ZipFile(prior_zip) as z:
   old={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  cur={p.relative_to(root/'mod').as_posix():p.read_bytes() for p in (root/'mod/data').rglob('*') if p.is_file()}
  assert len(old)==len(cur)==870 and old==cur
  d['data_unchanged_vs_1039']=870
 if original_api or patched_api:
  assert original_api and patched_api
  d['jar_proof']=verify_jar(root,original_api,patched_api)
 return d

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);a.add_argument('--original-api',type=Path);a.add_argument('--patched-api',type=Path);a.add_argument('--previous-zip',type=Path)
 x=a.parse_args();print(json.dumps(check(x.worktree,x.original_api,x.patched_api,x.previous_zip),indent=2))
