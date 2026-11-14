#!/usr/bin/env python3
"""Adversarial v1066 map/grammar mutation test, independent of Windows gameplay."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1054 import readmap
from apply_1066 import SIM,IND,TUT,OLD,NEW,build
from verify_1066 import render,check

def test(root:Path)->dict:
 root=Path(root);tr=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(tr/OLD);new=readmap(tr/NEW)
 if build(old)[0]!=new:raise ValueError('Wrong approved baseline')
 mapped={cl:{r['english_literal']:r['polish_ascii_draft'] for r in new if r['source_class']==cl}
         for cl in (SIM,IND,TUT)}
 rejected={}
 def reject(name,cb):
  try:cb()
  except (ValueError,KeyError,StopIteration,AssertionError):rejected[name]='REJECTED'
  else:raise AssertionError(('Unsafe mutation accepted',name))
 def rewrite_source(cb):
  rows=copy.deepcopy(old);cb(rows);build(rows)
 def rewrite_render(cb):
  rows=copy.deepcopy(mapped);cb(rows);render(rows)
 def select(rows,cl,english):return next(r for r in rows if r['source_class']==cl and r['english_literal']==english)
 reject('source map missing original industry key',lambda:rewrite_source(lambda r:r.remove(select(r,IND,'Requires %s more '))))
 reject('source map contains duplicated key',lambda:rewrite_source(lambda r:r.append(dict(select(r,SIM,'Do nothing')))))
 reject('unapproved legacy translation modification',lambda:rewrite_source(lambda r:select(r,IND,'Can not be built').update(polish_ascii_draft='BROKEN')))
 reject('simulator draft review status falsified',lambda:rewrite_source(lambda r:select(r,SIM,'Do nothing').update(status='FALSIFIED')))
 reject('unrelated map class changed',lambda:rewrite_source(lambda r:next(x for x in r if x['source_class'] not in (SIM,IND,TUT)).update(polish_ascii_draft='BAD')))
 reject('progress day declension regressed',lambda:rewrite_render(lambda m:m[IND].update(days='day')))
 reject('production units untranslated',lambda:rewrite_render(lambda m:m[IND].update(units='units')))
 reject('remaining days english suffix',lambda:rewrite_render(lambda m:m[IND].update({' left':' left'})))
 reject('dynamic construction cost marker missing',lambda:rewrite_render(lambda m:m[IND].update({'%s and %s ':'Koszt: %s'})))
 reject('dynamic colony location inflected',lambda:rewrite_render(lambda m:m[IND].update({' at ':' na '})))
 reject('tutorial Go Dark highlight untranslated',lambda:rewrite_render(lambda m:m[TUT].update({'Go Dark':'Go Dark'})))
 reject('tutorial Emergency Burn accusative incorrect',lambda:rewrite_render(lambda m:m[TUT].update({'Emergency Burn':'Awaryjny dopalacz'})))
 reject('tutorial sensor scan grammar incorrect',lambda:rewrite_render(lambda m:m[TUT].update({'Active Sensor Burst':'Aktywny impuls czujnikow'})))
 reject('tutorial Storage highlight not found',lambda:rewrite_render(lambda m:m[TUT].update({'"Storage"':'"Storage"'})))
 reject('simulator aggression section still English',lambda:rewrite_render(lambda m:m[SIM].update({'Aggression / behavior':'Aggression / behavior'})))
 reject('simulator developer section still English',lambda:rewrite_render(lambda m:m[SIM].update({'DevMode stuff':'DevMode stuff'})))
 result=check(root)
 if len(rejected)!=16 or result['rendered_combinations']!=60:
  raise ValueError('Mutation tests or subsequent source verification failed')
 return {'release':'1.0.66','invalid_mutations_rejected':len(rejected),
  'native_gameplay_tests':'after_1_1_release','valid_compositions_tested':60,'cases':rejected}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(test(p.parse_args().worktree),indent=2))
