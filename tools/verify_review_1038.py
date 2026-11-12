#!/usr/bin/env python3
"""Append-only 83->104 offline semantic reviews of the historian's visible text.

Historical DRAFT status does not mean that the patcher leaves it inactive.
Not a substitute for gameplay review.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
from apply_1038 import BAR,DONATION
from verify_1038 import rows,DRAFT,phrases
from verify_story_1033 import class_entries,texts

def fp(row):
 return hashlib.sha256('\0'.join(row[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode('utf8')).hexdigest()

def selected(current):
 return sorted((r for r in current if r['source_class'] in (BAR,DONATION) and r['status'] in DRAFT),key=lambda r:(r['source_class'],r['english_literal']))

def build(root,prior,out):
 p=json.loads(prior.read_text('utf8'))
 assert p['installed_version']=='1.0.37' and len(p['reviewed'])==83
 current=rows(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1038.csv')
 sel=selected(current)
 assert len(sel)==21 and sum(r['source_class']==BAR for r in sel)==19 and sum(r['source_class']==DONATION for r in sel)==2
 already={x['row_sha256'] for x in p['reviewed']}
 additions=[]
 for row in sel:
  digest=fp(row);assert digest not in already
  additions.append({'source_class':row['source_class'],'row_sha256':digest,
   'english_key_sha256':hashlib.sha256(row['english_literal'].encode()).hexdigest(),
   'evidence':'historian_gendered_context_original_and_patched_jvm_1038',
   'review_status':'offline_only_pending_native_windows'})
 result={'schema_version':1,'installed_version':'1.0.38',
  'review_protocol':'83 immutable earlier reviews plus 21 visually reconstructed historian/DonationOffer texts, including 18 complete gendered phrase variants and strict original/patched Java constant pools; no native Windows gameplay.',
  'reviewed':p['reviewed']+additions}
 out.write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
 return result

def verify(root,prior,ledger,patched=None):
 p=json.loads(prior.read_text('utf8'));n=json.loads(ledger.read_text('utf8'))
 assert p['installed_version']=='1.0.37' and n['installed_version']=='1.0.38' and n['schema_version']==p['schema_version']==1
 assert n['reviewed'][:83]==p['reviewed'] and len(n['reviewed'])==104
 cur=rows(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1038.csv')
 ix={(r['source_class'],fp(r)):r for r in cur}
 assert len(ix)==5254
 seen=set()
 for i,item in enumerate(n['reviewed']):
  key=(item['source_class'],item['row_sha256'])
  assert key in ix and key not in seen,(i,item)
  seen.add(key);row=ix[key]
  assert row['status'] in DRAFT and row['polish_ascii_draft'].isascii()
  if i>=83:
   assert item['review_status']=='offline_only_pending_native_windows'
   assert item['evidence']=='historian_gendered_context_original_and_patched_jvm_1038'
   assert item['english_key_sha256']==hashlib.sha256(row['english_literal'].encode()).hexdigest()
   assert row['source_class'] in (BAR,DONATION)
 assert len(selected(cur))==21
 assert {item['row_sha256'] for item in n['reviewed'][83:]}=={fp(r) for r in selected(cur)}
 assert sum(r['status'] in DRAFT for r in cur)==3658
 assert len(phrases(root)['male'])==len(phrases(root)['female'])==9
 if patched:
  with zipfile.ZipFile(patched) as z:
   cp={cl:texts(class_entries(z.read(cl.replace('.','/')+'.class'))[0]) for cl in (BAR,DONATION)}
   for row in selected(cur):assert row['polish_ascii_draft'] in cp[row['source_class']],(row['source_class'],row['english_literal'])
 return {'prior_offline_reviews':83,'new_offline_reviews':21,'offline_reviewed_total':104,
         'historical_unreviewed':3554,'historical_total':3658}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);a.add_argument('--prior-ledger',type=Path,required=True)
 a.add_argument('--ledger',type=Path,required=True);a.add_argument('--generate',action='store_true');a.add_argument('--patched-api',type=Path)
 opt=a.parse_args()
 if opt.generate:build(opt.worktree,opt.prior_ledger,opt.ledger)
 print(json.dumps(verify(opt.worktree,opt.prior_ledger,opt.ledger,opt.patched_api),indent=2))
