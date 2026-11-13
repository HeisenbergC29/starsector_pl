#!/usr/bin/env python3
"""Cumulative historical API semantic ledger: 314 old + 10 context-corrected DRAFT rows."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from apply_1052 import OLD,NEW,CORRECTIONS,ADDITIONS,readmap

def sha(b):return hashlib.sha256(b).hexdigest()
def fp(r):return sha('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode())

def make(root,previous):
 old=json.loads(Path(previous).read_text('utf8'))
 if old.get('installed_version')!='1.0.51' or len(old.get('reviewed',[]))!=314:raise ValueError('Wrong prior cumulative review ledger')
 trans=Path(root)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations';before=readmap(trans/OLD);after=readmap(trans/NEW)
 b={(x['source_class'],x['english_literal']):x for x in before}
 n={(x['source_class'],x['english_literal']):x for x in after}
 if len(b)!=5269 or len(n)!=5283 or set(n)-set(b)!=set(ADDITIONS):raise ValueError('Translation source keys unexpected')
 prior_ids={(v['source_class'],v['row_sha256']) for v in old['reviewed']}
 if len(prior_ids)!=314:raise ValueError('Duplicate old reviewed rows')
 if not prior_ids.issubset({(x['source_class'],fp(x)) for x in after}):
  raise ValueError('Earlier reviewed row silently modified')
 fresh=[]
 for key,(pl_old,pl_new) in sorted(CORRECTIONS.items()):
  pre=b[key];new=n[key]
  if pre['status'] not in ('DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED'):
   raise ValueError(('Previously verified, nonhistorical row counted as new',key))
  if pre['polish_ascii_draft']!=pl_old or new['polish_ascii_draft']!=pl_new:
   raise ValueError('Incorrect source edit')
  if (key[0],fp(pre)) in prior_ids:raise ValueError(('Already reviewed, cannot count twice',key))
  fresh.append({'source_class':key[0],'row_sha256':fp(new),'english_key_sha256':sha(key[1].encode()),
   'evidence':'original_JVM_CONSTANT_String_and_11_gender_getter_callsites_1052',
   'review_status':'context_grammar_reviewed_offline_pending_native_windows'})
 if len(fresh)!=10:raise ValueError('Incorrect historical DRAFT reviews added')
 result={
  'schema_version':1,'installed_version':'1.0.52','previous_ledger':'docs/API_SEMANTIC_REVIEW_1051.json',
  'review_protocol':'314 earlier immutable reviews + 10 newly verified historical DRAFT/OPTIONAL bar-dialogue text fragments; 14 previously untranslated class-scoped JVM fragments added but not counted as historical DRAFT, 324/3658 reviewed, 3334 remain; runtime Windows not tested.',
  'new_historical_reviews':10,'added_nonhistorical_exact_jvm_fragments':len(ADDITIONS),
  'reviewed':old['reviewed']+fresh
 }
 if len({(x['source_class'],x['row_sha256']) for x in result['reviewed']})!=324:raise ValueError('Review count mismatch')
 return result

def check(root,previous,ledger):
 expected=make(root,previous);actual=json.loads(Path(ledger).read_text('utf8'))
 if expected!=actual:raise ValueError('Historical cumulative ledger diverged from sources')
 return {'release':'1.0.52','old_reviews':314,'new_reviewed_historical':10,'total_reviewed':324,
    'original_historical_draft_total':3658,'unreviewed_historical':3334,
    'new_nonhistorical_class_scoped_literals':14,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous',type=Path,required=True)
 p.add_argument('--ledger',type=Path,required=True);p.add_argument('--generate',action='store_true')
 args=p.parse_args()
 if args.generate:args.ledger.write_text(json.dumps(make(args.worktree,args.previous),indent=2)+'\n',encoding='utf8')
 print(json.dumps(check(args.worktree,args.previous,args.ledger),indent=2))
