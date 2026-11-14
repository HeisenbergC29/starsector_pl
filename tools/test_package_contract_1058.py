#!/usr/bin/env python3
"""Reject false v1.0.58 package preflight metadata before cross-build."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import package_1058

def run(root):
 old=package_1058.check
 from verify_1058 import check
 baseline=check(root)
 denied={}
 try:
  for key,bad in [('new_reviewed_dialogue_rows',123),('speech_attributions_corrected',135),('remaining_gender_placeholders',0),('other_game_data_files_unchanged',868),('unchanged_api_map_entries',5297)]:
   mutated=dict(baseline);mutated[key]=bad
   package_1058.check=lambda _root,_d=mutated:_d
   try:package_1058.preflight(root)
   except (ValueError,KeyError):denied[key]='REJECTED'
   else:raise AssertionError(('Unapproved package contract accepted',key))
 finally:package_1058.check=old
 package_1058.preflight(root)
 if len(denied)!=5:raise AssertionError('Incomplete package mutation tests')
 return {'release':'1.0.58','preflight_passed':True,'invalid_package_states_rejected':denied}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
