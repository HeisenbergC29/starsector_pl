#!/usr/bin/env python3
"""Fail-closed 1.1 gate: 153 offline-reviewed rules rows are NOT Windows gameplay."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_review_1039 import verify as verify_review
from verify_1039 import verify as verify_data

def check(root,gates,ledger34,ledger35,ledger39,api_ledger):
    j=json.loads(gates.read_text('utf8'))
    assert j['schema_version']==1 and j['target_version']=='1.1'
    g={x['id']:x for x in j['gates']}
    assert set(g)=={'story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime'}
    assert all(x['status']!='completed' for x in g.values())
    s=g['story_contexts']
    assert s['status']=='in_progress' and s['reviewed_offline']==81 and s['pending_windows_ui']==81
    p=g['pronoun_contexts']
    assert p['status']=='blocked' and p['unresolved_count']==198 and p['total_jvm_getter_calls']==219
    assert p['reviewed_reflexive_calls_offline']==1 and p['reviewed_subject_getter_calls_offline']==6 and p['reviewed_historian_getter_calls_offline']==14
    assert p['pending_windows_ui_java_getter_calls']==219 and p['shared_her_conflict_open'] is True
    assert p['reviewed_rules_rows_offline']==153 and p['pending_windows_ui_rules_rows']==153 and p['removed_visible_gender_variable_refs']==260
    assert p['latest_rules_review_ledger']=='docs/RULES_PRONOUN_REVIEW_1039.json'
    proof=verify_review(root,ledger34,ledger35,ledger39)
    assert proof['cumulative_reviewed_rows']==153 and proof['cumulative_removed']==260
    data=verify_data(root);assert data['changed_rows']==62 and data['removed_pronoun_placeholders']==77
    api=json.loads(api_ledger.read_text('utf8'))
    assert api['installed_version']=='1.0.38' and len(api['reviewed'])==104
    d=g['draft_semantics']
    assert d['status']=='blocked' and d['total_draft_rows']==3658 and d['reviewed_offline']==104 and d['unresolved_count']==3554
    assert d['gameplay_unverified_count']==3693 and d['new_literal_count']==35 and d['review_ledger']=='docs/API_SEMANTIC_REVIEW_1038.json'
    assert d['reviewed_offline']+d['unresolved_count']==d['total_draft_rows']
    assert g['text_completeness']['status']=='in_progress' and g['windows_runtime']['status']=='blocked'
    return {'installed_version':'1.0.39','target':'1.1','release_allowed':False,'getters_still_pending_offline':198,'jvm_getters_pending_windows':219,'reviewed_rules_rows_offline':153,'rules_rows_pending_windows':153,'historical_api_pending_semantic':3554}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);a.add_argument('--gates',required=True,type=Path)
    a.add_argument('--ledger34',type=Path,required=True);a.add_argument('--ledger35',type=Path,required=True)
    a.add_argument('--ledger',type=Path,required=True);a.add_argument('--api-ledger',type=Path,required=True)
    o=a.parse_args();print(json.dumps(check(o.worktree,o.gates,o.ledger34,o.ledger35,o.ledger,o.api_ledger),indent=2))
