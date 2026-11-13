#!/usr/bin/env python3
"""Fail closed on all remaining 1.1 quality gates; 1.0.43 only reviews 36 phrases."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1043 import check
from verify_review_1043 import verify

LEDGERS=['docs/RULES_PRONOUN_REVIEW_1034.json','docs/RULES_PRONOUN_REVIEW_1035.json','docs/RULES_PRONOUN_REVIEW_1039.json','docs/RULES_POSSESSIVE_REVIEW_1043.json']

def validate_gates(root,gate_path,ledger_paths=None):
    root=Path(root);g=json.loads(Path(gate_path).read_text(encoding='utf8'))
    if g['target_version']!='1.1' or g['schema_version']!=1:raise ValueError('Wrong release target/schema')
    gates={e['id']:e for e in g['gates']}
    names={'story_contexts','pronoun_contexts','draft_semantics','numeric_quantities','punctuation_regression','rules_possessives','text_completeness','windows_runtime'}
    if set(gates)!=names or any(v['status']=='completed' for v in gates.values()):raise ValueError('Cannot mark unfinished 1.1 gate complete')
    r=gates['pronoun_contexts']
    if any(r.get(k)!=n for k,n in {'unresolved_count':186,'reviewed_rules_rows_offline':184,'removed_visible_gender_variable_refs':296,'pending_windows_ui_rules_rows':184,'total_jvm_getter_calls':219,'pending_windows_ui_java_getter_calls':219,'reviewed_base_get_commodity_man_or_woman_calls_offline':12}.items()):raise ValueError('Pronoun or rules counts falsified')
    if r['shared_her_conflict_open'] is not True or r['latest_rules_review_ledger']!=LEDGERS[-1]:raise ValueError('Shared her or ledger falsely closed')
    if r['reviewed_reflexive_calls_offline']+r['reviewed_subject_getter_calls_offline']+r['reviewed_historian_getter_calls_offline']+r['reviewed_base_get_commodity_man_or_woman_calls_offline']!=33:raise ValueError('Incorrect JVM callsites reviewed')
    s=gates['story_contexts'];assert s['reviewed_offline']==s['pending_windows_ui']==81 and s['status']=='in_progress'
    d=gates['draft_semantics'];assert (d['total_draft_rows'],d['reviewed_offline'],d['unresolved_count'])==(3658,122,3536) and d['status']=='blocked'
    q=gates['rules_possessives'];assert q['reviewed_offline']==q['pending_windows_ui']==36 and q['reviewed_rows_offline']==31 and q['status']=='in_progress'
    n=gates['numeric_quantities'];assert n['reviewed_offline']==n['pending_windows_ui']==77
    p=gates['punctuation_regression'];assert p['reviewed_offline']==p['pending_windows_ui']==15
    assert gates['text_completeness']['status']=='in_progress'
    assert gates['windows_runtime']['native_gameplay_tested'] is False and gates['windows_runtime']['status']=='blocked'
    assert check(root)['modified_rows']==31
    ledgers=ledger_paths or [Path(gate_path).parent/Path(p).name for p in LEDGERS]
    counts=verify(root,ledgers)
    return {'version':'1.0.43','gates':len(gates),'all_release_1_1_gates_still_open':True,**counts,'remaining_getter_callsite_reviews':186,'remaining_api_semantic_reviews':3536}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True)
    p.add_argument('--ledger34',type=Path);p.add_argument('--ledger35',type=Path);p.add_argument('--ledger39',type=Path);p.add_argument('--ledger',type=Path)
    a=p.parse_args();ls=[a.ledger34,a.ledger35,a.ledger39,a.ledger]
    print(json.dumps(validate_gates(a.worktree,a.gates,None if all(x is None for x in ls) else ls),indent=2))
