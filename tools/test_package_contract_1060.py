#!/usr/bin/env python3
"""Reject false v1.0.60 package preflight metadata before cross-build."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import package_1060

def run(root):
 old=package_1060.check
 from verify_1060 import check
 baseline=check(root)
 denied={}
 try:
  for key,bad in [('added_literals',0),('corrected_literals',0),('new_api_map_rows',5304),('unchanged_data_files',869),('rendered_combinations',0)]:
   mutated=dict(baseline);mutated[key]=bad
   package_1060.check=lambda _root,_d=mutated:_d
   try:package_1060.preflight(root)
   except (ValueError,KeyError):denied[key]='REJECTED'
   else:raise AssertionError(('Unapproved package contract accepted',key))
 finally:package_1060.check=old
 package_1060.preflight(root)
 if len(denied)!=5:raise AssertionError('Incomplete package mutation tests')
 return {'release':'1.0.60','preflight_passed':True,'invalid_package_states_rejected':denied}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
