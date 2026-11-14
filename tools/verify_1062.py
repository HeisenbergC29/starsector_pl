#!/usr/bin/env python3
"""Verify strict 1.0.62 PirateBaseIntel translation-only patch and game-data invariants."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1054 import readmap,encode,once
from apply_1062 import CLASS,OLD,NEW,BASE_SHA,REPAIRS,ADDITIONS,STATUS,RELEASE_SUFFIX,build,sha
from build_review_1062 import check as check_review
NEW_MAP_SHA='1f85680ff856b858f2f4db342aa98754c085a35bec6e9d0538113a55f9471f01'
OLD_GO_SHA='357f50ff0a085f5902b8a06ddb6948f1c512efa4115ac492579fe600a5ee505d'
NEW_GO_SHA='8e91220d9fd52d6c6b1a27d278706dcb911f1b589837ac62a89d843e7c8e3dd0'
DATA_SHA='feb6e159ae8d6aa6622b3dd5e8414b425082b930ee6c739baddb0091127fb370'
RULES_SHA='4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04'
REVIEW_SHA='ebb3b72ebe59b7c67daaa21d1cb7b0429587957f7260bc9bfc9c03cdc1d517a4'
JVM_SHA='628da2f27c9aca56fdc7abbea8ed52aa9d1c76ab7b779a1bef4a5d23655fe364'

def render(map_:dict[str,str])->dict:
 p=lambda s:map_[s]
 if (p('Fleet log'),p('Colony threats'))!=('Fleet log','Colony threats'):
  raise ValueError('Technical intel tags must remain original Java keys')
 if (p('Agreement'),p('agreement'))!=('Porozumienie','porozumienie'):
  raise ValueError('Missing original JVM agreement text/highlights')
 if not p('Agreement made with base commander').startswith(p('Agreement')+' '):
  raise ValueError('UI highlighted word does not occur in translated message')
 if p('Agreement made with base commander').count(p('Agreement'))!=1:
  raise ValueError('Highlight must be unique')
 if p('Agreement broken')!='Zerwano porozumienie' or p('Agreement dissolved')!='Rozwiazano porozumienie':
  raise ValueError('Wrong event titles')
 # Original compiled tooltip call passes 'agreement' as first of three
 # highlight parameters to the already-polish 'Masz %s ...' message.
 text=p('You have an %s with the base commander, and fleets from this base do not, as a rule, harass your colonies or shipping. The protection payment is %s of the gross income of all of your affected colonies, which amounts to %s per month at their current level of income.')
 variants=[]
 for credit in ['1 000','18 500','300 000']:
  for fraction in ['5%','20%','35%']:
   for agreement in ('agreement','Agreement'):
    # Two UI variants: lowercase for detail tooltip, uppercase for event.
    target=p('agreement') if agreement=='agreement' else p('Agreement')
    s=text % (target,fraction,credit)
    if agreement=='agreement' and (not s.startswith('Masz porozumienie z dowodca bazy') or 'Oplata za ochrone' not in s):
     raise ValueError(('Incorrect composed agreement tooltip',s))
    if any(token in s for token in ('agreement',' Agreement','Fleet log','Colony threats')):
     raise ValueError(('English missing translation survived in UI',s))
    if s.count(fraction)!=1 or s.count(credit)!=1:raise ValueError('Lost amount/percent parameter')
    variants.append(s)
 if len(variants)!=18:raise ValueError('Incomplete agreement UI variant set')
 return {'tooltip_variants':18,'category_tag_checks':3,'highlight_pairs_verified':2,
         'technical_fields_protected':True}

def check(root:Path,repo:Path|None=None)->dict:
 root=Path(root);repo=Path(repo) if repo else Path(__file__).resolve().parent.parent
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';t=api/'translations'
 before=(t/OLD).read_bytes();after=(t/NEW).read_bytes()
 if (sha(before),sha(after))!=(BASE_SHA,NEW_MAP_SHA):raise ValueError('Incorrect 1.0.61/1.0.62 map SHA')
 prev=readmap(t/OLD);actual=readmap(t/NEW);approved,stats=build(prev)
 if actual!=approved or encode(approved)!=after:raise ValueError('Unapproved map change')
 if (len(prev),len(actual),len(stats['reviews']),len(stats['corrected']))!=(5312,5314,31,5):
  raise ValueError('Wrong mapping cardinality')
 original={r['english_literal']:r for r in prev if r['source_class']==CLASS}
 m={r['english_literal']:r['polish_ascii_draft'] for r in actual if r['source_class']==CLASS}
 if len(m)!=38 or set(m)-set(original)!=set(ADDITIONS):raise ValueError('Nonapproved missing Java literal')
 output=render(m)
 code=(api/'main.go').read_text('utf8')
 if sha(code.encode())!=NEW_GO_SHA:raise ValueError('Unauthorized Go patcher source change')
 for a,b in reversed([('const version = "1061"','const version = "1062"'),
  ('const exeVersion = "1.0.61"','const exeVersion = "1.0.62"'),
  ('"1060", version}','"1060", "1061", version}'),
  ('PL ASCII patch up to 1.0.61','PL ASCII patch up to 1.0.62')]):code=once(code,b,a)
 if sha(code.encode())!=OLD_GO_SHA:raise ValueError('Non-version code changed')
 if 'const edition = "1.0.62"' not in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8'):
  raise ValueError('Wrong installer edition')
 mod=root/'mod';info=json.loads((mod/'mod_info.json').read_text('utf8'))
 if (info.get('version'),info.get('gameVersion'),len(info.get('replace',[])))!=('1.0.62','0.98a-RC8',41):
  raise ValueError('Wrong Starsector mod manifest')
 readme=(mod/'CZYTAJ.txt').read_text('utf8')
 if not readme.startswith('STARSECTOR PL ASCII 1.0.62') or not readme.endswith(RELEASE_SUFFIX):raise ValueError('Release guide missing')
 data=mod/'data';files=sorted(x for x in data.rglob('*') if x.is_file())
 actual_digest=sha('\n'.join(f'{x.relative_to(data).as_posix()}:{sha(x.read_bytes())}' for x in files).encode())
 if len(files)!=870 or actual_digest!=DATA_SHA or sha((data/'campaign/rules.csv').read_bytes())!=RULES_SHA:
  raise ValueError('Game data or dialogue changed')
 record=repo/'docs/PIRATE_BASE_REVIEW_1062.json';jvm=repo/'docs/JVM_AUDIT_1062.json'
 if sha(record.read_bytes())!=REVIEW_SHA or sha(jvm.read_bytes())!=JVM_SHA:raise ValueError('Original JVM or manual review evidence modified')
 check_review(root,record)
 evidence=json.loads(jvm.read_text('utf8'))
 if (evidence['confirmed_original_jvm_ldc_uses'],evidence['unique_confirmed_literals'])!=(42,38):
  raise ValueError('Original JVM evidence not complete')
 return {'release':'1.0.62','map_rows':5314,'old_map_rows':5312,
   'historical_newly_reviewed':31,'historical_reviewed_total':447,'remaining_historical_api':3211,
   'existing_literal_corrections':5,'new_literal_translations':2,
   'original_jvm_ldc_uses':42,'game_data_files_byte_identical':870,
   'rendered_tooltip_combinations':output['tooltip_variants'],
   'technical_category_tokens_restored':2,'mapping_sha256':NEW_MAP_SHA,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--repo',type=Path)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.repo),indent=2))
