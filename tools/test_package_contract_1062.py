#!/usr/bin/env python3
"""Negative tests: reject fraudulent v1.0.62 preflight metadata."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import package_1062

def test(root:Path)->dict:
 original=package_1062.check;base=original(root);reject=[]
 diffs=[('fake completed history',{'historical_newly_reviewed':3658}),
 ('wrong API row count',{'map_rows':5311}),('invent dynamic grammar',{'rendered_tooltip_combinations':100}),
 ('claim 100 data files',{'game_data_files_byte_identical':100}),
 ('hide new source literals',{'new_literal_translations':0}),('invent 20 repairs',{'existing_literal_corrections':20})]
 try:
  for title,change in diffs:
   fake=dict(base);fake.update(change);package_1062.check=lambda _r,x=fake:x
   try:package_1062.preflight(root)
   except (ValueError,KeyError):reject.append(title)
   else:raise AssertionError(('Invalid contract accepted',title))
 finally:package_1062.check=original
 if len(reject)!=6 or package_1062.preflight(root)!=base:raise ValueError('Contract recovery/coverage failure')
 return {'version':'1.0.62','preflight_passed':True,'invalid_metadata_cases_rejected':reject}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(test(a.worktree),indent=2))
