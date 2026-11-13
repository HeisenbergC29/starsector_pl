#!/usr/bin/env python3
"""Fail closed on unfinished 1.1 completion for the 1.0.48 working release."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1048 import check
from verify_review_1048 import verify

GATE_IDS={'story_contexts','pronoun_contexts','draft_semantics','rules_possessives',
 'rules_gender_neutral_1044','rules_gender_neutral_1045','numeric_quantities',
 'punctuation_regression','api_contexts_1046','api_numeric_1047','api_numeric_1048',
 'text_completeness','windows_runtime'}

def audit(root,gates,previous,ledger):
    raw=json.loads(Path(gates).read_text('utf8'))
    if raw.get('schema_version')!=1 or raw.get('target_version')!='1.1':raise ValueError('Invalid release gate schema')
    gs=raw.get('gates',[]);items={x['id']:x for x in gs}
    if len(gs)!=13 or set(items)!=GATE_IDS or any(x['status']=='completed' for x in gs):
        raise ValueError('Release gates missing, duplicated or prematurely closed')
    p=items['pronoun_contexts'];d=items['draft_semantics'];w=items['windows_runtime']
    if (p.get('unresolved_count'),p.get('total_jvm_getter_calls'),p.get('shared_her_conflict_open'))!=(186,219,True):
        raise ValueError('Java pronoun problem cannot be marked fixed')
    if (p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(253,420):
        raise ValueError('Historical rules reviews changed')
    if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'))!=(3658,203,3455):
        raise ValueError('Historical API review counters falsified')
    if d.get('review_ledger')!='docs/API_SEMANTIC_REVIEW_1048.json' or d['status']!='blocked':
        raise ValueError('Semantic review blocked gate invalid')
    q=items['api_numeric_1048']
    if (q.get('corrected_api_rows'),q.get('changed_classes'),q.get('pending_windows_ui'))!=(29,19,29) or q['status']!='in_progress':
        raise ValueError('Review/gate numerical mismatch')
    if items['api_numeric_1047']['corrected_api_rows']!=14 or items['api_contexts_1046']['reviewed_offline']!=16:
        raise ValueError('Prior release gate lost')
    if w.get('native_gameplay_tested') is not False or w.get('status')!='blocked':
        raise ValueError('No native Windows gameplay done')
    if items['story_contexts']['pending_windows_ui']!=81 or items['text_completeness']['status']!='in_progress':
        raise ValueError('Full 1.1 cannot be marked finished')
    src=check(root);reviews=verify(root,previous,ledger)
    if src['corrected_api_rows']!=29 or reviews['new_reviewed']!=23:
        raise ValueError('API map/reviews mismatch')
    return {'release':'1.0.48','gates':13,'target_1_1_blocked':True,
            'api_numeric_texts_fixed_offline':29,'historical_api_offline_reviewed':203,
            'historical_api_unreviewed':3455,'unreviewed_java_getter_calls':186,
            'native_windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path)
    p.add_argument('--previous',required=True,type=Path);p.add_argument('--ledger',required=True,type=Path)
    a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.ledger),indent=2))
