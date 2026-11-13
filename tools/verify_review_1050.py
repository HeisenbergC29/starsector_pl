#!/usr/bin/env python3
"""Append-only semantic review of 60 new short UI messages, no duplicate accounting."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1050 import NEW,readmap
from verify_review_1049 import fp,DRAFT
STATIC_DOC=Path(__file__).resolve().parent.parent/'docs/API_STATIC_UI_REVIEW_1050.json'
def make(root,previous,static_path=STATIC_DOC):
 prev=json.loads(Path(previous).read_text('utf8'));reviewed=prev.get('reviewed',[])
 if prev.get('installed_version')!='1.0.49' or len(reviewed)!=252:raise ValueError('Wrong immutable previous review baseline')
 rows=readmap(Path(root)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'/NEW)
 if len(rows)!=5269:raise ValueError('API map row count changed')
 mapped={(r['source_class'],r['english_literal']):r for r in rows}
 if len(mapped)!=5269:raise ValueError('Duplicate API source keys')
 prev_keys={(r['source_class'],r['row_sha256']) for r in reviewed}
 if len(prev_keys)!=252:raise ValueError('Duplicate inherited reviews')
 allkeys={(r['source_class'],fp(r)) for r in rows}
 if not prev_keys.issubset(allkeys):raise ValueError('An earlier-reviewed translation was changed')
 data=json.loads(Path(static_path).read_text('utf8'))
 if data.get('version')!='1.0.50' or data.get('count')!=60 or len(data.get('reviewed',[]))!=60:raise ValueError('Wrong new reviewed list')
 new=[];used=set()
 for obj in data['reviewed']:
  key=obj['source_class'],obj['english_literal']
  if key in used or key not in mapped:raise ValueError(('Duplicate/missing source key',key))
  used.add(key);r=mapped[key]
  if r['status'] not in DRAFT or (r['source_class'],fp(r)) in prev_keys:raise ValueError(('Non-DRAFT / double-counted review',key))
  if obj['polish_ascii_reviewed']!=r['polish_ascii_draft'] or obj['row_sha256']!=fp(r) or obj['source_status']!=r['status']:
   raise ValueError(('Translation or status was not actually reviewed',key))
  if obj['evidence']!='exact_original_JVM_CONSTANT_String_one_match_1050' or obj['windows_gameplay']!='not_tested':raise ValueError('Review evidence not pinned')
  new.append({'source_class':r['source_class'],'row_sha256':fp(r),
   'english_key_sha256':hashlib.sha256(r['english_literal'].encode()).hexdigest(),
   'evidence':'original_JVM_CONSTANT_String_1050','review_status':'short_UI_label_original_JVM_offline_pending_native_windows'})
 if len(new)!=60:raise ValueError('Incorrect number of new audited labels')
 out={'schema_version':1,'installed_version':'1.0.50','previous_ledger':'docs/API_SEMANTIC_REVIEW_1049.json',
  'review_protocol':'252 prior exact immutable API DRAFT reviews plus 60 new class-scoped original-JVM-confirmed labels from BaseIndustry/MarketCMD/BaseIntelPlugin. 312/3658 offline; 3346 still unreviewed. Not a Windows gameplay claim.',
  'new_static_review_count':60,'reviewed':reviewed+new}
 if len({(x['source_class'],x['row_sha256']) for x in out['reviewed']})!=312:raise ValueError('Duplicate cumulative review key')
 return out
def verify(root,previous,ledger):
 expected=make(root,previous);actual=json.loads(Path(ledger).read_text('utf8'))
 if actual!=expected:raise ValueError('Cumulative review ledger mismatch')
 return {'release':'1.0.50','prior_historical_reviewed':252,'new_reviewed_offline':60,
   'historical_reviewed_offline':312,'historical_total':3658,'historical_unreviewed':3346,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--generate',action='store_true')
 a=p.parse_args()
 if a.generate:a.ledger.write_text(json.dumps(make(a.worktree,a.previous),indent=2,ensure_ascii=True)+'\n')
 print(json.dumps(verify(a.worktree,a.previous,a.ledger),indent=2))
