#!/usr/bin/env python3
"""Regression: 1.0.30 full assembled Polish UI and bounded 1.0.29 map delta."""
from __future__ import annotations
import argparse,csv,json,zipfile
from pathlib import Path
from apply_1030 import OBF,API,CORRECTION,STATUS,PREV_OBF_SHA,NEW_OBF_SHA,FIELDS

def csvrows(p):
 with p.open('r',encoding='utf8',newline='') as f:
  c=csv.DictReader(f);assert c.fieldnames==FIELDS
  return list(c)

def check(root,previous=None):
 o=root/'buildtools/NARZEDZIA_OBF';a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old_o=csvrows(o/'TLUMACZENIA_OBF_10129.csv');new_o=csvrows(o/'TLUMACZENIA_OBF_10130.csv')
 old_a=csvrows(a/'translations/TLUMACZENIA_JAR_1029.csv');new_a=csvrows(a/'translations/TLUMACZENIA_JAR_1030.csv')
 eo=[dict(source_class=c,english_literal=e,polish_ascii_draft=v,status=STATUS) for c,parts in OBF.items() for e,v in parts.items()]
 ea=[dict(source_class=c,english_literal=e,polish_ascii_draft=v,status=STATUS) for c,parts in API.items() for e,v in parts.items()]
 assert len(old_o)==3508 and len(old_a)==5215
 assert len(eo)==2 and len(ea)==4 and new_o==old_o+eo
 edited=[(i,(old,new)) for i,(old,new) in enumerate(zip(old_a,new_a)) if old!=new]
 assert len(edited)==1,(edited[:3],len(edited))
 i,(original,fix)=edited[0]
 assert original['source_class']==CORRECTION['source_class'] and original['english_literal']==CORRECTION['english_literal']
 assert original['polish_ascii_draft']==CORRECTION['from_polish']
 assert fix==dict(source_class=CORRECTION['source_class'],english_literal=CORRECTION['english_literal'],polish_ascii_draft=CORRECTION['to_polish'],status=STATUS)
 assert new_a[len(old_a):]==ea
 assert len(set((r['source_class'],r['english_literal']) for r in new_o))==len(new_o)
 assert len(set((r['source_class'],r['english_literal']) for r in new_a))==len(new_a)
 assert len(new_o)==3510 and len(new_a)==5219
 # Assembled bounty text in the actual order: personal pronoun + phrase + location.
 cl='com.fs.starfarer.api.impl.campaign.intel.PersonBountyIntel'
 mapped={r['english_literal']:r['polish_ascii_draft'] for r in new_a if r['source_class']==cl}
 for gender in ['He is','She is']:
  for location in ['hiding out near','hiding out in','located in']:
   sentence=mapped[gender]+mapped[' rumored to be ']+mapped[location]+' Eos.'
   assert sentence[0].isupper() and '  ' not in sentence and 'He' not in sentence and 'She' not in sentence
   assert 'podobno' in sentence and 'przebywa ukrywa' not in sentence
   assert sentence.startswith(('On podobno ','Ona podobno ')),sentence
 assert 'On podobno ukrywa sie w poblizu Eos.' == mapped['He is']+mapped[' rumored to be ']+mapped['hiding out near']+' Eos.'
 # Duration is a whole UI sentence, with Polish abbreviation of 'sekundy'.
 im={r['english_literal']:r['polish_ascii_draft'] for r in new_a if r['source_class']=='com.fs.starfarer.api.impl.campaign.abilities.InterdictionPulseAbility'}
 for n in (1,2,5,100):
  assert im['Interdict! (']+str(n)+im['s)']==f'Zaklocenie! ({n} s)'
 assert len({(r['source_class'],r['english_literal']) for r in new_a})==len(new_a)
 obf_src=(o/'main.go').read_text('utf8');api_src=(a/'main.go').read_text('utf8')
 for frag in ['patched 10130','TLUMACZENIA_OBF_10130.csv',f'"{PREV_OBF_SHA}": "10129"']:
  assert frag in obf_src,frag
 for frag in ['const version = "1030"','const exeVersion = "1.0.30"',f'const expectedOBFPatched10130 = "{NEW_OBF_SHA}"']:
  assert frag in api_src,frag
 assert 'const edition = "1.0.30"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
 mod=root/'mod';info=json.loads((mod/'mod_info.json').read_text('utf8'))
 assert info['version']=='1.0.30' and info['gameVersion']=='0.98a-RC8'
 data={p.relative_to(mod).as_posix():p.read_bytes() for p in (mod/'data').rglob('*') if p.is_file()}
 assert len(data)==870 and all(v.isascii() for v in data.values())
 if previous:
  with zipfile.ZipFile(previous) as z:
   expected={n.removeprefix('Starsector_PL_ASCII/'):z.read(n) for n in z.namelist() if n.startswith('Starsector_PL_ASCII/data/')}
  assert data==expected,'game data unexpectedly changed'
 return dict(OBF_new_rows=len(eo),API_new_rows=len(ea),API_existing_corrected=len(edited),bounty_variants_tested=6,interdiction_variants_tested=4,data_unchanged=870)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous-zip',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.previous_zip),indent=2))
