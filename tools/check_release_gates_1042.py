#!/usr/bin/env python3
"""Block premature 1.1 and protect accounting of 15 purely punctuation-only fixes."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1042 import verify

def validate(root,gates):
 root=Path(root);d=json.loads(Path(gates).read_text('utf8'))
 assert d['schema_version']==1 and d['target_version']=='1.1'
 fields={x['id']:x for x in d['gates']};assert len(fields)==len(d['gates'])
 assert json.loads((root/'mod/mod_info.json').read_text('utf8'))['version']=='1.0.42'
 x=verify(root)
 assert x['corrected_rows']==15 and x['double_periods_remaining']==0
 v=fields['punctuation_regression']
 assert v['status']=='in_progress' and v['reviewed_offline']==15 and v['pending_windows_ui']==15 and v['plan_sha256']==x['review_hash']
 numeric=fields['numeric_quantities']
 assert numeric['status']=='in_progress' and numeric['reviewed_offline']==77 and numeric['pending_windows_ui']==77
 story=fields['story_contexts']
 assert story['status']=='in_progress' and story['pending_windows_ui']==81
 p=fields['pronoun_contexts'];assert p['status']=='blocked' and p['unresolved_count']==186 and p['shared_her_conflict_open'] is True and p['pending_windows_ui_rules_rows']==153 and p['pending_windows_ui_java_getter_calls']==219
 s=fields['draft_semantics'];assert s['status']=='blocked' and s['reviewed_offline']==122 and s['unresolved_count']==3536 and s['gameplay_unverified_count']==3696
 w=fields['windows_runtime'];assert w['status']=='blocked' and w['native_gameplay_tested'] is False
 return {'current_release':'1.0.42','target_version':'1.1','blocked':True,'fixed_double_periods_offline':15,'runtime_unverified':True,'getters_pending':186,'semantics_pending':3536}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);a.add_argument('--gates',type=Path,required=True);o=a.parse_args();print(json.dumps(validate(o.worktree,o.gates),indent=2))
