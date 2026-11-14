#!/usr/bin/env python3
"""Append-only 48 historical API reviews for inspection and Path base intel."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1054 import readmap
from apply_1064 import CLASSES,DRAFT,OLD,NEW,REPAIRS,TECHNICAL,BASE_SHA,fp,sha,build
PREVIOUS=482
TOTAL=3658

def inventory(worktree:Path)->dict:
 path=Path(worktree)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(path/OLD);new=readmap(path/NEW)
 approved,stats=build(old)
 if new!=approved:raise ValueError('Source API map and reviewed v1064 target do not match')
 before={(r['source_class'],r['english_literal']):r for r in old}
 selected=[]
 for r in new:
  if r['source_class'] not in CLASSES:continue
  o=before[(r['source_class'],r['english_literal'])]
  if o['status'] not in DRAFT:continue
  selected.append({'source_class':r['source_class'],'english_literal':r['english_literal'],
   'english_key_sha256':sha(r['english_literal'].encode()),
   'old_status':o['status'],'old_draft':o['polish_ascii_draft'],
   'new_draft':r['polish_ascii_draft'],'old_row_sha256':fp(o),'row_sha256':fp(r),
   'evidence':'original_JVM_HegemonyInspection_and_LuddicPathBase_1064',
   'review_status':'original_JVM_semantic_review_offline_pending_native_Windows'})
 if len(selected)!=48 or len({(x['source_class'],x['row_sha256']) for x in selected})!=48:
  raise ValueError('Wrong approved historical review count')
 return {'schema_version':1,'release':'1.0.64','game_version':'0.98a-RC8',
   'source_classes':list(CLASSES),'previous_api_map_sha256':sha((path/OLD).read_bytes()),
   'new_api_map_sha256':sha((path/NEW).read_bytes()),
   'previous_historical_reviews':PREVIOUS,'new_historical_reviews':48,
   'historical_reviewed_total':530,'historical_remaining':TOTAL-530,
   'corrected_literals':[{'source_class':cl,'english_literal':en,'polish_ascii_draft':pl}
     for (cl,en),pl in REPAIRS.items()],
   'protected_technical_category_keys':[{'source_class':cl,'english_literal':en}
     for cl,en in sorted(TECHNICAL)],
   'historical_reviewed_rows':selected,'native_windows_gameplay_tested':False}

def cumulative(previous:dict,record:dict)->dict:
 old=previous.get('reviewed',[])
 if previous.get('installed_version')!='1.0.63' or len(old)!=PREVIOUS:
  raise ValueError('Wrong 482-row previous historical review ledger')
 past={(x['source_class'],x['row_sha256']) for x in old}
 if len(past)!=PREVIOUS or any(x['source_class'] in CLASSES for x in old):
  raise ValueError('Previous review inventory overlaps selected classes')
 added=[{k:r[k] for k in ('source_class','row_sha256','english_key_sha256','evidence','review_status')}
    for r in record['historical_reviewed_rows']]
 if len(added)!=48 or len(set((x['source_class'],x['row_sha256']) for x in added))!=48:
  raise ValueError('Historical review additions not unique')
 return {'schema_version':1,'installed_version':'1.0.64','previous_ledger':'docs/API_SEMANTIC_REVIEW_1063.json',
   'review_protocol':'All 482 previous historical review fingerprints preserved exactly plus 48 class-scoped DRAFT/OPTIONAL inspection and Luddic Path base strings verified with original Java ldc/cp and three technical Set tag guards; native Windows UI untested.',
   'new_historical_reviews':48,'reviewed':old+added}

def check(root:Path,record:Path,previous:Path|None=None,ledger:Path|None=None)->dict:
 expected=inventory(root)
 if json.loads(Path(record).read_text('utf8'))!=expected:raise ValueError('Reviewed 48-row registry unexpectedly changed')
 if previous and ledger:
  prev=json.loads(Path(previous).read_text('utf8'))
  if json.loads(Path(ledger).read_text('utf8'))!=cumulative(prev,expected):
   raise ValueError('Cumulative historical ledger not append-only')
 return {'release':'1.0.64','new_historical_reviews':48,'historical_reviewed_total':530,
   'historical_unreviewed':3128,'prior_482_preserved':bool(previous and ledger)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--record',type=Path,required=True);p.add_argument('--previous',type=Path)
 p.add_argument('--ledger',type=Path);p.add_argument('--generate',action='store_true')
 a=p.parse_args()
 if a.generate:
  obj=inventory(a.worktree);a.record.write_text(json.dumps(obj,ensure_ascii=True,indent=2)+'\n','utf8')
  if a.previous and a.ledger:
   a.ledger.write_text(json.dumps(cumulative(json.loads(a.previous.read_text('utf8')),obj),ensure_ascii=True,indent=2)+'\n','utf8')
 print(json.dumps(check(a.worktree,a.record,a.previous,a.ledger),indent=2))
