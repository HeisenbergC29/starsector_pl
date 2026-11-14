#!/usr/bin/env python3
"""Twelve negative map and compositional grammar checks for v1.0.64."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1054 import readmap
from apply_1064 import INSPECTION,PATH_BASE,OLD,NEW,CLASSES,REPAIRS,build
from verify_1064 import render,check

def run(root:Path)->dict:
 root=Path(root);p=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(p/OLD);new=readmap(p/NEW)
 if build(old)[0]!=new:raise ValueError('Not a verified 1.0.64 map')
 cls={cl:{r['english_literal']:r['polish_ascii_draft'] for r in new if r['source_class']==cl} for cl in CLASSES}
 rejected={}
 def reject(name,action):
  try:action()
  except (ValueError,KeyError,AssertionError,StopIteration):rejected[name]='REJECTED'
  else:raise AssertionError(('Corruption was accepted',name))
 def row(r,k):return next(x for x in r if (x['source_class'],x['english_literal'])==k)
 def broken_map(change):
  r=copy.deepcopy(old);change(r);build(r)
 def broken_text(change):
  r=copy.deepcopy(cls);change(r);render(r)
 h=(INSPECTION,'Colony threats');p=(PATH_BASE,'Fleet log');q=(PATH_BASE,'Colony threats')
 reject('missing original source row',lambda:broken_map(lambda x:x.pop(next(i for i,v in enumerate(x) if v['source_class']==INSPECTION))))
 reject('duplicated original row',lambda:broken_map(lambda x:x.append(dict(row(x,h)))))
 reject('unapproved status advance',lambda:broken_map(lambda x:row(x,h).update(status='FAKE_REVIEWED')))
 reject('unexpected original text',lambda:broken_map(lambda x:row(x,h).update(polish_ascii_draft='WRONG')))
 reject('non-targeted translation altered',lambda:broken_map(lambda x:row(x,(PATH_BASE,'Development level')).update(polish_ascii_draft='DEV LEVEL')))
 reject('Hegemony technical tag translated',lambda:broken_text(lambda x:x[INSPECTION].update({'Colony threats':'Zagrozenia dla kolonii'})))
 reject('Path base Colony threats translated',lambda:broken_text(lambda x:x[PATH_BASE].update({'Colony threats':'Zagrozenia dla kolonii'})))
 reject('Path base Fleet log sorting key translated',lambda:broken_text(lambda x:x[PATH_BASE].update({'Fleet log':'Dziennik floty'})))
 reject('Hegemony target placeholder removed',lambda:broken_text(lambda x:x[INSPECTION].update({'Operations at %s disrupted':'Zaklocono dzialalnosc w'})))
 reject('inspection decision lacks punctuation',lambda:broken_text(lambda x:x[INSPECTION].update({' will comply with the inspection. ':' zgoda na inspekcje. '})))
 reject('Path base invalid faction grammar',lambda:broken_text(lambda x:x[PATH_BASE].update({'The base serves to provide material support to active Pather cells on nearby colonies, enabling them ':'Baza wspiera komorki Sciezki i moze '})))
 reject('Path base status untranslated',lambda:broken_text(lambda x:x[PATH_BASE].update({'You do not know of any active pather cells this base might be providing support to.':'You do not know of any active pather cells'})))
 result=check(root)
 if len(rejected)!=12:raise ValueError('Negative checks count mismatch')
 return {'release':'1.0.64','rejected_invalid_cases':len(rejected),
  'original_25_rendered_combinations_valid':result['rendered_combinations'],'cases':rejected}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(run(p.parse_args().worktree),indent=2))
