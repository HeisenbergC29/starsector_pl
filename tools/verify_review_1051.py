#!/usr/bin/env python3
"""Cumulative historical API review: 312 immutable prior + 2 new UI fragments.

The two fragments are in the original JVM class, are passed only to the
TooltipMakerAPI.addPara UI method, and retain both %s placeholders. Native
Windows gameplay is not claimed or inferred.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1051 import CLASS,OLD,NEW,CORRECTIONS,readmap

def sha(b):return hashlib.sha256(b).hexdigest()
def fp(row):return sha('\0'.join(row[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode('utf8'))

def make(root,previous):
 old=json.loads(Path(previous).read_text('utf8'))
 if old.get('installed_version')!='1.0.50' or len(old.get('reviewed',[]))!=312:
  raise ValueError('Wrong previous review baseline')
 base=Path(root)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 before=readmap(base/OLD);after=readmap(base/NEW)
 if len(before)!=5269 or len(after)!=5269:raise ValueError('Wrong map cardinality')
 oldkeys={(r['source_class'],r['row_sha256']) for r in old['reviewed']}
 if len(oldkeys)!=312:raise ValueError('Duplicate historical prior review')
 before_by_key={(r['source_class'],r['english_literal']):r for r in before}
 after_by_key={(r['source_class'],r['english_literal']):r for r in after}
 if before_by_key.keys()!=after_by_key.keys():raise ValueError('API source keys changed')
 new_entries=[]
 for eng,(prior,corrected) in CORRECTIONS.items():
  key=(CLASS,eng)
  if key not in before_by_key:raise ValueError(('Missing expected source row',key))
  a=before_by_key[key];b=after_by_key[key]
  if a['status']!='DRAFT_ONLY_NOT_INSTALLED' or a['polish_ascii_draft']!=prior or b['polish_ascii_draft']!=corrected:
   raise ValueError(('Wrong previous/current translation or status',key))
  if (CLASS,fp(a)) in oldkeys:raise ValueError(('Previously reviewed row double counted',key))
  new_entries.append({'source_class':CLASS,'row_sha256':fp(b),
      'english_key_sha256':sha(eng.encode()),
      'evidence':'original_jvm_addDescToTooltip_ldc_and_exact_two_byte_operand_exception_1051',
      'review_status':'context_reviewed_personality_UI_pending_native_windows'})
 if len(new_entries)!=2:raise ValueError('Wrong new review count')
 allkey={(r['source_class'],fp(r)) for r in after}
 if not oldkeys.issubset(allkey):raise ValueError('Older reviewed rows modified')
 record={'schema_version':1,'installed_version':'1.0.51',
  'previous_ledger':'docs/API_SEMANTIC_REVIEW_1050.json',
  'review_protocol':'312 previous exact reviews plus 2 new personality tooltips on original JVM; exact display-only operand exception documented, technical identity literals unchanged, native Windows gameplay untested.',
  'new_personality_display_reviews':2,
  'reviewed':old['reviewed']+new_entries}
 if len({(x['source_class'],x['row_sha256']) for x in record['reviewed']})!=314:
  raise ValueError('Cumulative review duplicates')
 return record

def verify(root,previous,ledger):
 expected=make(root,previous);actual=json.loads(Path(ledger).read_text('utf8'))
 if expected!=actual:raise ValueError('Review ledger changed from verified map')
 return {'release':'1.0.51','prior_reviews':312,'new_reviews':2,'total_history_reviewed':314,
   'historical_total':3658,'historical_unreviewed':3344,'gameplay_native_windows_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous',required=True,type=Path);p.add_argument('--ledger',required=True,type=Path);p.add_argument('--generate',action='store_true')
 a=p.parse_args()
 if a.generate:a.ledger.write_text(json.dumps(make(a.worktree,a.previous),indent=2)+'\n')
 print(json.dumps(verify(a.worktree,a.previous,a.ledger),indent=2))
