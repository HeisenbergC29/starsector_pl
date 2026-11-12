#!/usr/bin/env python3
"""Fail closed: 1.0.40 is not complete 1.1 and 12 snippets are not Windows gameplay."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1040 import check as mapcheck
from verify_review_1040 import verify as reviewcheck

def verify(root,gate,prior,ledger):
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.40'
 d=json.loads(gate.read_text('utf8'));assert d['schema_version']==1 and d['target_version']=='1.1'
 g={x['id']:x for x in d['gates']};assert set(g)=={'story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime'}
 assert all(x['status']!='completed' for x in g.values())
 p=g['pronoun_contexts'];assert p['status']=='blocked'
 assert p['total_jvm_getter_calls']==219 and p['reviewed_base_get_commodity_man_or_woman_calls_offline']==12
 assert p['reviewed_reflexive_calls_offline']==1 and p['reviewed_subject_getter_calls_offline']==6 and p['reviewed_historian_getter_calls_offline']==14
 assert p['unresolved_count']==186 and p['unresolved_count']+1+6+14+12==219
 assert p['pending_windows_ui_java_getter_calls']==219 and p['shared_her_conflict_open'] is True
 assert p['reviewed_rules_rows_offline']==p['pending_windows_ui_rules_rows']==153
 assert p['removed_visible_gender_variable_refs']==260 and p['latest_rules_review_ledger']=='docs/RULES_PRONOUN_REVIEW_1039.json'
 s=g['story_contexts'];assert s['status']=='in_progress' and s['reviewed_offline']==81 and s['pending_windows_ui']==81
 t=g['draft_semantics'];assert t['status']=='blocked' and t['total_draft_rows']==3658 and t['reviewed_offline']==122 and t['unresolved_count']==3536
 assert t['gameplay_unverified_count']==3696 and t['new_literal_count']==38 and t['review_ledger']=='docs/API_SEMANTIC_REVIEW_1040.json'
 assert t['reviewed_offline']+t['unresolved_count']==3658
 assert g['text_completeness']['status']=='in_progress' and g['windows_runtime']['status']=='blocked'
 assert reviewcheck(root,prior,ledger)['reviewed_offline']==122
 assert mapcheck(root)['gendered_snippets']==24
 return {'release_11_allowed':False,'getter_reviewed_offline':33,'getter_remaining_offline':186,'jvm_getters_pending_windows':219,'api_reviewed_offline':122,'api_remaining_semantic':3536,'rules_rows_pending_windows':153,'story_calls_pending_windows':81}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True);p.add_argument('--prior-ledger',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 q=p.parse_args();print(json.dumps(verify(q.worktree,q.gates,q.prior_ledger,q.ledger),indent=2))
