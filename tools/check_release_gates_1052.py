#!/usr/bin/env python3
"""Fail-closed verification: shared her fixed offline, rest of 1.1 remains blocked."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1052 import check
from verify_review_1052 import check as check_reviews
GATE_IDS={'story_contexts','pronoun_contexts','draft_semantics','rules_possessives',
 'rules_gender_neutral_1044','rules_gender_neutral_1045','numeric_quantities','punctuation_regression',
 'api_contexts_1046','api_numeric_1047','api_numeric_1048','api_grammar_1049',
 'api_time_fragments_1050','personality_ui_1051','bar_shared_her_1052',
 'text_completeness','windows_runtime'}

def audit(root,gates,previous,ledger):
 g=json.loads(Path(gates).read_text('utf8'));rows=g.get('gates',[]);D={x['id']:x for x in rows}
 if g.get('schema_version')!=1 or g.get('target_version')!='1.1' or len(rows)!=17 or set(D)!=GATE_IDS or any(x['status']=='completed' for x in rows):
  raise ValueError('Illegal complete/missing 1.1 release gate')
 p=D['pronoun_contexts'];d=D['draft_semantics'];w=D['windows_runtime'];q=D['bar_shared_her_1052']
 if (p.get('unresolved_count'),p.get('total_jvm_getter_calls'),p.get('shared_her_conflict_open'))!=(186,219,False):
  raise ValueError('Cannot reclassify more unresolved getters or claim new conflict')
 if (p.get('base_bar_shared_her_resolved_offline_1052'),p.get('shared_her_pending_native_windows_validation'),p.get('base_bar_gender_getter_callsites_reviewed_1052'))!=(True,True,13):
  raise ValueError('Missing proof/pending UI for shared feminine her')
 if (p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(253,420):
  raise ValueError('Previous rules reviews altered')
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'),d.get('review_ledger'))!=(3658,324,3334,'docs/API_SEMANTIC_REVIEW_1052.json'):
  raise ValueError('Falsified historical API counters')
 if d['status']!='blocked':raise ValueError('Historical API review cannot be completed')
 if (q.get('new_api_rows'),q.get('corrected_existing_api_rows'),q.get('modified_java_classes'))!=(14,10,3):
  raise ValueError('Altered bar literal inventory')
 if (q.get('shared_her_resolved_offline'),q.get('new_executable_java_bytecode_changes'),q.get('reviewed_gender_getter_callsites'),q.get('pending_windows_ui'),q.get('status'))!=(True,0,13,24,'in_progress'):
  raise ValueError('Bar grammar review or JVM bytecode claims falsified')
 if D['personality_ui_1051'].get('jvm_ldc_operand_changes')!=2:raise ValueError('Prior tiny JVM exception lost')
 if D['api_time_fragments_1050'].get('added_api_rows')!=8:raise ValueError('Prior duration strings lost')
 if (w.get('status'),w.get('native_gameplay_tested'))!=('blocked',False):raise ValueError('Windows gameplay falsely confirmed')
 if D['story_contexts'].get('pending_windows_ui')!=81 or D['text_completeness']['status']!='in_progress':raise ValueError('Release 1.1 prematurely marked complete')
 a=check(root);b=check_reviews(root,previous,ledger)
 if a['new_context_literals']!=14 or b['total_reviewed']!=324:raise ValueError('Inconsistent 1.0.52 map/review ledger')
 return {'release':'1.0.52','gate_count':17,'target_1_1_blocked':True,
  'shared_her_conflict_resolved_offline_only':True,'historical_reviewed':324,'historical_pending':3334,
  'unreviewed_getter_calls_conservatively_retained':186,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True)
 p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.ledger),indent=2))
