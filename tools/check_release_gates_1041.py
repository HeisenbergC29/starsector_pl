#!/usr/bin/env python3
"""Conservative gates: 77 grammar fixes are not full semantic or Windows reviews."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1041 import verify as verify_map

def validate(root,gates):
 root=Path(root);doc=json.loads(Path(gates).read_text('utf8'))
 assert doc['target_version']=='1.1' and doc['schema_version']==1
 checks={x['id']:x for x in doc['gates']}
 assert len(checks)==len(doc['gates'])
 assert json.loads((root/'mod/mod_info.json').read_text('utf8'))['version']=='1.0.41'
 data=verify_map(root)
 assert data['changed_map_rows']==77 and data['changed_classes']==59
 assert data['groups']=={'unit':40,'point':25,'light_year':12}
 numeric=checks['numeric_quantities']
 assert numeric['status']=='in_progress'
 assert numeric['reviewed_offline']==77 and numeric['pending_windows_ui']==77
 assert numeric['source_version']=='1.0.41'
 assert numeric['review_sha256']==data['review_hash']
 for name in ('pronoun_contexts','draft_semantics','windows_runtime'):
  assert checks[name]['status']=='blocked',name
 assert checks['story_contexts']['status']=='in_progress'
 assert checks['story_contexts']['pending_windows_ui']==81
 p=checks['pronoun_contexts'];assert p['unresolved_count']==186 and p['total_jvm_getter_calls']==219 and p['pending_windows_ui_java_getter_calls']==219
 assert p['shared_her_conflict_open'] is True
 assert p['reviewed_rules_rows_offline']==153 and p['pending_windows_ui_rules_rows']==153
 d=checks['draft_semantics'];assert d['total_draft_rows']==3658 and d['reviewed_offline']==122 and d['unresolved_count']==3536 and d['gameplay_unverified_count']==3696
 assert checks['windows_runtime']['native_gameplay_tested'] is False
 return {'current_version':'1.0.41','target_version':'1.1','blocked':True,'numeric_offline_checked':77,
         'numeric_windows_untested':77,'pronoun_unreviewed':186,'api_semantic_unreviewed':3536}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True)
 a=p.parse_args();print(json.dumps(validate(a.worktree,a.gates),indent=2))
