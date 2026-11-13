#!/usr/bin/env python3
"""Fail-closed 1.1 gates after Starsector PL 1.0.47 (NOT complete)."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1047 import check
from verify_review_1047 import verify

EXPECTED_IDS={'story_contexts','pronoun_contexts','draft_semantics','rules_possessives',
 'rules_gender_neutral_1044','rules_gender_neutral_1045','numeric_quantities',
 'punctuation_regression','api_contexts_1046','api_numeric_1047','text_completeness','windows_runtime'}

def audit(root,gates,previous,ledger,fixture=False):
    g=json.loads(Path(gates).read_text(encoding='utf8'))
    if g['schema_version']!=1 or g['target_version']!='1.1':raise ValueError('Wrong gate schema/version')
    mapped={x['id']:x for x in g['gates']}
    if len(g['gates'])!=12 or set(mapped)!=EXPECTED_IDS or any(x['status']=='completed' for x in mapped.values()):
        raise ValueError('Unreviewed release gate closed or missing')
    p=mapped['pronoun_contexts']
    expected={'unresolved_count':186,'total_jvm_getter_calls':219,
              'reviewed_rules_rows_offline':253,'removed_visible_gender_variable_refs':420,
              'pending_windows_ui_rules_rows':253,'pending_windows_ui_java_getter_calls':219}
    if any(p.get(k)!=v for k,v in expected.items()) or p['shared_her_conflict_open'] is not True:
        raise ValueError('Pronoun counts or shared her gate falsified')
    d=mapped['draft_semantics']
    if (d['total_draft_rows'],d['reviewed_offline'],d['unresolved_count'])!=(3658,180,3478):
        raise ValueError('Review counters wrong')
    if d['review_ledger']!='docs/API_SEMANTIC_REVIEW_1047.json' or d['status']!='blocked':
        raise ValueError('Draft semantics closed early')
    r=mapped['api_numeric_1047']
    if r['status']!='in_progress' or (r['corrected_api_rows'],r['changed_classes'],r['pending_windows_ui'])!=(14,11,14):
        raise ValueError('Wrong numeric UI gate')
    if mapped['api_contexts_1046']['reviewed_offline']!=16:raise ValueError('Prior API fixes lost')
    if mapped['numeric_quantities']['reviewed_offline']!=77:raise ValueError('Prior numeric count lost')
    if mapped['story_contexts']['pending_windows_ui']!=81:raise ValueError('Story native test falsified')
    if mapped['windows_runtime']['native_gameplay_tested'] is not False or mapped['windows_runtime']['status']!='blocked':
        raise ValueError('Native Windows gameplay not verified')
    v=check(root,strict_go=not fixture);re=verify(root,previous,ledger)
    if v['changes']!=14 or re['new_offline_reviews']!=38:raise ValueError('Release source review mismatch')
    return {'release':'1.0.47','gates':len(g['gates']),'target_1_1_blocked':True,
            'api_numeric_texts_fixed_offline':14,'api_semantic_review_total':180,
            'api_historical_review_remaining':3478,'unreviewed_java_getter_calls':186,
            'native_windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--ledger',type=Path,required=True);p.add_argument("--fixture",action="store_true");a=p.parse_args()
    print(json.dumps(audit(a.worktree,a.gates,a.previous,a.ledger,a.fixture),indent=2))
