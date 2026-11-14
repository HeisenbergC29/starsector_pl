#!/usr/bin/env python3
"""Build SHA-pinned audit of 31 original-JVM-reviewed PirateBaseIntel historical drafts."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1062 import CLASS,OLD,NEW,DRAFT,REPAIRS,ADDITIONS,STATUS,build,fp,sha
from apply_1054 import readmap
PREVIOUS_REVIEWS=416;TOTAL_HISTORICAL=3658

def inventory(root:Path)->dict:
 root=Path(root);path=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 before=readmap(path/OLD);after=readmap(path/NEW)
 expected,summary=build(before)
 if after!=expected:raise ValueError('Nonapproved v1.0.62 map')
 old={(r['source_class'],r['english_literal']):r for r in before}
 historic=[]
 for row in after:
  if row['source_class']!=CLASS:continue
  source=old.get((CLASS,row['english_literal']))
  if source and source['status'] in DRAFT:
   historic.append({'source_class':CLASS,'english_literal':row['english_literal'],
      'english_key_sha256':sha(row['english_literal'].encode()),
      'old_status':source['status'],'previous_polish_ascii':source['polish_ascii_draft'],
      'reviewed_polish_ascii':row['polish_ascii_draft'],'old_row_sha256':fp(source),
      'row_sha256':fp(row),'evidence':'original_JVM_PirateBaseIntel_ldc_callsite_1062',
      'review_status':'original_JVM_semantics_reviewed_offline_pending_native_Windows'})
 if len(historic)!=31 or len({x['row_sha256'] for x in historic})!=31:
  raise ValueError('Wrong count or duplicate historical reviews')
 return {'schema_version':1,'release':'1.0.62','source_class':CLASS,'game_version':'0.98a-RC8',
  'previous_api_map_sha256':sha((path/OLD).read_bytes()),'reviewed_api_map_sha256':sha((path/NEW).read_bytes()),
  'previous_historical_reviews':PREVIOUS_REVIEWS,'new_historical_reviews':len(historic),
  'historical_reviewed_total':PREVIOUS_REVIEWS+len(historic),
  'historical_remaining':TOTAL_HISTORICAL-PREVIOUS_REVIEWS-len(historic),
  'new_literals':ADDITIONS,'corrected_literals':REPAIRS,
  'technical_category_tokens_protected':['Fleet log','Colony threats'],
  'historical_reviewed_rows':historic,'native_windows_gameplay_tested':False}

def cumulative(previous:dict,record:dict)->dict:
 old=previous.get('reviewed',[])
 if previous.get('installed_version')!='1.0.61' or len(old)!=PREVIOUS_REVIEWS:
  raise ValueError('Wrong previous historical API review file')
 historical={(x['source_class'],x['row_sha256']) for x in old}
 if len(historical)!=PREVIOUS_REVIEWS or any(x['source_class']==CLASS for x in old):
  raise ValueError('Previously reviewed PirateBaseIntel or duplicate prior hash')
 add=[{'source_class':r['source_class'],'row_sha256':r['row_sha256'],
       'english_key_sha256':r['english_key_sha256'],'evidence':r['evidence'],
       'review_status':r['review_status']} for r in record['historical_reviewed_rows']]
 if len(add)!=31 or len({x['row_sha256'] for x in add})!=31:raise ValueError('Wrong new review list')
 return {'schema_version':1,'installed_version':'1.0.62',
  'previous_ledger':'docs/API_SEMANTIC_REVIEW_1061.json',
  'review_protocol':'Exact preservation of 416 previous reviewed rows plus 31 PirateBaseIntel historic DRAFT/OPTIONAL rows reviewed against the original game JVM. Two new original literals are excluded from history; two tag constants intentionally kept English. No native Windows gameplay.',
  'new_historical_reviews':31,'reviewed':old+add}

def check(root:Path,record_file:Path,previous_file:Path|None=None,new_file:Path|None=None)->dict:
 r=inventory(root)
 if json.loads(Path(record_file).read_text('utf8'))!=r:raise ValueError('Pirate Base manual audit altered')
 if previous_file is not None and new_file is not None:
  prev=json.loads(previous_file.read_text('utf8'))
  if json.loads(new_file.read_text('utf8'))!=cumulative(prev,r):raise ValueError('Historical API ledger is not append-only')
 return {'release':'1.0.62','new_historical_reviews':31,'historical_reviewed_total':447,
  'historical_remaining':3211,'previous_416_preserved':previous_file is not None,
  'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--record',required=True,type=Path);p.add_argument('--previous',type=Path);p.add_argument('--ledger',type=Path);p.add_argument('--generate',action='store_true')
 a=p.parse_args()
 if a.generate:
  a.record.write_text(json.dumps(inventory(a.worktree),ensure_ascii=True,indent=2)+'\n','utf8')
  if a.previous and a.ledger:
   a.ledger.write_text(json.dumps(cumulative(json.loads(a.previous.read_text('utf8')),inventory(a.worktree)),ensure_ascii=True,indent=2)+'\n','utf8')
 print(json.dumps(check(a.worktree,a.record,a.previous,a.ledger),indent=2))
