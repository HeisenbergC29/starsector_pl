#!/usr/bin/env python3
"""48 context-group historical DRAFT rows, append-only to v1054 review ledger.

Reviewed fragments are anchored to their full source class, both original and
final literals, and original JVM constant/use evidence; this is not game testing.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from apply_1055 import BLOCK,KNIGHTS,GENERIC,OLD,NEW,REPAIRS
from apply_1054 import readmap,sha
DRAFT={'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
PREVIOUS_COUNT=343
NEW_COUNTS={BLOCK:14,KNIGHTS:10,GENERIC:24}
REVIEWED_TOTAL=391
HISTORICAL_TOTAL=3658

def fp(r):return sha('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode())

def chosen(root,previous):
 root=Path(root);prev=json.loads(Path(previous).read_text('utf8'))
 if prev.get('installed_version')!='1.0.54' or len(prev.get('reviewed',[]))!=PREVIOUS_COUNT:
  raise ValueError('Wrong previous semantic review')
 tr=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(tr/OLD);current=readmap(tr/NEW)
 if len(old)!=5290 or len(current)!=5298:raise ValueError('Unexpected mapping data')
 oldids={(x['source_class'],x['english_literal']) for x in old}
 previousids={(x['source_class'],x['row_sha256']) for x in prev['reviewed']}
 currentids={(x['source_class'],fp(x)) for x in current}
 if not previousids.issubset(currentids) or len(previousids)!=PREVIOUS_COUNT:
  raise ValueError('A previously reviewed row changed or disappeared')
 selected=[x for x in current if x['source_class'] in NEW_COUNTS and x['status'] in DRAFT and
           (x['source_class'],x['english_literal']) in oldids and (x['source_class'],fp(x)) not in previousids]
 actual={cl:sum(x['source_class']==cl for x in selected) for cl in NEW_COUNTS}
 if actual!=NEW_COUNTS or len(selected)!=48 or not set(REPAIRS).issubset({(x['source_class'],x['english_literal']) for x in selected}):
  raise ValueError(('Wrong reviewed inventory',actual))
 return prev,selected

def make(root,previous):
 prev,selected=chosen(root,previous)
 new=[{'source_class':r['source_class'],'row_sha256':fp(r),
       'english_key_sha256':sha(r['english_literal'].encode()),
       'evidence':'original_JVM_CONST_String_ldc_blockade_group_1055',
       'review_status':'reviewed_grammar_and_original_jvm_offline_pending_native_windows'} for r in selected]
 return {'schema_version':1,'installed_version':'1.0.55',
   'previous_ledger':'docs/API_SEMANTIC_REVIEW_1054.json',
   'review_protocol':'343 previous fingerprint-preserved reviews + 48 historical DRAFT/OPTIONAL UI fragments from BlockadeFGI (14), KnightsOfLuddTakeoverExpedition (10) and GenericRaidFGI (24), including two fixed compositions. Eight new literals are not counted as historical; original JVM constant and ldc uses audited; no Windows gameplay',
   'new_historical_reviews':48,'reviewed':prev['reviewed']+new}

def check(root,previous,ledger):
 expected=make(root,previous)
 if json.loads(Path(ledger).read_text('utf8'))!=expected:raise ValueError('Cumulative 1.0.55 ledger mismatch')
 if len(expected['reviewed'])!=REVIEWED_TOTAL:raise ValueError('Wrong historical review total')
 return {'release':'1.0.55','old_reviewed':PREVIOUS_COUNT,'new_reviewed':48,
   'historical_reviewed':REVIEWED_TOTAL,'historical_unreviewed':HISTORICAL_TOTAL-REVIEWED_TOTAL,
   'original_jvm_verified_offline':True,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--generate',action='store_true');a=p.parse_args()
 if a.generate:a.ledger.write_text(json.dumps(make(a.worktree,a.previous),ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps(check(a.worktree,a.previous,a.ledger),indent=2))
