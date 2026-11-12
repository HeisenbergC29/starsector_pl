#!/usr/bin/env python3
"""Fail closed: 55 immutable old reviews + 3 new verified STORY fragments.

Offline linguistic verification is NOT runtime Windows gameplay validation.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
from story_pf_plan_1033 import API

DRAFT_STATUS={'DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME','OPTIONAL_PATCHER_NOT_GAME_TESTED'}

def fingerprint(row):
 v='\0'.join(row[k] for k in ('source_class','english_literal','polish_ascii_draft'))
 return hashlib.sha256(v.encode('utf8')).hexdigest()
def readrows(p):
 with p.open('r',encoding='utf8',newline='') as f:return list(csv.DictReader(f))

def verify(rows,old,new):
 assert old['schema_version']==new['schema_version']==1
 assert old['installed_version']=='1.0.32' and new['installed_version']=='1.0.33'
 assert len(old['reviewed'])==55 and len(new['reviewed'])==58
 assert new['reviewed'][:55]==old['reviewed'],'old reviews modified'
 assert len(rows)==5242
 lookup={(r['source_class'],fingerprint(r)):r for r in rows}
 assert len(lookup)==len(rows)
 checked=set();extra=set()
 for i,item in enumerate(new['reviewed']):
  k=(item['source_class'],item['row_sha256'])
  assert k not in checked and k in lookup,('duplicate/stale ledger',k)
  checked.add(k)
  row=lookup[k]
  assert row['status'] in DRAFT_STATUS,('reviewed row is not DRAFT/OPTIONAL',k)
  if i<55:assert item['evidence'] in {'enum_constructor_label','tooltip_addPara','monthly_report_label','assembled_light_year_tooltip','quantity_label_number_neutral'}
  else:
   assert item['evidence']=='story_pf_81_callsites_offline'
   key=(row['source_class'],row['english_literal'])
   assert row['english_literal'] in API.get(row['source_class'],{})
   assert row['polish_ascii_draft']==API[row['source_class']][row['english_literal']]
   extra.add(key)
  assert row['polish_ascii_draft'].isascii()
  # API patcher preserves markers; complete map is also tested by Go.
 assert len(extra)==3
 pool=[r for r in rows if r['status'] in DRAFT_STATUS]
 assert len(pool)==3658
 assert len([r for r in rows if r['status']=='VERIFIED_STORY_PF_1033'])==17
 assert len([r for r in rows if r['status']=='VERIFIED_COMPOSED_FUEL_TOOLTIP_1032'])==6
 return {'reviewed_offline':58,'newly_reviewed_existing':3,'pending_offline_semantics':3600,
         'api_new_1033':17,'api_pending_windows_in_tracked_cohorts':3681,
         'status_not_used_as_runtime_visibility_filter':True}

def main():
 p=argparse.ArgumentParser();p.add_argument('--map',required=True,type=Path);p.add_argument('--old-ledger',required=True,type=Path);p.add_argument('--ledger',required=True,type=Path)
 a=p.parse_args();print(json.dumps(verify(readrows(a.map),json.loads(a.old_ledger.read_text('utf8')),json.loads(a.ledger.read_text('utf8'))),indent=2))
if __name__=='__main__':main()
