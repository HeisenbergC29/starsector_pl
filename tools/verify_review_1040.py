#!/usr/bin/env python3
"""Append-only offline review ledger for 18 historical gender-context API fragments."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from apply_1040 import CORRECT
from verify_1040 import validate_map,read,composed
DRAFT={'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}

def fp(r):return hashlib.sha256('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode()).hexdigest()
def selected(cur):
 keys={(cl,en) for cl,q in CORRECT.items() for en in q}
 return sorted((r for r in cur if (r['source_class'],r['english_literal']) in keys),key=lambda r:(r['source_class'],r['english_literal']))

def create(root,prev,out):
 p=json.loads(prev.read_text('utf8'));assert p['installed_version']=='1.0.38' and len(p['reviewed'])==104
 cur=read(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1040.csv')
 s=selected(cur);assert len(s)==18 and all(r['status'] in DRAFT for r in s)
 used={x['row_sha256'] for x in p['reviewed']}
 assert all(fp(r) not in used for r in s)
 ledger={'schema_version':1,'installed_version':'1.0.40',
  'review_protocol':'104 earlier immutable offline reviews plus 18 repaired gender-neutral text fragments around getManOrWoman in 7 classes; verified original/patched JVM strings and 24 gendered partial compositions; some complete scenes contain other unreviewed pronouns. Windows gameplay NOT tested.',
  'reviewed':p['reviewed']+[
    {'source_class':r['source_class'],'row_sha256':fp(r),'english_key_sha256':hashlib.sha256(r['english_literal'].encode()).hexdigest(),
     'evidence':'bar_gendered_man_or_woman_context_original_and_patched_jvm_1040',
     'review_status':'offline_local_fragment_pending_other_pronouns_and_native_windows'} for r in s]}
 out.write_text(json.dumps(ledger,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
 return ledger

def verify(root,prev,out):
 assert validate_map(root)['api_map_rows']==5257
 prior=json.loads(prev.read_text('utf8'));new=json.loads(out.read_text('utf8'))
 assert prior['installed_version']=='1.0.38' and len(prior['reviewed'])==104
 assert new['schema_version']==1 and new['installed_version']=='1.0.40' and len(new['reviewed'])==122
 assert new['reviewed'][:104]==prior['reviewed']
 cur=read(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1040.csv')
 index={(r['source_class'],fp(r)):r for r in cur}
 assert len(index)==5257
 seen=set()
 for i,rec in enumerate(new['reviewed']):
  key=(rec['source_class'],rec['row_sha256'])
  assert key in index and key not in seen,(i,rec)
  seen.add(key)
  if i>=104:
   row=index[key]
   assert row['status'] in DRAFT and row['polish_ascii_draft'].isascii()
   assert rec['english_key_sha256']==hashlib.sha256(row['english_literal'].encode()).hexdigest()
   assert rec['evidence']=='bar_gendered_man_or_woman_context_original_and_patched_jvm_1040'
   assert rec['review_status']=='offline_local_fragment_pending_other_pronouns_and_native_windows'
 assert {r['row_sha256'] for r in new['reviewed'][104:]}=={fp(r) for r in selected(cur)}
 assert sum(r['status'] in DRAFT for r in cur)==3658
 assert composed(root)['gendered_snippets']==24
 return {'prior_reviews':104,'new_reviews':18,'reviewed_offline':122,'historical_unreviewed':3536,'historical_total':3658}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--prior-ledger',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--generate',action='store_true');a=p.parse_args()
 if a.generate:create(a.worktree,a.prior_ledger,a.ledger)
 print(json.dumps(verify(a.worktree,a.prior_ledger,a.ledger),indent=2))
