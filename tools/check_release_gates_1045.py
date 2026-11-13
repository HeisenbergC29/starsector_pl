#!/usr/bin/env python3
"""Fail closed on 1.1 while auditing verified 1.0.45 dialogue changes."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1045 import check,reverse_bytes
from apply_1045 import patch_bytes

OLD_LEDGERS=(
 'docs/RULES_PRONOUN_REVIEW_1034.json',
 'docs/RULES_PRONOUN_REVIEW_1035.json',
 'docs/RULES_PRONOUN_REVIEW_1039.json',
 'docs/RULES_POSSESSIVE_REVIEW_1043.json',
 'docs/RULES_GENDER_REVIEW_1044.json',
)

def validate(root, gates_file, ledger_file, prior_ledger_paths=None):
    root=Path(root)
    ledger_file=Path(ledger_file)
    old=prior_ledger_paths or [Path(x) for x in OLD_LEDGERS]
    summary=check(root,prior_ledgers=old)
    blob=(root/'mod/data/campaign/rules.csv').read_bytes()
    _,report,details=patch_bytes(reverse_bytes(blob))
    ledger=json.loads(ledger_file.read_text('utf8'))
    if ledger!={'stats':report,'approved':details}:
        raise ValueError('Unverifiable or modified 1.0.45 review ledger')
    gates=json.loads(Path(gates_file).read_text('utf8'))
    if gates.get('schema_version')!=1 or gates.get('target_version')!='1.1':
        raise ValueError('Incorrect gate metadata')
    d={x['id']:x for x in gates.get('gates',[])}
    req={'story_contexts','pronoun_contexts','draft_semantics','numeric_quantities',
         'punctuation_regression','rules_possessives','rules_gender_neutral_1044',
         'rules_gender_neutral_1045','text_completeness','windows_runtime'}
    if set(d)!=req or any(x['status']=='completed' for x in d.values()):
        raise ValueError('Premature 1.1 release claim')
    pr=d['pronoun_contexts']
    for key,val in {'total_jvm_getter_calls':219,'unresolved_count':186,
        'pending_windows_ui_java_getter_calls':219,
        'reviewed_rules_rows_offline':253,
        'pending_windows_ui_rules_rows':253,
        'removed_visible_gender_variable_refs':420}.items():
        if pr.get(key)!=val:raise ValueError(('Incorrect review counter',key))
    if pr.get('shared_her_conflict_open') is not True or pr.get('latest_rules_review_ledger')!='docs/RULES_GENDER_REVIEW_1045.json':
        raise ValueError('Unresolved JVM pronoun conflict was incorrectly closed')
    new=d['rules_gender_neutral_1045']
    for key,val in {'reviewed_rows_offline':44,'fragments_changed':80,
                    'removed_visible_gender_variable_refs':93,'pending_windows_ui_rows':44}.items():
        if new.get(key)!=val:raise ValueError(('Wrong new review counter',key))
    if new['status']!='in_progress':raise ValueError('Visual review prematurely completed')
    dr=d['draft_semantics']
    if (dr['total_draft_rows'],dr['reviewed_offline'],dr['unresolved_count'])!=(3658,122,3536) or dr['status']!='blocked':
        raise ValueError('API review incorrectly closed')
    if d['story_contexts']['pending_windows_ui']!=81 or d['windows_runtime']['native_gameplay_tested'] is not False:
        raise ValueError('Missing native Windows gameplay proof')
    return {'version':'1.0.45','new_rows':44,'new_edits':80,'removed_gender_vars':93,
            'all_offline_reviewed_dialogue_rows':253,
            'cumulative_removed_gender_references':420,
            'unreviewed_java_getters':186,
            'unreviewed_historical_api_translations':3536,
            'remaining_gates':len(d),'version_1_1_still_blocked':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--gates',type=Path,required=True)
    p.add_argument('--ledger',type=Path,required=True)
    p.add_argument('--prior-ledger',type=Path,action='append')
    a=p.parse_args();print(json.dumps(validate(a.worktree,a.gates,a.ledger,a.prior_ledger),indent=2))
