#!/usr/bin/env python3
"""Review ledger for 64 new gender-neutral dialogue records, 27 prior records."""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
from apply_1035 import PATCHES,OPTION_IDS,PRONOUN,OLD_SHA,NEW_SHA,sha
from verify_1035 import revert,rows
from verify_1034 import revert as revert_1034

def fieldsha(v):return hashlib.sha256(v.encode('ascii')).hexdigest()

def check(root,prior_path,ledger_path):
    prior=json.loads(prior_path.read_text('utf8'));ld=json.loads(ledger_path.read_text('utf8'))
    assert prior['schema_version']==1 and prior['installed_version']=='1.0.34'
    assert prior['reviewed_rows']==27 and prior['removed_visible_pronoun_placeholders']==75
    assert ld['schema_version']==1 and ld['installed_version']=='1.0.35' and ld['source_release']=='1.0.34'
    assert ld['prior_rules_ledger']=='docs/RULES_PRONOUN_REVIEW_1034.json'
    assert ld['reviewed_rows']==64 and ld['exact_edits']==93 and ld['removed_visible_pronoun_placeholders']==108
    assert ld['pending_windows_ui_rows']==64
    assert ld['cumulative_offline_rows']==91 and ld['cumulative_removed_references']==183
    assert ld['cumulative_pending_windows_ui_rows']==91 and ld['java_getter_calls_untouched']==219
    assert ld['rules_sha256_before']==OLD_SHA and ld['rules_sha256_after']==NEW_SHA
    nowbytes=(root/'mod/data/campaign/rules.csv').read_bytes()
    beforebytes=revert(nowbytes)
    old33=revert_1034(beforebytes)
    old=rows(beforebytes);new=rows(nowbytes);original=rows(old33)
    # Preserve ALL 27 original review approvals and their hashes.
    seen_old=set();old_removed=0
    for item in prior['reviewed']:
      key=item['id'];fld=item['field']
      assert key not in seen_old and key in old and key in original
      assert fieldsha(original[key][fld])==item['before_sha256']
      assert fieldsha(old[key][fld])==item['after_sha256']
      assert item['windows_gameplay']=='not_tested'
      seen_old.add(key);old_removed+=item['removed_variable_references']
    assert len(seen_old)==27 and old_removed==75
    seen=set();total_edits=removed=0
    for item in ld['reviewed']:
      key=item['id'];assert key in PATCHES and key not in seen and key not in seen_old
      fields=item['fields'];expected=['text','options'] if key in OPTION_IDS else ['text']
      assert fields==expected and item['exact_edits']==len(PATCHES[key])
      assert item['offline_review']=='approved_grammatical_rewrite_without_pronoun_placeholder'
      assert item['windows_gameplay']=='not_tested'
      for fld in fields:
       assert fieldsha(old[key][fld])==item['before_sha256'][fld]
       assert fieldsha(new[key][fld])==item['after_sha256'][fld]
      changed_refs=len(PRONOUN.findall((' '.join(old[key][fld] for fld in fields)).encode('ascii')))-len(PRONOUN.findall((' '.join(new[key][fld] for fld in fields)).encode('ascii')))
      assert changed_refs==item['removed_variable_references']
      assert not PRONOUN.search((' '.join(new[key][fld] for fld in fields)).encode('ascii'))
      seen.add(key);total_edits+=item['exact_edits'];removed+=changed_refs
    assert len(seen)==64 and seen==set(PATCHES) and total_edits==93 and removed==108
    return {'prior_reviewed_rows':27,'new_reviewed_rows':64,'cumulative_reviewed_rows':91,'new_removed_variable_references':108,'cumulative_removed_variable_references':183,'Java_getter_invocations_still_unresolved':219,'pending_native_windows_dialog_rows':91}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--prior-ledger',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.prior_ledger,a.ledger),indent=2))
