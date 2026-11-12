#!/usr/bin/env python3
"""Append-only 78 -> 83 historical API semantic-review fingerprints, with callsites."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from apply_1037 import CORRECT,CALLS
from verify_1037 import rows
DRAFT={'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}

def fp(row):
 return hashlib.sha256('\0'.join(row[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode('utf8')).hexdigest()

def generate(root,prior,out):
 old=json.loads(prior.read_text('utf8'));assert old['installed_version']=='1.0.36' and len(old['reviewed'])==78
 mapping=rows(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1037.csv')
 idx={(r['source_class'],r['english_literal']):r for r in mapping}
 additions=[]
 for cl,ss in CORRECT.items():
  for en,(_,pl) in ss.items():
   r=idx[(cl,en)];assert r['polish_ascii_draft']==pl and r['status'] in DRAFT
   method,offset=CALLS[cl]
   additions.append({'source_class':cl,'row_sha256':fp(r),
     'evidence':'reviewed_both_genders_original_and_patched_jvm_1037',
     'getter': 'getHeOrShe', 'jvm_method':method,'jvm_offset':offset,
     'english_key_sha256':hashlib.sha256(en.encode('utf8')).hexdigest()})
 prior_keys={(x['source_class'],x['row_sha256']) for x in old['reviewed']}
 assert len(additions)==5 and not any((r['source_class'],r['row_sha256']) in prior_keys for r in additions)
 data={'schema_version':1,'installed_version':'1.0.37',
       'review_protocol':'78 prior immutable offline API reviews plus five class-scoped grammatical corrections of getHeOrShe contexts, verified for both genders against original and patched JVM constant pools. Not Windows gameplay.',
       'reviewed':old['reviewed']+additions}
 assert len(data['reviewed'])==83
 out.write_text(json.dumps(data,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 return data

def verify(root,prior,out):
 p=json.loads(prior.read_text('utf8'));n=json.loads(out.read_text('utf8'))
 assert n['schema_version']==p['schema_version']==1
 assert n['reviewed'][:78]==p['reviewed'] and len(n['reviewed'])==83
 rr=rows(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1037.csv')
 lookup={(r['source_class'],fp(r)):r for r in rr}
 assert len(lookup)==5245
 seen=set()
 for i,item in enumerate(n['reviewed']):
  key=(item['source_class'],item['row_sha256'])
  assert key in lookup and key not in seen
  seen.add(key)
  r=lookup[key];assert r['status'] in DRAFT and r['polish_ascii_draft'].isascii()
  if i>=78:
   assert item['evidence']=='reviewed_both_genders_original_and_patched_jvm_1037'
   assert item['source_class'] in CORRECT and r['english_literal'] in CORRECT[item['source_class']]
   assert item['english_key_sha256']==hashlib.sha256(r['english_literal'].encode('utf8')).hexdigest()
   assert (item['jvm_method'],item['jvm_offset'])==CALLS[item['source_class']]
 assert len([r for r in rr if r['status'] in DRAFT])==3658
 return {'previous_offline_reviewed':78,'new_offline_reviewed':5,'offline_reviewed_total':83,'historical_to_review':3575}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--prior-ledger',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--generate',action='store_true')
 x=p.parse_args()
 if x.generate:generate(x.worktree,x.prior_ledger,x.ledger)
 print(json.dumps(verify(x.worktree,x.prior_ledger,x.ledger),indent=2))
