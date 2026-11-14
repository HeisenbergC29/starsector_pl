#!/usr/bin/env python3
"""Fail-closed packaging tests executed before Windows cross-compilation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import package_1057

def test(root:Path):
 baseline=package_1057.preflight(root);original=package_1057.check;denied={}
 try:
  for name,patch in [
   ('fake extra corrected row',{'corrected_dialogue_rows':71}),
   ('fake translation completeness',{'remaining_gender_placeholders':0}),
   ('missing original data file',{'other_game_data_files_byte_identical':868}),
   ('wrong API mapping size',{'api_map_entries_unchanged':5297}),
   ('changed placeholder count',{'removed_gender_placeholders':75})]:
   package_1057.check=lambda _,bad=patch: {**baseline,**bad}
   try:package_1057.preflight(root)
   except (ValueError,KeyError):denied[name]='REJECTED'
   else:raise AssertionError(('Packager accepted invalid release metadata',name))
 finally:package_1057.check=original
 assert len(denied)==5
 package_1057.preflight(root)
 return {'release':'1.0.57','source_preflight_pass':True,'false_contracts_rejected':denied}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);p=a.parse_args();print(json.dumps(test(p.worktree),indent=2))
