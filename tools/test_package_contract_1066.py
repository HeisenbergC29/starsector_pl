#!/usr/bin/env python3
"""Negative tests: reject fraudulent v1.0.66 preflight metadata."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import package_1066

def test(root:Path)->dict:
 original=package_1066.check;base=original(root);reject=[]
 diffs=[('fake completed history',{'historical_api_reviews_total':3658}),
 ('incorrect new historical review count',{'new_unique_historical_reviews':999}),
 ('inflate composition evidence',{'rendered_combinations':1000}),
 ('claim changed data files',{'unchanged_game_data_files':869}),
 ('claimed unverified mapping',{'mapped_class_scoped_literals':300}),
 ('hide literal corrections',{'corrected_ui_fragments':0}),
 ('hide untranslated legacy API backlog',{'historical_api_unreviewed':0})]
 try:
  for title,change in diffs:
   fake=dict(base);fake.update(change);package_1066.check=lambda _r,x=fake:x
   try:package_1066.preflight(root)
   except (ValueError,KeyError):reject.append(title)
   else:raise AssertionError(('Invalid contract accepted',title))
 finally:package_1066.check=original
 if len(reject)!=7 or package_1066.preflight(root)!=base:raise ValueError('Contract recovery/coverage failure')
 return {'version':'1.0.66','preflight_passed':True,'invalid_metadata_cases_rejected':reject}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args();print(json.dumps(test(a.worktree),indent=2))
