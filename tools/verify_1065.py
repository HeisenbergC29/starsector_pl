#!/usr/bin/env python3
"""Fail-closed regression of the 1.0.65 MarketCMD grammar / original-JVM audit."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1054 import readmap,encode,once
from apply_1065 import CLASS,OLD,NEW,REPAIRS,BASE_SHA,RELEASE_SUFFIX,sha,build
from build_review_1065 import check as review_check
MAP_SHA='4d83faa23a64a85a094c325d6f7f53e7d8944da7919eb497eb20be480aba2163'
PRIOR_GO_SHA='255eac1601f041ad3f5858f25c952c38b6b7218b3e57c8cc58799a03b01e8c86'
NEW_GO_SHA='fff448cb53c8638e1d5f417e1efd1ac09d74466ee546ecb85d92c726aabf2e25'
REVIEW_SHA='51c30b70de72543e032647d8e75aeab08fe9e1945d37a6096f74e7136efc6b72'
JVM_SHA='de369a75836864dc62248a9b71a3b069a9c0c7eb76b9467afbd2cbad47985b99'
DATA_SHA='feb6e159ae8d6aa6622b3dd5e8414b425082b930ee6c739baddb0091127fb370'
RULES_SHA='4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04'

NAMES=['Jangala','Chicomoztoc','Asharu','Nova Maxios','Sindria']
INDUSTRIES=['Rafineria','Stocznia orbitalna','Obrona naziemna','Rolnictwo','Przemysl ciezki']
FACTIONS=['Hegemonia','Liga Perseanska','Tri-Tachyon','Kosciol Ludda','Diktat Sindria']
NUMBERS=[1,2,5,12,21]

def render(m:dict)->dict:
 for k in REPAIRS:
  if m[k]!=REPAIRS[k]:raise ValueError(('Approved translation differs',k))
 texts=[]
 def add(group,actual,expected):
  if actual!=expected or not actual.isascii() or '  ' in actual or '\n' in actual or '%s' in actual:
   raise ValueError(('Broken composed MarketCMD UI message',group,actual,expected))
  texts.append({'kind':group,'text':actual})
 for name,industry,faction,num in zip(NAMES,INDUSTRIES,FACTIONS,NUMBERS):
  n=str(num)
  add('raid_duration',m['Your ground forces commander estimates that given the relative force strengths,  the raid should disrupt all ']+industry+m[' operations for at least %s days.'].replace('%s',n),
   f'Dowodca sil naziemnych ocenia, ze rajd powinien zaklocic dzialanie obiektu: {industry} przez co najmniej {n} dn.')
  add('previously_disrupted',industry+m[' operations are already disrupted, and a raid will have ']+m['reduced effect.'],
   f'{industry} - dzialanie obiektu jest juz zaklocone, wiec skutecznosc rajdu bedzie mniejsza.')
  add('orbital_superiority','Stacja orbitalna'+m[' dominates the orbit and prevents any ']+m['hostile action, aside from a quick raid, unless it is dealt with.'],
   'Stacja orbitalna kontroluje orbite i blokuje wrogie dzialania poza szybkim rajdem, dopoki zagrozenie nie zostanie usuniete.')
  add('aid_option',m['Aid the ']+name+m[' and its defenders'],f'Wesprzyj: {name} (wraz z obroncami)')
  add('attack_option',m['Engage the ']+name+m[' and its defenders'],f'Zaatakuj: {name} (wraz z obroncami)')
  add('raid_minimum',m['Requires at least ']+n+m[' raid effectiveness.'],f'Minimalna wymagana skutecznosc rajdu: {n}.')
  add('colony_stability',m['Stability of ']+name,f'Stabilnosc kolonii: {name}')
  add('orbital_bombardment',m['Consider an orbital bombardment of ']+name,f'Rozwaz bombardowanie orbitalne. Cel: {name}')
  add('start_raid',m['Launch a raid against ']+name,f'Rozpocznij rajd. Cel: {name}')
  add('secret_raid',m['Secretly raided ']+name,f'Przeprowadzono tajny rajd. Cel: {name}')
  add('reputation',m['Suffer no penalty to your standing with ']+faction,f'Bez pogorszenia relacji. Frakcja: {faction}')
 if len(texts)!=55 or len({t['kind'] for t in texts})!=11:
  raise ValueError(('Incomplete grammar simulation',len(texts)))
 return {'rendered_combinations':len(texts),'message_kinds':11,
  'names_tested':len(NAMES),'industry_names_tested':len(INDUSTRIES),
  'faction_names_tested':len(FACTIONS),'quantities_tested':len(NUMBERS)}

def check(root:Path,repo:Path|None=None)->dict:
 root=Path(root);repo=Path(repo) if repo else Path(__file__).resolve().parent.parent
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';tr=api/'translations'
 prior=(tr/OLD).read_bytes();new=(tr/NEW).read_bytes()
 if (sha(prior),sha(new))!=(BASE_SHA,MAP_SHA):raise ValueError('Unexpected API map hash')
 before=readmap(tr/OLD);actual=readmap(tr/NEW);predicted,meta=build(before)
 if predicted!=actual or encode(predicted)!=new:
  raise ValueError('Unapproved map modification')
 if len(actual)!=5314 or len(meta['reviews'])!=104 or len(meta['repaired'])!=17:
  raise ValueError('Wrong API review/correction counts')
 m={r['english_literal']:r['polish_ascii_draft'] for r in actual if r['source_class']==CLASS}
 if len(m)!=111:raise ValueError('Missing MarketCMD mapping')
 sim=render(m)
 code=(api/'main.go').read_text('utf8');got=sha(code.encode())
 if got!=NEW_GO_SHA:raise ValueError(('Unexpected patcher executable code',got))
 for old,nxt in reversed([('const version = "1064"','const version = "1065"'),
  ('const exeVersion = "1.0.64"','const exeVersion = "1.0.65"'),
  ('"1063", version}','"1063", "1064", version}'),
  ('PL ASCII patch up to 1.0.64','PL ASCII patch up to 1.0.65')]):code=once(code,nxt,old)
 if sha(code.encode())!=PRIOR_GO_SHA:raise ValueError('Unapproved Go executable logic rewrite')
 if 'const edition = "1.0.65"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Installer edition stale')
 mod=root/'mod';info=json.loads((mod/'mod_info.json').read_text('utf8'))
 if (info.get('version'),info.get('gameVersion'),len(info.get('replace',[])))!=('1.0.65','0.98a-RC8',41):
  raise ValueError('Wrong mod/game metadata')
 guide=(mod/'CZYTAJ.txt').read_text('utf8')
 if not guide.startswith('STARSECTOR PL ASCII 1.0.65') or not guide.endswith(RELEASE_SUFFIX):
  raise ValueError('Player instructions inconsistent')
 files=sorted(x for x in (mod/'data').rglob('*') if x.is_file())
 digest=sha('\n'.join(f'{x.relative_to(mod/"data").as_posix()}:{sha(x.read_bytes())}' for x in files).encode())
 if len(files)!=870 or digest!=DATA_SHA or sha((mod/'data/campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError(('Data files or dialogue IDs changed',len(files),digest))
 reg=repo/'docs/MARKETCMD_REVIEW_1065.json';evidence=repo/'docs/JVM_AUDIT_1065.json'
 if sha(reg.read_bytes())!=REVIEW_SHA or sha(evidence.read_bytes())!=JVM_SHA:
  raise ValueError('Manual review or original-JVM evidence SHA mismatch')
 review_check(root,reg)
 ev=json.loads(evidence.read_text('utf8'))
 if (ev['jvm_ldc_uses'],ev['unique_jvm_literal_texts'],ev['mapped_source_literals'],ev['historical_draft_reviews'],ev['repaired_fragments'])!=(363,240,111,104,17):
  raise ValueError('Original JVM audit incomplete or inflated')
 if len(ev['mapped_literal_evidence'])!=111 or any(not x['uses'] or x['english_literal'] not in m for x in ev['mapped_literal_evidence']):
  raise ValueError('Original JVM mapping/callsite missing')
 return {'release':'1.0.65','historical_api_reviewed_new':87,'historical_api_rechecked_prior':17,
  'historical_api_reviewed_total':617,'historical_api_unreviewed':3041,
  'original_jvm_ldc_uses':363,'mapped_literals':111,
  'repaired_literals':17,'unchanged_game_data_files':870,
  'native_gameplay_test_policy':'after_1_1_release',**sim}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--repo',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.repo),indent=2))
