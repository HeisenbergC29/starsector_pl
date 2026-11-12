#!/usr/bin/env python3
"""Fail closed for 1.0.32: 30 immutable prior reviews + 25 actually corrected rows.

All 55 reviews are offline context checks only. 6 newly translated JVM
literals are a distinct cohort and must still be tested in running Windows.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
from apply_1032 import CORRECTIONS,NEW
from verify_review_1031 import verify as verify_old, fingerprint, fmt_markers
from audit_api_effective_1031 import DRAFT_STATUSES

EXPECTED_OLD=30
EXPECTED_NEW=25
EVIDENCE={'assembled_light_year_tooltip','quantity_label_number_neutral'}

def readrows(path):
 with path.open('r',encoding='utf8',newline='') as f:return list(csv.DictReader(f))

def verify(rows,old_ledger,new_ledger):
 assert new_ledger['schema_version']==1 and new_ledger['installed_version']=='1.0.32'
 assert old_ledger['schema_version']==1 and old_ledger['installed_version']=='1.0.30'
 assert len(new_ledger['reviewed'])==EXPECTED_OLD+EXPECTED_NEW
 assert new_ledger['reviewed'][:EXPECTED_OLD]==old_ledger['reviewed'],'prior approvals were altered'
 old_report=verify_old(rows,old_ledger)
 assert old_report['reviewed_offline_not_gameplay']==EXPECTED_OLD
 bykey={(r['source_class'],r['english_literal']):r for r in rows}
 byfingerprint={(r['source_class'],fingerprint(r)):r for r in rows}
 seen=set()
 for entry in new_ledger['reviewed']:
  key=(entry['source_class'],entry['row_sha256'])
  assert key not in seen,'duplicate approval'
  seen.add(key)
 assert len(seen)==55
 expect={(cl,en) for cl,pairs in CORRECTIONS.items() for en in pairs}
 matched=set()
 for entry in new_ledger['reviewed'][EXPECTED_OLD:]:
  assert entry['evidence'] in EVIDENCE
  key=(entry['source_class'],entry['row_sha256'])
  assert key in byfingerprint,'stale or invented review proof'
  r=byfingerprint[key];cl,en=r['source_class'],r['english_literal']
  assert (cl,en) in expect and r['status'] in DRAFT_STATUSES,'wrong review candidate'
  before,after=CORRECTIONS[cl][en]
  assert r['polish_ascii_draft']==after and before!=after
  if 'worth of fuel' in en or ' light ' in en or 'combat deployment' in en:
   assert entry['evidence']=='assembled_light_year_tooltip'
  else:
   assert entry['evidence']=='quantity_label_number_neutral'
  assert fmt_markers(en)==fmt_markers(after),'format variable mismatch'
  assert after.isascii() and en.count('\n')==after.count('\n')
  matched.add((cl,en))
 assert matched==expect,('unreviewed corrections',expect-matched)
 pool=[r for r in rows if r['status'] in DRAFT_STATUSES]
 assert len(rows)==5225 and len(pool)==3658
 verified_new=sum(r['status']=='VERIFIED_COMPOSED_FUEL_TOOLTIP_1032' for r in rows)
 assert verified_new==6
 return {'existing_review_count':30,'new_review_count':25,'reviewed_offline':55,'pending_offline_review':3603,'pending_runtime_reviews_cohort':3658,'additional_new_literals_pending_runtime':6,'total_pending_runtime_in_tracked_cohorts':3664}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--map',type=Path,required=True);p.add_argument('--old-ledger',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(verify(readrows(a.map),json.loads(a.old_ledger.read_text()),json.loads(a.ledger.read_text())),indent=2))
