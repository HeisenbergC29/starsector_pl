#!/usr/bin/env python3
"""Refuse premature completion, wrong counts and ledger forgery for release 1.1."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1039 import check

def run(root,gates,l34,l35,l39,api):
    base=json.loads(gates.read_text('utf8'))
    assert check(root,gates,l34,l35,l39,api)['release_allowed'] is False
    def guard(modify):
        j=copy.deepcopy(base);d={x['id']:x for x in j['gates']};modify(d)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'gates.json';p.write_text(json.dumps(j))
            try:check(root,p,l34,l35,l39,api)
            except (AssertionError,ValueError,KeyError):return
            raise AssertionError('Improperly completed 1.1 gate accepted')
    tests=[
        lambda x:x['windows_runtime'].update(status='completed'),
        lambda x:x['text_completeness'].update(status='completed'),
        lambda x:x['story_contexts'].update(pending_windows_ui=0),
        lambda x:x['story_contexts'].update(reviewed_offline=80),
        lambda x:x['pronoun_contexts'].update(unresolved_count=197),
        lambda x:x['pronoun_contexts'].update(pending_windows_ui_java_getter_calls=0),
        lambda x:x['pronoun_contexts'].update(shared_her_conflict_open=False),
        lambda x:x['pronoun_contexts'].update(reviewed_rules_rows_offline=154),
        lambda x:x['pronoun_contexts'].update(reviewed_rules_rows_offline=91),
        lambda x:x['pronoun_contexts'].update(removed_visible_gender_variable_refs=259),
        lambda x:x['pronoun_contexts'].update(pending_windows_ui_rules_rows=0),
        lambda x:x['draft_semantics'].update(reviewed_offline=105),
        lambda x:x['draft_semantics'].update(unresolved_count=0),
        lambda x:x['draft_semantics'].update(gameplay_unverified_count=0),
    ]
    for t in tests:guard(t)
    return {'negative_release_gate_cases':len(tests),'release_1_1_blocked':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True);p.add_argument('--ledger34',type=Path,required=True);p.add_argument('--ledger35',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--api-ledger',type=Path,required=True)
    a=p.parse_args();print(json.dumps(run(a.worktree,a.gates,a.ledger34,a.ledger35,a.ledger,a.api_ledger),indent=2))
