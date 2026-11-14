#!/usr/bin/env python3
"""Negative-mutation regression of PirateBaseIntel scope, category tags and event highlight."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1054 import readmap
from apply_1062 import CLASS,OLD,NEW,ADDITIONS,REPAIRS,build
from verify_1062 import check,render

def run(root:Path)->dict:
 root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 before=readmap(api/OLD);now=readmap(api/NEW)
 plan,_=build(before)
 if plan!=now:raise ValueError('The installed map is not canonical')
 row=lambda rows,lit:next(r for r in rows if r['source_class']==CLASS and r['english_literal']==lit)
 variants={r['english_literal']:r['polish_ascii_draft'] for r in now if r['source_class']==CLASS}
 failed={}
 def reject(name,fn):
  try:fn()
  except (ValueError,AssertionError,KeyError,StopIteration,TypeError):failed[name]='REJECTED'
  else:raise AssertionError(('Bad 1.0.62 mutation incorrectly accepted',name))
 def change_source(mutator):
  p=copy.deepcopy(before);mutator(p);build(p)
 def change_render(mutator):
  p=dict(variants);mutator(p);render(p)
 reject('delete existing map row',lambda:change_source(lambda p:p.pop(next(i for i,x in enumerate(p) if x['source_class']==CLASS))))
 reject('duplicate existing map row',lambda:change_source(lambda p:p.append(dict(row(p,'Agreement broken')))))
 reject('reviewed row incorrectly reclassified',lambda:change_source(lambda p:row(p,'Agreement broken').update(status='REVIEWED_ALREADY')))
 reject('unexpected previous Polish translation',lambda:change_source(lambda p:row(p,'Agreement broken').update(polish_ascii_draft='FAKE')))
 reject('new missing literal already mapped',lambda:change_source(lambda p:p.append({'source_class':CLASS,'english_literal':'Agreement','polish_ascii_draft':'test','status':'DRAFT_ONLY_NOT_INSTALLED'})))
 reject('unapproved previously approved row modified',lambda:change_source(lambda p:row(p,' Base - Destroyed').update(polish_ascii_draft='NADPISANO')))
 reject('translation of Fleet log technical sort key',lambda:change_render(lambda p:p.update({'Fleet log':'Dziennik floty'})))
 reject('translation of Colony threats internal tag',lambda:change_render(lambda p:p.update({'Colony threats':'Zagrozenia kolonii'})))
 reject('missing agreement highlighted token',lambda:change_render(lambda p:p.update({'Agreement':'Umowa'})))
 reject('wrong lowercase dynamic agreement value',lambda:change_render(lambda p:p.update({'agreement':'umowa'})))
 reject('English agreement event translation',lambda:change_render(lambda p:p.update({'Agreement broken':'Agreement broken'})))
 reject('ambiguous repeated highlight',lambda:change_render(lambda p:p.update({'Agreement made with base commander':'Porozumienie Porozumienie zawarte'})))
 report=check(root)
 if len(failed)!=12:raise ValueError('Negative mutation cases not exhaustive')
 return {'release':'1.0.62','negative_mutations_rejected':len(failed),'cases':failed,
  'source_verified':True,'original_jvm_ldc_uses':report['original_jvm_ldc_uses'],
  'historical_new_reviews':report['historical_newly_reviewed'],
  'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
