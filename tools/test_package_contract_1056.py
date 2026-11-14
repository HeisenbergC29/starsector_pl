#!/usr/bin/env python3
"""Pre-build package schema validation, independent of Windows EXE compilation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import package_1056

def run(root):
 real=package_1056.check
 from verify_1056 import check as verify_check
 package_1056.check=lambda x:verify_check(x,validate_prior=False)
 baseline=package_1056.preflight(root)
 invalid={
  'rows_api from older release':{'rows_api':5298},
  'inflated review count':{'changed_dialogue_rows':111},
  'false zero gender refs':{'remaining_gender_tokens':0},
  'missing source file count':{'unchanged_other_game_data':868},
 }
 denied=[]
 try:
  for name,diff in invalid.items():
   d=dict(baseline);d.update(diff)
   if name=='rows_api from older release':d.pop('unchanged_api_map_entries')
   package_1056.check=lambda root,_d=d:_d
   try:package_1056.preflight(root)
   except (ValueError,KeyError):denied.append(name)
   else:raise AssertionError(('Bad package metadata accepted',name))
 finally:package_1056.check=lambda x:verify_check(x,validate_prior=False)
 assert len(denied)==4
 package_1056.preflight(root)
 package_1056.check=real
 return {'release':'1.0.56','preflight_passed':True,'invalid_schema_cases_rejected':denied}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
