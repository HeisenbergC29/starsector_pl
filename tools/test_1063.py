#!/usr/bin/env python3
"""Adversarial negative tests for 1.0.63 class scope and dynamic grammar."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1054 import readmap
from apply_1063 import CLASS,OLD,NEW,REPAIRS,build
from verify_1063 import render,check

def test(root:Path):
 root=Path(root);t=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 original=readmap(t/OLD);now=readmap(t/NEW)
 if build(original)[0]!=now:raise ValueError('Not an approved 1.0.63 mapping')
 cls={r['english_literal']:r['polish_ascii_draft'] for r in now if r['source_class']==CLASS}
 reject={}
 def must_fail(name,fn):
  try:fn()
  except (ValueError,KeyError,AssertionError,StopIteration):reject[name]='REJECTED'
  else:raise AssertionError(('Invalid translation incorrectly accepted',name))
 def map_change(fn):
  x=copy.deepcopy(original);fn(x);build(x)
 def text_change(fn):
  x=dict(cls);fn(x);render(x)
 def source(x,key):return next(r for r in x if r['source_class']==CLASS and r['english_literal']==key)
 must_fail('delete reviewed original row',lambda:map_change(lambda x:x.pop(next(i for i,r in enumerate(x) if r['source_class']==CLASS))))
 must_fail('duplicate original mapping',lambda:map_change(lambda x:x.append(dict(source(x,'Colony threats')))))
 must_fail('review status rewritten before approval',lambda:map_change(lambda x:source(x,'Colony threats').update(status='REVIEWED_FAKE')))
 must_fail('unknown previous Polish text',lambda:map_change(lambda x:source(x,'Colony threats').update(polish_ascii_draft='FAKE')))
 must_fail('previously protected mapping changed',lambda:map_change(lambda x:source(x,'Impact').update(polish_ascii_draft='FAKE')))
 must_fail('missing %s highlight placeholder',lambda:text_change(lambda x:x.update({' operations for %s ':'. Zaklocenie potrwa '})))
 must_fail('technical category tag translated',lambda:text_change(lambda x:x.update({'Colony threats':'Zagrozenia dla kolonii'})))
 must_fail('destroyed colony with English label',lambda:text_change(lambda x:x.update({'The Pather cells have smuggled a planetbuster onto ':'The Pather cells have smuggled a planetbuster onto '})))
 must_fail('warning loses required space',lambda:text_change(lambda x:x.update({'If they succeed, the colony will effectively be destroyed.':'Jesli plan sie powiedzie, kolonia zostanie praktycznie zniszczona.'})))
 must_fail('bad support-base composition',lambda:text_change(lambda x:x.update({' is providing support to these cells.':' wspiera te komorki.'})))
 must_fail('grammatically invalid averted industrial target',lambda:text_change(lambda x:x.update({' operations was averted by the local security forces.':' dzialalnosc udaremniono.'})))
 must_fail('double space injected into planetbuster line',lambda:text_change(lambda x:x.update({' and detonated it. The colony has been effectively destroyed.':'.  Nastepnie zdetonowali ladunek, praktycznie niszczac kolonie.'})))
 report=check(root)
 if len(reject)!=12:raise ValueError('Wrong negative test count')
 return {'release':'1.0.63','rejected_corrupted_map_and_composition_cases':12,
  'rechecked_approved_compositions':report['rendered_combinations'],'cases':reject}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(test(p.parse_args().worktree),indent=2))
