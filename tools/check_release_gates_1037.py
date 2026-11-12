#!/usr/bin/env python3
"""Fail-closed release 1.1 blocker verification for current 1.0.37 patch."""
import argparse,json
from pathlib import Path
from verify_1037 import mapdiff,phrases
from verify_review_1037 import verify as verify_review

def check(root,gates,prior,ledger):
 d=mapdiff(root);z=phrases()
 a=json.loads(gates.read_text('utf8'))
 assert a['target_version']=='1.1' and a['schema_version']==1
 by={x['id']:x for x in a['gates']}
 assert set(by)=={'story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime'}
 assert all(x['status']!='completed' for x in a['gates'])
 s=by['story_contexts'];assert s['status']=='in_progress' and s['reviewed_offline']==81 and s['pending_windows_ui']==81
 p=by['pronoun_contexts'];assert p['status']=='blocked' and p['total_jvm_getter_calls']==219 and p['unresolved_count']==212
 assert p['reviewed_reflexive_calls_offline']==1 and p['reviewed_subject_getter_calls_offline']==6 and p['pending_windows_ui_java_getter_calls']==219
 assert p['shared_her_conflict_open'] is True and p['reviewed_rules_rows_offline']==91 and p['removed_visible_gender_variable_refs']==183
 r=verify_review(root,prior,ledger)
 c=by['draft_semantics'];assert c['status']=='blocked' and c['reviewed_offline']==83 and c['unresolved_count']==3575
 assert c['total_draft_rows']==3658 and c['gameplay_unverified_count']==3684 and c['new_literal_count']==26
 assert c['review_ledger']=='docs/API_SEMANTIC_REVIEW_1037.json'
 assert by['windows_runtime']['status']=='blocked' and by['text_completeness']['status']=='in_progress'
 assert d['api_map_rows']==5245 and len(z['male'])==len(z['female'])==6
 return {'release':'1.0.37','target':'1.1','release_allowed':False,'getter_pending_offline':212,'windows_getter_pending':219,'api_semantic_pending':3575,'api_runtime_pending':3684}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True);p.add_argument('--prior-ledger',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(check(a.worktree,a.gates,a.prior_ledger,a.ledger),indent=2))
