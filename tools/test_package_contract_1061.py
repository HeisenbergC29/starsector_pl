#!/usr/bin/env python3
"""Negative tests: reject fraudulent v1.0.61 preflight metadata."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import package_1061

def test(root:Path)->dict:
 original=package_1061.check;base=original(root);reject=[]
 diffs=[('fake completed history',{'reviewed_historical_rows':3658}),
 ('wrong API row count',{'api_rows':5311}),('invent dynamic grammar',{'grammar_combinations':100}),
 ('claim 100 data files',{'game_data_files_unchanged':100}),
 ('hide new source literals',{'new_literals':0}),('invent 20 repairs',{'fixed_existing_literals':20})]
 try:
  for title,change in diffs:
   fake=dict(base);fake.update(change);package_1061.check=lambda _r,x=fake:x
   try:package_1061.preflight(root)
   except (ValueError,KeyError):reject.append(title)
   else:raise AssertionError(('Invalid contract accepted',title))
 finally:package_1061.check=original
 if len(reject)!=6 or package_1061.preflight(root)!=base:raise ValueError('Contract recovery/coverage failure')
 return {'version':'1.0.61','preflight_passed':True,'invalid_metadata_cases_rejected':reject}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(test(a.worktree),indent=2))
