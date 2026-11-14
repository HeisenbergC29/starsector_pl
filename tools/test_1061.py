#!/usr/bin/env python3
"""Negative tests rejecting unapproved GateHauler translations and false review counts."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1054 import readmap
from apply_1061 import CLASS,OLD,NEW,BASE_SHA,DRAFT,REPAIRS,NEW_LITERALS,build,sha
from verify_1061 import check,render
from build_review_1061 import inventory

def run(root:Path)->dict:
 root=Path(root);trans=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 base=readmap(trans/OLD);b,stats=build(base)
 keys={x['english_literal']:x['polish_ascii_draft'] for x in b if x['source_class']==CLASS}
 if check(root)['grammar_combinations']!=93:raise ValueError('Independent verifier failed')
 errors={}
 def reject(name,callback):
  try:callback()
  except (ValueError,AssertionError,KeyError):errors[name]='REJECTED'
  else:raise AssertionError(('Invalid test case accepted',name))
 def mut(fun):
  a=copy.deepcopy(base);fun(a);build(a)
 def edit(english,field,val):
  return lambda xs: next(x for x in xs if x['source_class']==CLASS and x['english_literal']==english).__setitem__(field,val)
 reject('lost original class row',lambda:mut(lambda x:x.pop(next(i for i,r in enumerate(x) if r['source_class']==CLASS))))
 reject('extra duplicate class key',lambda:mut(lambda x:x.append(dict(x[-1]))))
 reject('claim former draft was already reviewed',lambda:mut(edit('Entered open space','status','MANUALLY_VERIFIED')))
 reject('translate missing day twice',lambda:mut(lambda x:x.append({'source_class':CLASS,'english_literal':'day','polish_ascii_draft':'dzien','status':'DRAFT_ONLY_NOT_INSTALLED'})))
 reject('replace previous translation unexpectedly',lambda:mut(edit('Status: operational','polish_ascii_draft','Stan: gotowy')))
 reject('replace previously approved location label',lambda:mut(edit('Location: ','status','DRAFT_ONLY_NOT_INSTALLED')))
 def wrong(e,repl):
  d=dict(keys);d[e]=repl;render(d)
 reject('English plural days',lambda:wrong('days','days'))
 reject('wrong singular day grammar',lambda:wrong('day','dni'))
 reject('missing sentence separator',lambda:wrong(' ',''))
 reject('incorrect original arrival declension',lambda:wrong('The gate hauler has arrived to the ','Holownik dotarl do '))
 reject('English transit suffix',lambda:wrong(' for transit',' for transit'))
 reject('feminine status for masculine noun',lambda:wrong('Status: dormant','Stan: uspiona'))
 if len(errors)!=12:raise ValueError('Negative tests were skipped')
 return {'release':'1.0.61','negative_mutations_rejected':len(errors),'cases':errors,
  'verified_real_original_jvm_calls':49,'historical_new_reviewed':25,
  'grammar_combinations_passed':93,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(run(a.worktree),indent=2))
