#!/usr/bin/env python3
"""Twelve negative tests of MarketCMD original-JVM-scoped grammar and map."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1054 import readmap
from apply_1065 import CLASS,OLD,NEW,REPAIRS,build
from verify_1065 import render,check

def test(root:Path)->dict:
 root=Path(root);folder=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(folder/OLD);new=readmap(folder/NEW)
 if build(old)[0]!=new:raise ValueError('Current map not approved 1.0.65')
 mapped={r['english_literal']:r['polish_ascii_draft'] for r in new if r['source_class']==CLASS}
 rejected={}
 def reject(label,action):
  try:action()
  except (ValueError,KeyError,StopIteration,AssertionError):rejected[label]='REJECTED'
  else:raise AssertionError(('Corrupted data unexpectedly accepted',label))
 def damaged_map(change):
  rows=copy.deepcopy(old);change(rows);build(rows)
 def damaged_render(change):
  rows=copy.deepcopy(mapped);change(rows);render(rows)
 def row(rows,key):return next(r for r in rows if (r['source_class'],r['english_literal'])==(CLASS,key))
 reject('map deleted original key',lambda:damaged_map(lambda r:r.remove(row(r,'Engage the '))))
 reject('map duplicated original key',lambda:damaged_map(lambda r:r.append(dict(row(r,'Engage the ')))))
 reject('map new malicious status',lambda:damaged_map(lambda r:row(r,'Engage the ').update(status='FALSIFIED_REVIEWED')))
 reject('map changed baseline user text',lambda:damaged_map(lambda r:row(r,'Engage the ').update(polish_ascii_draft='Niedozwolona zmiana')))
 reject('map changed non-target class',lambda:damaged_map(lambda r:next(x for x in r if x['source_class']!=CLASS).update(polish_ascii_draft='Falsified')))
 reject('market duration placeholder removed',lambda:damaged_render(lambda m:m.update({' operations for at least %s days.':' przez co najmniej dni.'})))
 reject('market duration incorrect declension',lambda:damaged_render(lambda m:m.update({' operations for at least %s days.':' przez co najmniej %s dni.'})))
 reject('industry dynamic inflection regressed',lambda:damaged_render(lambda m:m.update({'Your ground forces commander estimates that given the relative force strengths,  the raid should disrupt all ':'Zakloc wszystkie '})))
 reject('station attack inflection regressed',lambda:damaged_render(lambda m:m.update({'Engage the ':'Zaatakuj '})))
 reject('station defender subject gender broken',lambda:damaged_render(lambda m:m.update({' and its defenders':' i jego obroncow'})))
 reject('colon-based stability lost',lambda:damaged_render(lambda m:m.update({'Stability of ':'Stabilnosc '})))
 reject('raid skill requirement grammar regressed',lambda:damaged_render(lambda m:m.update({' raid effectiveness.':' skutecznosc rajdu.'})))
 if len(rejected)!=12:raise ValueError('Negative test count incorrect')
 return {'release':'1.0.65','invalid_mutations_rejected':len(rejected),
  'positive_rendered_combinations':check(root)['rendered_combinations'],'cases':rejected}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(test(p.parse_args().worktree),indent=2))
