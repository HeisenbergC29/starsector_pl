#!/usr/bin/env python3
"""Reject false v1.0.59 package preflight metadata before cross-build."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import package_1059

def run(root):
 old=package_1059.check
 from verify_1059 import check
 baseline=check(root)
 denied={}
 try:
  for key,bad in [('class_scoped_new_literals',5),('revised_old_literal',0),('total_api_map_rows',5298),('game_data_files_byte_identical',869),('monthly_report_quantity_renderings_checked',0)]:
   mutated=dict(baseline);mutated[key]=bad
   package_1059.check=lambda _root,_d=mutated:_d
   try:package_1059.preflight(root)
   except (ValueError,KeyError):denied[key]='REJECTED'
   else:raise AssertionError(('Unapproved package contract accepted',key))
 finally:package_1059.check=old
 package_1059.preflight(root)
 if len(denied)!=5:raise AssertionError('Incomplete package mutation tests')
 return {'release':'1.0.59','preflight_passed':True,'invalid_package_states_rejected':denied}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
