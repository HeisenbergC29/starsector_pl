#!/usr/bin/env python3
"""Enforce unfinished 1.1 while verifying v1.0.54 review integrity."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1054 import check
from verify_review_1054 import check as check_review
IDS={'story_contexts','pronoun_contexts','draft_semantics','rules_possessives',
 'rules_gender_neutral_1044','rules_gender_neutral_1045','numeric_quantities',
 'punctuation_regression','api_contexts_1046','api_numeric_1047','api_numeric_1048',
 'api_grammar_1049','api_time_fragments_1050','personality_ui_1051','bar_shared_her_1052',
 'obf_recovery_1053','api_dynamic_fragments_1054','text_completeness','windows_runtime'}

def audit(root,gates,previous,ledger):
 d=json.loads(Path(gates).read_text('utf8'));gs=d.get('gates',[]);g={x['id']:x for x in gs}
 if d.get('schema_version')!=1 or d.get('target_version')!='1.1' or len(gs)!=19 or set(g)!=IDS or any(x['status']=='completed' for x in gs):
  raise ValueError('1.1 gates falsely complete/altered')
 if (g['draft_semantics'].get('total_draft_rows'),g['draft_semantics'].get('reviewed_offline'),g['draft_semantics'].get('unresolved_count'),g['draft_semantics'].get('review_ledger'),g['draft_semantics'].get('status'))!=(3658,343,3315,'docs/API_SEMANTIC_REVIEW_1054.json','blocked'):
  raise ValueError('Semantics release gate falsely closed')
 if (g['pronoun_contexts'].get('unresolved_count'),g['pronoun_contexts'].get('total_jvm_getter_calls'),g['pronoun_contexts'].get('shared_her_conflict_open'),g['pronoun_contexts'].get('shared_her_pending_native_windows_validation'))!=(186,219,False,True):
  raise ValueError('Pronoun context audits falsely closed')
 q=g['api_dynamic_fragments_1054']
 if (q.get('new_api_rows'),q.get('corrected_api_rows'),q.get('changed_classes'),q.get('pending_windows_ui'),q['status'])!=(7,6,6,13,'in_progress'):
  raise ValueError('Dynamic UI release gate falsified')
 rec=g['obf_recovery_1053']
 if (rec.get('new_obf_entries'),rec.get('total_obf_entries'),rec.get('changed_classes'))!=(3,3537,1):raise ValueError('Previous OBF gate changed')
 if (g['windows_runtime'].get('native_gameplay_tested'),g['windows_runtime']['status'],g['text_completeness']['status'])!=(False,'blocked','in_progress'):
  raise ValueError('Native Windows/full localization cannot be completed offline')
 if g['personality_ui_1051'].get('jvm_ldc_operand_changes')!=2 or g['bar_shared_her_1052'].get('reviewed_gender_getter_callsites')!=13:
  raise ValueError('Historical contextual evidence removed')
 if check(root)['api_map_entries']!=5290 or check_review(root,previous,ledger)['total_reviewed']!=343:
  raise ValueError('Map and semantic history mismatch')
 return {'working_release':'1.0.54','gates':len(gs),'target_1_1_blocked':True,
  'historical_api_reviewed_offline':343,'historical_api_unreviewed':3315,
  'unreviewed_gender_getter_contexts':186,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);a=p.parse_args()
 print(json.dumps(audit(a.worktree,a.gates,a.previous,a.ledger),indent=2))
