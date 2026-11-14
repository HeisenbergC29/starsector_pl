#!/usr/bin/env python3
"""Reproducible 35-row historical API review, append-only to all 447 prior reviews."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1063 import CLASS,OLD,NEW,REPAIRS,DRAFT,build,fp,sha
from apply_1054 import readmap
PREVIOUS=447;TOTAL=3658

def inventory(worktree:Path)->dict:
 base=Path(worktree)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(base/OLD);new=readmap(base/NEW)
 expected,stats=build(old)
 if new!=expected:raise ValueError('Unapproved v1.0.63 map for review')
 bykey={(x['source_class'],x['english_literal']):x for x in old}
 approved=[]
 for r in new:
  if r['source_class']!=CLASS:continue
  original=bykey[(r['source_class'],r['english_literal'])]
  if original['status'] not in DRAFT:continue
  approved.append({'source_class':CLASS,'english_literal':r['english_literal'],
   'english_key_sha256':sha(r['english_literal'].encode()),
   'old_status':original['status'],'old_draft':original['polish_ascii_draft'],
   'new_draft':r['polish_ascii_draft'],'old_row_sha256':fp(original),
   'row_sha256':fp(r),
   'evidence':'original_JVM_LuddicPathCellsIntel_ldc_1063',
   'review_status':'original_JVM_semantic_review_offline_pending_native_Windows'})
 if len(approved)!=35 or len({x['row_sha256'] for x in approved})!=35:
  raise ValueError('Wrong historical reviewed fingerprint count')
 return {'schema_version':1,'release':'1.0.63','source_class':CLASS,
   'game_version':'0.98a-RC8','previous_api_map_sha256':sha((base/OLD).read_bytes()),
   'new_api_map_sha256':sha((base/NEW).read_bytes()),
   'previous_historical_reviews':PREVIOUS,'new_historical_reviews':35,
   'historical_reviewed_total':482,'historical_remaining':TOTAL-482,
   'corrected_literals':REPAIRS,'technical_category_token_protected':'Colony threats',
   'historical_reviewed_rows':approved,'native_windows_gameplay_tested':False}

def cumulative(previous:dict,record:dict)->dict:
 old=previous.get('reviewed',[])
 if previous.get('installed_version')!='1.0.62' or len(old)!=PREVIOUS:
  raise ValueError('Wrong 447-row previous historical review ledger')
 past={(x['source_class'],x['row_sha256']) for x in old}
 if len(past)!=PREVIOUS or any(x['source_class']==CLASS for x in old):
  raise ValueError('Luddic Path historic review duplicated')
 additions=[{k:r[k] for k in ('source_class','row_sha256','english_key_sha256','evidence','review_status')} for r in record['historical_reviewed_rows']]
 if len(additions)!=35 or len({(x['source_class'],x['row_sha256']) for x in additions})!=35:
  raise ValueError('Duplicate new historical review')
 return {'schema_version':1,'installed_version':'1.0.63',
  'previous_ledger':'docs/API_SEMANTIC_REVIEW_1062.json',
  'review_protocol':'447 old SHA-pinned reviews immutable; 35 new class-scoped draft API text reviews verified by original LuddicPathCellsIntel JVM constant pool and ldc sites, 14 corrected literals including protected Set.add category; no Windows gameplay.',
  'new_historical_reviews':35,'reviewed':old+additions}

def check(root:Path,record:Path,previous:Path|None=None,ledger:Path|None=None)->dict:
 expected=inventory(root)
 if json.loads(Path(record).read_text('utf8'))!=expected:raise ValueError('Manual review registry altered')
 if previous is not None and ledger is not None:
  prev=json.loads(Path(previous).read_text('utf8'))
  if json.loads(Path(ledger).read_text('utf8'))!=cumulative(prev,expected):
   raise ValueError('Not an append-only 482-row historical API ledger')
 return {'release':'1.0.63','new_historical_reviews':35,'historical_reviewed_total':482,
  'remaining_unreviewed_historical':3176,'previous_447_preserved':previous is not None,
  'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--record',required=True,type=Path);p.add_argument('--previous',type=Path)
 p.add_argument('--ledger',type=Path);p.add_argument('--generate',action='store_true')
 a=p.parse_args()
 if a.generate:
  review=inventory(a.worktree)
  a.record.write_text(json.dumps(review,ensure_ascii=True,indent=2)+'\n','utf8')
  if a.previous and a.ledger:
   a.ledger.write_text(json.dumps(cumulative(json.loads(a.previous.read_text('utf8')),review),ensure_ascii=True,indent=2)+'\n','utf8')
 print(json.dumps(check(a.worktree,a.record,a.previous,a.ledger),indent=2))
