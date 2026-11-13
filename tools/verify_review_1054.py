#!/usr/bin/env python3
"""Append 19 genuinely reviewed historical entries, never count new map keys."""
from __future__ import annotations
import argparse,hashlib,json,zipfile,subprocess,re
from pathlib import Path
from apply_1054 import (SIM,CODEX,PHASE,PLANET,BLOCK,LEAGUE,CORRECTIONS,ADDITIONS,
                        OLD,NEW,readmap,sha)
from private_jvm_1051 import parse_class,getstr
DRAFT={'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
REV_CLASSES={SIM,CODEX,PHASE,PLANET,LEAGUE}
HISTORICAL_TOTAL=3658
PREV_N=324
NEW_N=19

def fp(r):return sha('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode())
def eligible(row):
 return row['status'] in DRAFT and (row['source_class'] in REV_CLASSES or (row['source_class'],row['english_literal']) in CORRECTIONS)

def make(root,previous):
 old=json.loads(Path(previous).read_text('utf8'))
 if len(old.get('reviewed',[]))!=PREV_N or old.get('installed_version')!='1.0.52':raise ValueError('Wrong immutable 1.0.52 review input')
 base=Path(root)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 b=readmap(base/OLD);n=readmap(base/NEW)
 oldrows={(x['source_class'],x['english_literal']):x for x in b}
 target={(x['source_class'],x['english_literal']):x for x in n}
 priorids={(x['source_class'],x['row_sha256']) for x in old['reviewed']}
 if len(priorids)!=PREV_N or not priorids.issubset({(x['source_class'],fp(x)) for x in n}):raise ValueError('Previously reviewed text changed')
 selected=[]
 for row in n:
  if not eligible(row):continue
  key=row['source_class'],row['english_literal']
  if key not in oldrows or (key[0],fp(row)) in priorids:continue
  selected.append(row)
 if len(selected)!=NEW_N or len({(x['source_class'],x['english_literal']) for x in selected})!=NEW_N:
  raise ValueError(('Unexpected candidate historical inventory',len(selected),[(x['source_class'].split('.')[-1],x['english_literal'][:40]) for x in selected]))
 if set(CORRECTIONS)-{(x['source_class'],x['english_literal']) for x in selected}:raise ValueError('Missing corrected review')
 newentries=[{'source_class':x['source_class'],'row_sha256':fp(x),'english_key_sha256':sha(x['english_literal'].encode()),
  'evidence':'original_JVM_CONST_String_ldc_and_contextual_UI_review_1054',
  'review_status':'reviewed_static_UI_or_dynamic_composition_offline_pending_native_windows'} for x in selected]
 return {'schema_version':1,'installed_version':'1.0.54','previous_ledger':'docs/API_SEMANTIC_REVIEW_1052.json',
  'review_protocol':'324 prior immutable historical reviews, 19 new class-scoped and original-JVM-checked historical DRAFT/OPTIONAL UI rows (6 corrected); 7 new literal mappings not counted as historical; Windows not tested; 343/3658, 3315 remain',
  'new_historical_reviews':NEW_N,'corrected_historical_rows':len(CORRECTIONS),'added_nonhistorical_literal_rows':len(ADDITIONS),
  'reviewed':old['reviewed']+newentries}

def check(root,previous,ledger):
 result=make(root,previous)
 if json.loads(Path(ledger).read_text('utf8'))!=result:raise ValueError('Unmatched append-only semantic ledger')
 return {'release':'1.0.54','old_reviewed':PREV_N,'new_reviewed':NEW_N,'total_reviewed':PREV_N+NEW_N,
  'historical_total':HISTORICAL_TOTAL,'historical_remaining':HISTORICAL_TOTAL-PREV_N-NEW_N,
  'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous',type=Path,required=True)
 p.add_argument('--ledger',type=Path,required=True);p.add_argument('--generate',action='store_true')
 a=p.parse_args()
 if a.generate: a.ledger.write_text(json.dumps(make(a.worktree,a.previous),ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps(check(a.worktree,a.previous,a.ledger),indent=2))
