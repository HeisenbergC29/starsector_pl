#!/usr/bin/env python3
"""Assert 1.1 remains blocked and 1.0.44 reviewed dialogue counts are authentic."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1044 import patch_bytes
from verify_1044 import check,reverse_bytes

def validate(root,gates_path,ledger_path):
    root=Path(root);g=json.loads(Path(gates_path).read_text('utf8'))
    if g.get('target_version')!='1.1' or g.get('schema_version')!=1:raise ValueError('Wrong gate set')
    gates={v['id']:v for v in g['gates']}
    req={'story_contexts','pronoun_contexts','draft_semantics','numeric_quantities','punctuation_regression','rules_possessives','rules_gender_neutral_1044','text_completeness','windows_runtime'}
    if set(gates)!=req or any(x['status']=='completed' for x in gates.values()):raise ValueError('Premature 1.1 release')
    pr=gates['pronoun_contexts']
    assert pr['unresolved_count']==186 and pr['reviewed_rules_rows_offline']==209
    assert pr['removed_visible_gender_variable_refs']==327 and pr['pending_windows_ui_rules_rows']==209
    assert pr['total_jvm_getter_calls']==219 and pr['pending_windows_ui_java_getter_calls']==219
    assert pr['shared_her_conflict_open'] is True
    draft=gates['draft_semantics']
    assert (draft['total_draft_rows'],draft['reviewed_offline'],draft['unresolved_count'])==(3658,122,3536)
    story=gates['story_contexts'];assert story['reviewed_offline']==story['pending_windows_ui']==81
    new=gates['rules_gender_neutral_1044']
    assert (new['reviewed_rows_offline'],new['fragments_changed'],new['removed_visible_gender_variable_refs'],new['pending_windows_ui_rows'])==(25,30,31,25)
    assert gates['windows_runtime']['native_gameplay_tested'] is False
    stats=check(root)
    before=reverse_bytes((root/'mod/data/campaign/rules.csv').read_bytes())
    _,_,expected=patch_bytes(before)
    ledger=json.loads(Path(ledger_path).read_text('utf8'))
    if ledger.get('stats')!={k:stats[k] for k in ['version','rows_changed','fragments_changed','gender_references_removed','before_sha256','after_sha256']} or ledger.get('approved')!=expected:
        raise ValueError('Unauthenticated review ledger')
    return {'release':'1.0.44','gates':len(gates),'release_1_1_blocked':True,'reviewed_dialogue_rows_total':209,'pronoun_placeholders_removed_total':327,'new_reviewed_rows':25,'new_removed_placeholders':31,'getter_calls_remaining':186,'api_semantics_remaining':3536}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path);ap.add_argument('--gates',type=Path,required=True);ap.add_argument('--ledger',type=Path,required=True)
    a=ap.parse_args();print(json.dumps(validate(a.worktree,a.gates,a.ledger),indent=2))