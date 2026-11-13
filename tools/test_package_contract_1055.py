#!/usr/bin/env python3
"""Catch release-package/validator interface mismatches before slow Windows build."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from package_1055 import preflight

def test(root):
 v=preflight(root)
 if v['rows_api']!=5298 or v['effective_api_literals']!=5296 or v['unchanged_game_data_files']!=870:
  raise ValueError('Package preflight did not confirm release input')
 return {'release':'1.0.55','package_validator_schema_compatible':True,
  'mapped_rows':v['rows_api'],'effective_strings':v['effective_api_literals']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
 print(json.dumps(test(a.worktree),indent=2))