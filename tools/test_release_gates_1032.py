#!/usr/bin/env python3
"""Make semantic review fraud, stale fingerprints and premature 1.1 fail closed."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from check_release_gates_1032 import check

def failure(fn):
 try:fn()
 except (AssertionError,ValueError,RuntimeError,KeyError):return
 raise AssertionError('Expected negative test failure')

def main(root:Path,gates:Path,prior:Path,ledger:Path):
 import tempfile
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);valid=json.loads(gates.read_text());approved=json.loads(ledger.read_text());
  def verify(x,y,strict=False):
   g=p/'gates.json';l=p/'ledger.json'
   g.write_text(json.dumps(x));l.write_text(json.dumps(y))
   return check(root,g,prior,l,strict)
  x=verify(valid,approved);assert not x['release_11_allowed']
  n=0
  def bad(change,where='gate'):
   nonlocal n
   x=copy.deepcopy(valid);y=copy.deepcopy(approved)
   if where=='gate':change(x)
   else:change(y)
   failure(lambda:verify(x,y));n+=1
  bad(lambda x:x['gates'][2].__setitem__('unresolved_count',0))
  bad(lambda x:x['gates'][2].__setitem__('reviewed_offline',9999))
  bad(lambda x:x['gates'][2].__setitem__('gameplay_unverified_count',0))
  bad(lambda x:x['gates'][2].__setitem__('new_literal_count',0))
  bad(lambda x:x['gates'][0].__setitem__('status','verified'))
  bad(lambda x:x['reviewed'][-1].__setitem__('row_sha256','0'*64),'ledger')
  bad(lambda x:x['reviewed'].append(x['reviewed'][-1]),'ledger')
  bad(lambda x:x['reviewed'].__delitem__(-1),'ledger')
  failure(lambda:verify(valid,approved,strict=True));n+=1
 print(json.dumps({'positive':'PASS','negative_cases':n,'blocked_release':'1.1'}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,default=Path('docs/RELEASE_GATES_11.json'));p.add_argument('--prior',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1031.json'));p.add_argument('--ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1032.json'))
 a=p.parse_args();main(a.worktree,a.gates,a.prior,a.ledger)
