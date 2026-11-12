#!/usr/bin/env python3
"""Negative regressions: 1.0.33 PF story translation must not drift or fake review."""
from __future__ import annotations
import argparse,copy,csv,json,tempfile
from pathlib import Path
from story_pf_plan_1033 import API,OBF
from verify_story_1033 import loadmap,verify_diff,composed_samples
from verify_review_1033 import verify as verify_review,readrows
from check_release_gates_1033 import check as check_gates


def reject(callback):
 try:callback()
 except (AssertionError,ValueError,RuntimeError):return
 raise AssertionError('Invalid alteration was not rejected')

def check(root,ledger_path,old_ledger_path,gates_path):
 o=root/'buildtools/NARZEDZIA_OBF';a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 old_o=loadmap(o/'TLUMACZENIA_OBF_10130.csv');new_o=loadmap(o/'TLUMACZENIA_OBF_10133.csv')
 old_a=loadmap(a/'translations/TLUMACZENIA_JAR_1032.csv');new_a=loadmap(a/'translations/TLUMACZENIA_JAR_1033.csv')
 verify_diff(old_o,new_o,OBF);verify_diff(old_a,new_a,API)
 old_ledger=json.loads(old_ledger_path.read_text());ledger=json.loads(ledger_path.read_text())
 verify_review(new_a,old_ledger,ledger)
 assert len(composed_samples(root)['examples'])==10
 count=0
 def neg(fn):
  nonlocal count
  reject(fn);count+=1
 # Alter an unrelated historical row.
 tmp=copy.deepcopy(new_a);tmp[20]['polish_ascii_draft']+='!'
 neg(lambda:verify_diff(old_a,tmp,API))
 tmp=copy.deepcopy(new_o);tmp[10]['polish_ascii_draft']+='!'
 neg(lambda:verify_diff(old_o,tmp,OBF))
 # Delete one of the newly approved constants.
 neg(lambda:verify_diff(old_a,new_a[:-1],API))
 neg(lambda:verify_diff(old_o,new_o[:-1],OBF))
 # Modify the acronym or a required suffix.
 tmp=copy.deepcopy(new_a)
 target=next(r for r in tmp if r['source_class']=='com.fs.starfarer.api.util.Misc' and r['english_literal']=='story')
 target['polish_ascii_draft']='story'
 neg(lambda:verify_diff(old_a,tmp,API))
 tmp=copy.deepcopy(new_o)
 target=next(r for r in tmp if r['source_class']=='com.fs.starfarer.ui.d' and r['english_literal']==' points: ')
 target['polish_ascii_draft']=' points: '
 neg(lambda:verify_diff(old_o,tmp,OBF))
 # Duplicate map and alter old status (disallow quiet alteration of provenance).
 tmp=copy.deepcopy(new_a);tmp.append(tmp[-1]);neg(lambda:verify_diff(old_a,tmp,API))
 tmp=copy.deepcopy(new_o);tmp[20]['status']='VERIFIED_STORY_PF_1033';neg(lambda:verify_diff(old_o,tmp,OBF))
 # Review provenance hashes cannot be fabricated, rewritten, removed or duplicated.
 tmp=copy.deepcopy(ledger);tmp['reviewed'][0]['row_sha256']='0'*64
 neg(lambda:verify_review(new_a,old_ledger,tmp))
 tmp=copy.deepcopy(ledger);tmp['reviewed'][-1]['row_sha256']='0'*64
 neg(lambda:verify_review(new_a,old_ledger,tmp))
 tmp=copy.deepcopy(ledger);tmp['reviewed'][-1]=tmp['reviewed'][-2]
 neg(lambda:verify_review(new_a,old_ledger,tmp))
 tmp=copy.deepcopy(ledger);tmp['reviewed']=tmp['reviewed'][:-1]
 neg(lambda:verify_review(new_a,old_ledger,tmp))
 # Release blocked even if someone changes metadata to 1.1.
 g=json.loads(gates_path.read_text());g['gates'][1]['status']='verified'
 with tempfile.TemporaryDirectory() as d:
  path=Path(d)/'g.json';path.write_text(json.dumps(g))
  neg(lambda:check_gates(root,path,old_ledger_path,ledger_path))
 neg(lambda:check_gates(root,gates_path,old_ledger_path,ledger_path,strict=True))
 assert count==14,count
 print(json.dumps({'release':'1.0.33','negative_cases_passed':count,'complete_text_samples':10,
                  'blocked_1_1':True,'legacy_maps_protected':True},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--old-ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1032.json'))
 p.add_argument('--ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1033.json'))
 p.add_argument('--gates',type=Path,default=Path('docs/RELEASE_GATES_11.json'))
 a=p.parse_args();check(a.worktree,a.ledger,a.old_ledger,a.gates)
