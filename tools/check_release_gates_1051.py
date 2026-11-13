#!/usr/bin/env python3
"""Fail-closed 1.1 gates when a two-operand UI bytecode exception is used."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1051 import check
from verify_review_1051 import verify
GATE_IDS={'story_contexts','pronoun_contexts','draft_semantics','rules_possessives',
 'rules_gender_neutral_1044','rules_gender_neutral_1045','numeric_quantities',
 'punctuation_regression','api_contexts_1046','api_numeric_1047','api_numeric_1048',
 'api_grammar_1049','api_time_fragments_1050','personality_ui_1051',
 'text_completeness','windows_runtime'}
def audit(root,gates,previous,ledger):
 obj=json.loads(Path(gates).read_text('utf8'));gs=obj.get('gates',[])
 items={a['id']:a for a in gs}
 if obj.get('schema_version')!=1 or obj.get('target_version')!='1.1' or len(gs)!=16 or set(items)!=GATE_IDS or any(x['status']=='completed' for x in gs):raise ValueError('Release 1.1 falsely completed')
 p,d,w=items['pronoun_contexts'],items['draft_semantics'],items['windows_runtime']
 if (p.get('unresolved_count'),p.get('total_jvm_getter_calls'),p.get('shared_her_conflict_open'))!=(186,219,True):raise ValueError('Shared her unresolved')
 if (p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(253,420):raise ValueError('Historical dialog reviews altered')
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'))!=(3658,314,3344):raise ValueError('Historical API review count incorrect')
 if d.get('review_ledger')!='docs/API_SEMANTIC_REVIEW_1051.json' or d.get('status')!='blocked':raise ValueError('Historical API review gate incomplete')
 q=items['personality_ui_1051']
 if (q.get('corrected_ui_rows'),q.get('changed_classes'),q.get('jvm_ldc_operand_changes'),q.get('pending_windows_ui'))!=(2,1,2,2):raise ValueError('JVM UI exception scope mismatch')
 if q.get('technical_identity_constants_preserved') is not True or q.get('status')!='in_progress':raise ValueError('Personality UI proof absent')
 if items['api_time_fragments_1050'].get('added_api_rows')!=8:raise ValueError('Previous 1050 gate lost')
 if w.get('status')!='blocked' or w.get('native_gameplay_tested') is not False:raise ValueError('Native Windows game not yet tested')
 if items['story_contexts'].get('pending_windows_ui')!=81 or items['text_completeness']['status']!='in_progress':raise ValueError('Whole-game translation unverified')
 a=check(root);b=verify(root,previous,ledger)
 if a['intentional_ldc_operand_changes']!=2 or b['total_history_reviewed']!=314:raise ValueError('Map and review evidence inconsistent')
 return {'release':'1.0.51','gates':16,'target_1_1_blocked':True,'reviewed_history':314,'history_pending':3344,
   'display_only_jvm_operand_exception_count':2,'technical_personality_ids_preserved':True,
   'java_getter_sites_unreviewed':186,'shared_her_conflict_open':True,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.ledger),indent=2))
