#!/usr/bin/env python3
"""Fail closed on release 1.1; certify only 1.0.46 offline improvements."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1046 import check as verify
from verify_review_1046 import verify as review

GATE_IDS={'story_contexts','pronoun_contexts','draft_semantics','rules_possessives',
          'rules_gender_neutral_1044','rules_gender_neutral_1045','numeric_quantities',
          'punctuation_regression','api_contexts_1046','text_completeness','windows_runtime'}

def validate(root,gatepath,prev,ledger,strict_go=True):
    root=Path(root)
    data=json.loads(Path(gatepath).read_text('utf8'))
    if data['target_version']!='1.1' or data['schema_version']!=1:raise ValueError('Wrong release metadata')
    g={x['id']:x for x in data['gates']}
    if set(g)!=GATE_IDS or len(g)!=len(data['gates']):raise ValueError('Invalid gate set')
    if any(x['status']=='completed' for x in g.values()):raise ValueError('Premature 1.1 completion')
    p=g['pronoun_contexts']
    if p['unresolved_count']!=186 or p['total_jvm_getter_calls']!=219 or p['shared_her_conflict_open'] is not True:
        raise ValueError('Pronoun getter debt falsified')
    if p['reviewed_rules_rows_offline']!=253 or p['removed_visible_gender_variable_refs']!=420:
        raise ValueError('1.0.45 dialog counter modified')
    d=g['draft_semantics']
    if (d['total_draft_rows'],d['reviewed_offline'],d['unresolved_count'])!=(3658,142,3516):
        raise ValueError('Historical API semantic debt incorrect')
    if d['status']!='blocked' or d['review_ledger']!='docs/API_SEMANTIC_REVIEW_1046.json':
        raise ValueError('Review ledger reference invalid')
    n=g['api_contexts_1046']
    if (n['reviewed_offline'],n['pending_windows_ui'],n['changed_classes'])!=(16,16,8) or n['status']!='in_progress':
        raise ValueError('1.0.46 numeric/context review not tracked')
    if g['story_contexts']['pending_windows_ui']!=81 or g['numeric_quantities']['pending_windows_ui']!=77:
        raise ValueError('Older Windows test obligations erased')
    if g['windows_runtime']['native_gameplay_tested'] is not False or g['windows_runtime']['status']!='blocked':
        raise ValueError('Unverified Windows test marked complete')
    if g['text_completeness']['status']!='in_progress':raise ValueError('Game completeness falsely claimed')
    vr=verify(root,strict_go=strict_go)
    rr=review(root,prev,ledger)
    if vr['corrected_api_map_rows']!=13 or vr['new_api_map_rows']!=3 or rr['remaining_historical_api_reviews']!=3516:
        raise ValueError('Verification counters disagree')
    return {'version':'1.0.46','release_1_1_blocked':True,'open_gates':len(GATE_IDS),
            'corrected_api_literal_translations':13,'newly_localized_dynamic_fragments':3,'new_historical_api_semantic_reviews':20,
            'historical_api_reviewed_total':142,'historical_api_reviews_remaining':3516,
            'java_pronoun_callsite_reviews_remaining':186,'windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--ledger',type=Path,required=True);p.add_argument('--fixture',action='store_true')
    a=p.parse_args();print(json.dumps(validate(a.worktree,a.gates,a.previous,a.ledger,strict_go=not a.fixture),indent=2))
