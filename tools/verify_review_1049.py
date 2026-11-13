#!/usr/bin/env python3
"""Append-only 1.0.49 semantic review, with 44 original-JVM short UI texts + 5 revised DRAFT strings."""
from __future__ import annotations
import json,hashlib,argparse
from pathlib import Path
from apply_1049 import PLAN_PATH,OLD,NEW,readmap,plan
DRAFT={'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
STATIC_DOC=Path(__file__).parent.parent/'docs/API_STATIC_UI_REVIEW_1049.json'
def fp(r):return hashlib.sha256('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode()).hexdigest()
def make(root,previous,static_path=STATIC_DOC):
 root=Path(root);prev=json.loads(Path(previous).read_text('utf8'))
 if prev.get('installed_version')!='1.0.48' or len(prev.get('reviewed',[]))!=203:
  raise ValueError('Incorrect prior semantic review ledger')
 rows=readmap(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'/NEW)
 base=readmap(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'/OLD)
 edits,extra,items=plan(base)
 index={(r['source_class'],r['english_literal']):r for r in rows}
 if len(index)!=5261 or len(rows)!=5261:raise ValueError('Review map missing')
 previous_ids={(x['source_class'],x['row_sha256']) for x in prev['reviewed']}
 if len(previous_ids)!=203:raise ValueError('Duplicate prior reviews')
 current_ids={(r['source_class'],fp(r)) for r in rows}
 if not previous_ids.issubset(current_ids):raise ValueError('Previously reviewed source translation changed')
 static=json.loads(Path(static_path).read_text('utf8'))
 if static.get('version')!='1.0.49' or len(static.get('reviewed',[]))!=44 or static.get('original_jvm_matches')!=44:
  raise ValueError('Invalid static reviewed inventory')
 static_rows=[];used=set()
 for v in static['reviewed']:
  k=v['source_class'],v['english_literal']
  if k in used or k not in index or k in edits:raise ValueError(('Duplicate or unsuitable static record',k))
  used.add(k);r=index[k]
  if r['status'] not in DRAFT or fp(r)!=v['row_sha256'] or r['polish_ascii_draft']!=v['polish_ascii_reviewed'] or v['evidence']!='exact_original_JVM_CONSTANT_String_single_match':
   raise ValueError(('Static review does not match current mapping',k))
  if (r['source_class'],fp(r)) in previous_ids:raise ValueError('Already reviewed static UI counted twice')
  static_rows.append(r)
 fixed_rows=[]
 for key,obj in edits.items():
  r=index[key]
  if r['status'] not in DRAFT:continue
  if (r['source_class'],fp(r)) in previous_ids or key in used:raise ValueError('Prior reviewed double count')
  fixed_rows.append(r)
 if len(fixed_rows)!=5:raise ValueError('Review scope of corrected historical rows changed')
 reviewed=list(prev['reviewed']);nnew=0
 for r in static_rows+fixed_rows:
  e={'source_class':r['source_class'],'row_sha256':fp(r),'english_key_sha256':hashlib.sha256(r['english_literal'].encode()).hexdigest(),
    'evidence':'original_JVM_constant_string_1049',
    'review_status':'reviewed_short_ui_literal_original_jvm_1049_pending_windows' if r in static_rows else 'reviewed_1049_gender_and_number_grammar_original_jvm_pending_windows'}
  reviewed.append(e);nnew+=1
 if nnew!=49 or len(reviewed)!=252 or len({(x['source_class'],x['row_sha256']) for x in reviewed})!=252:
  raise ValueError('Invalid cumulative review sum')
 return {'schema_version':1,'installed_version':'1.0.49','previous_ledger':'docs/API_SEMANTIC_REVIEW_1048.json',
   'review_protocol':'Preserve prior 203 immutable reviews, add 44 short player-visible UI text literal reviews and 5 corrected historical DRAFT/OPTIONAL reviews; 252/3658 reviewed offline, 3406 pending. Exact original JVM constant-string matches verified; Windows runtime not tested.',
   'new_static_review_count':44,'new_corrected_historical_review_count':5,'reviewed':reviewed}
def verify(root,previous,ledger):
 got=json.loads(Path(ledger).read_text('utf8'));expected=make(root,previous)
 if got!=expected:raise ValueError('Review ledger differs from verified current translation mapping')
 return {'prior_reviews':203,'new_short_ui_reviews':44,'new_fixed_historical_reviews':5,'historical_reviewed_offline':252,'historical_unreviewed':3406,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--generate',action='store_true')
 a=p.parse_args()
 if a.generate:a.ledger.write_text(json.dumps(make(a.worktree,a.previous),ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps(verify(a.worktree,a.previous,a.ledger),indent=2))
