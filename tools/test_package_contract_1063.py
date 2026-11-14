#!/usr/bin/env python3
"""Negative tests: reject fraudulent v1.0.63 preflight metadata."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import package_1063

def test(root:Path)->dict:
 original=package_1063.check;base=original(root);reject=[]
 diffs=[('fake completed history',{'historical_api_reviewed_total':3658}),
 ('wrong new historical row count',{'historical_api_reviewed_new':350}),
 ('inflate compositions',{'rendered_combinations':1000}),
 ('fabricate changed data',{'game_data_files_byte_identical':100}),
 ('technical tag protection missing',{'technical_keys_protected':0}),
 ('inflate repair count',{'repaired_literals':100})]
 try:
  for title,change in diffs:
   fake=dict(base);fake.update(change);package_1063.check=lambda _r,x=fake:x
   try:package_1063.preflight(root)
   except (ValueError,KeyError):reject.append(title)
   else:raise AssertionError(('Invalid contract accepted',title))
 finally:package_1063.check=original
 if len(reject)!=6 or package_1063.preflight(root)!=base:raise ValueError('Contract recovery/coverage failure')
 return {'version':'1.0.63','preflight_passed':True,'invalid_metadata_cases_rejected':reject}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(test(a.worktree),indent=2))
