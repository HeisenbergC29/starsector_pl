#!/usr/bin/env python3
"""Negative/synthetic checks for 1.0.25 map and text boundary validation."""
import argparse,csv,copy,tempfile
from pathlib import Path
from verify_1025_ui import rows
from apply_1025 import OBF,STATUS
FIELDS=['source_class','english_literal','polish_ascii_draft','status']

def verify_append(old,updated):
 assert updated[:len(old)]==old,'historical map tampered'
 expected=[{'source_class':cl,'english_literal':src,'polish_ascii_draft':dst,'status':STATUS} for cl,items in OBF.items() for src,dst in items.items()]
 assert updated[len(old):]==expected,'unapproved row or incorrect translation'
 assert len(updated)==len({(r['source_class'],r['english_literal']) for r in updated}),'duplicated mapping'
 return True

def main(root):
 p=root/'buildtools/NARZEDZIA_OBF';old=rows(p/'TLUMACZENIA_OBF_10124.csv');new=rows(p/'TLUMACZENIA_OBF_10125.csv')
 assert verify_append(old,new)
 tests=[]
 def reject(name,transform):
  fake=copy.deepcopy(new);transform(fake)
  try:verify_append(old,fake)
  except AssertionError:tests.append(name)
  else:raise AssertionError('dangerous edit was not rejected: '+name)
 reject('changed historical translation',lambda r:r[6].__setitem__('polish_ascii_draft','DISALLOWED'))
 reject('added unrelated mapping',lambda r:r.append({'source_class':'test','english_literal':'technical_id','polish_ascii_draft':'localized_id','status':STATUS}))
 reject('changed new translation',lambda r:r[-1].__setitem__('polish_ascii_draft','CR'))
 reject('duplicate source key',lambda r:r.append(copy.copy(r[-1])))
 reject('removed original row',lambda r:r.pop(0))
 assert len(tests)==5
 print('1.0.25 NEGATIVE TESTS PASS:',', '.join(tests))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();main(a.worktree)