#!/usr/bin/env python3
"""Verify immutable offline-reviewed gender-neutral rules fragments in 1.0.34."""
import argparse,csv,hashlib,io,json
from pathlib import Path
from apply_1034 import PATCHES,ALLOWED_FIELDS,OLD_SHA,NEW_SHA
from verify_1034 import revert

def sha(s):return hashlib.sha256(s.encode('ascii')).hexdigest()

def check(root,ledger_path):
 ledger=json.loads(ledger_path.read_text('utf8'))
 assert ledger['schema_version']==1 and ledger['installed_version']=='1.0.34'
 assert ledger['reviewed_rows']==27 and ledger['exact_edits']==62
 assert ledger['removed_visible_pronoun_placeholders']==75 and ledger['pending_windows_ui_rows']==27
 assert ledger['rules_sha256_before']==OLD_SHA and ledger['rules_sha256_after']==NEW_SHA
 new_bytes=(root/'mod/data/campaign/rules.csv').read_bytes();old_bytes=revert(new_bytes)
 now={r['id']:r for r in csv.DictReader(io.StringIO(new_bytes.decode('ascii'),newline=''))}
 old={r['id']:r for r in csv.DictReader(io.StringIO(old_bytes.decode('ascii'),newline=''))}
 seen=set();edits=0;removed=0
 for item in ledger['reviewed']:
  key=item['id'];field=item['field']
  assert key not in seen and key in PATCHES and field in ALLOWED_FIELDS[key]
  assert item['offline_review']=='approved_grammatical_rewrite_without_pronoun_placeholder'
  assert item['windows_gameplay']=='not_tested'
  assert sha(old[key][field])==item['before_sha256'] and sha(now[key][field])==item['after_sha256']
  assert item['exact_edits']==len(PATCHES[key])
  assert item['removed_variable_references']==old[key][field].count('$')-now[key][field].count('$')
  seen.add(key);edits+=item['exact_edits'];removed+=item['removed_variable_references']
 assert seen==set(PATCHES) and edits==62 and removed==75
 return {'reviewed_offline_rows':27,'removed_visible_variable_references':75,'pending_windows_ui_rows':27,'Java_pronoun_calls_remaining':219}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path);ap.add_argument('--ledger',required=True,type=Path)
 a=ap.parse_args();print(json.dumps(check(a.worktree,a.ledger),indent=2))
