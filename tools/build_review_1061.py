#!/usr/bin/env python3
"""Generate immutable 25-row review record and cumulative prior-hash-aware audit."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1054 import readmap
from apply_1061 import CLASS,NEW,OLD,DRAFT,REPAIRS,NEW_LITERALS,STATUS,build,sha,fp

HISTORICAL_PREVIOUS=391
HISTORICAL_NEW=25
HISTORICAL_TOTAL=3658

def inventory(root:Path)->dict:
 root=Path(root);t=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(t/OLD);current=readmap(t/NEW);expected,stats=build(old)
 if expected!=current:raise ValueError('Cannot audit a noncanonical 1.0.61 map')
 previous={r['english_literal']:r for r in old if r['source_class']==CLASS}
 rows=[]
 for r in current:
  if r['source_class']!=CLASS:continue
  src=previous.get(r['english_literal'])
  if src and src['status'] in DRAFT:
   rows.append({'source_class':CLASS,'english_literal':r['english_literal'],
     'english_key_sha256':sha(r['english_literal'].encode('utf8')),
     'previous_status':src['status'],'previous_polish_ascii':src['polish_ascii_draft'],
     'reviewed_polish_ascii':r['polish_ascii_draft'],'row_sha256':fp(r),
     'evidence':'original_JVM_ldc_addBulletPoints_or_createSmallDescription_or_getName_getIntelTags_getSortString_1061',
     'review_status':'semantic_and_original_JVM_reviewed_offline_pending_native_Windows'})
 if len(rows)!=HISTORICAL_NEW:raise ValueError('Historical candidate count incorrect')
 return {'schema_version':1,'release':'1.0.61','game_version':'0.98a-RC8',
  'source_class':CLASS,'previous_api_map_sha256':sha((t/OLD).read_bytes()),
  'reviewed_api_map_sha256':sha((t/NEW).read_bytes()),
  'historical_reviewed_new':len(rows),'previous_historical_reviewed':HISTORICAL_PREVIOUS,
  'historical_reviewed_total':HISTORICAL_PREVIOUS+len(rows),
  'historical_remaining':HISTORICAL_TOTAL-HISTORICAL_PREVIOUS-len(rows),
  'new_missing_java_literals':NEW_LITERALS,
  'corrected_prior_java_literals':REPAIRS,
  'reviewed_historical_rows':rows,'native_windows_gameplay_tested':False}

def cumulative(root:Path,previous_ledger:Path,record:dict)->dict:
 d=json.loads(Path(previous_ledger).read_text('utf8'))
 old=d.get('reviewed',[])
 if len(old)!=HISTORICAL_PREVIOUS or d.get('installed_version')!='1.0.55':raise ValueError('Invalid previous review ledger')
 oldkeys={(x['source_class'],x['row_sha256']) for x in old}
 if len(oldkeys)!=HISTORICAL_PREVIOUS:raise ValueError('Duplicate previous reviews')
 older_set={x['row_sha256'] for x in old if x['source_class']==CLASS}
 if older_set:raise ValueError('Gate Hauler previously counted; refuse double review')
 addition=[{'source_class':x['source_class'],'row_sha256':x['row_sha256'],
  'english_key_sha256':x['english_key_sha256'],'evidence':x['evidence'],
  'review_status':x['review_status']} for x in record['reviewed_historical_rows']]
 if len(addition)!=HISTORICAL_NEW or len({x['row_sha256'] for x in addition})!=HISTORICAL_NEW:raise ValueError('Missing unique new historical reviews')
 return {'schema_version':1,'installed_version':'1.0.61',
  'previous_ledger':'docs/API_SEMANTIC_REVIEW_1055.json',
  'review_protocol':'Immutable 391 prior fingerprints plus 25 original-JVM-reviewed GateHaulerIntel historic DRAFT/OPTIONAL rows, including idiomatic compositions. 3 new original JVM literals are excluded from historical count. No Windows native gameplay.',
  'new_historical_reviews':HISTORICAL_NEW,'reviewed':old+addition}

def check(root:Path,recordfile:Path,previous_ledger:Path|None=None,all_ledger:Path|None=None)->dict:
 record=inventory(root)
 if json.loads(Path(recordfile).read_text('utf8'))!=record:raise ValueError('Review record mutation or wrong SHA')
 if previous_ledger and all_ledger:
  expected=cumulative(root,previous_ledger,record)
  if json.loads(Path(all_ledger).read_text('utf8'))!=expected:raise ValueError('Cumulative historical review ledger mutated')
 return {'release':'1.0.61','new_historical_reviews':HISTORICAL_NEW,
  'historical_reviewed_total':HISTORICAL_PREVIOUS+HISTORICAL_NEW,
  'historical_unreviewed':HISTORICAL_TOTAL-HISTORICAL_PREVIOUS-HISTORICAL_NEW,
  'existing_391_fingerprints_preserved':bool(previous_ledger and all_ledger),
  'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--record',type=Path,required=True);p.add_argument('--previous',type=Path)
 p.add_argument('--ledger',type=Path);p.add_argument('--generate',action='store_true');a=p.parse_args()
 if a.generate:
  a.record.write_text(json.dumps(inventory(a.worktree),ensure_ascii=True,indent=2)+'\n','utf8')
  if a.previous and a.ledger:a.ledger.write_text(json.dumps(cumulative(a.worktree,a.previous,inventory(a.worktree)),ensure_ascii=True,indent=2)+'\n','utf8')
 print(json.dumps(check(a.worktree,a.record,a.previous,a.ledger),indent=2))
