#!/usr/bin/env python3
"""1.0.53 fail-closed 1.1 release gates, OBF-only recovery translations."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1053 import check
from verify_review_1052 import check as review_check

PRIOR_IDS={'story_contexts','pronoun_contexts','draft_semantics','rules_possessives',
 'rules_gender_neutral_1044','rules_gender_neutral_1045','numeric_quantities',
 'punctuation_regression','api_contexts_1046','api_numeric_1047','api_numeric_1048',
 'api_grammar_1049','api_time_fragments_1050','personality_ui_1051','bar_shared_her_1052',
 'text_completeness','windows_runtime'}
IDS=PRIOR_IDS|{'obf_recovery_1053'}

def audit(root,gates,previous,ledger):
 doc=json.loads(Path(gates).read_text('utf8')); rows=doc.get('gates',[])
 D={r['id']:r for r in rows}
 if doc.get('target_version')!='1.1' or doc.get('schema_version')!=1 or len(rows)!=18 or set(D)!=IDS:
  raise ValueError('1.1 gate set changed')
 if any(r['status']=='completed' for r in rows):raise ValueError('Premature completed 1.1 gate')
 u=D['pronoun_contexts'];d=D['draft_semantics'];w=D['windows_runtime'];rec=D['obf_recovery_1053']
 if (u.get('unresolved_count'),u.get('total_jvm_getter_calls'),u.get('shared_her_conflict_open'),u.get('shared_her_pending_native_windows_validation'))!=(186,219,False,True):
  raise ValueError('Previous getter review status falsified')
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'),d.get('review_ledger'),d.get('status'))!=(3658,324,3334,'docs/API_SEMANTIC_REVIEW_1052.json','blocked'):
  raise ValueError('History ledger cannot be auto-reviewed by OBF-only work')
 if (rec.get('new_obf_entries'),rec.get('total_obf_entries'),rec.get('changed_classes'),rec.get('pending_windows_ui'),rec.get('status'))!=(3,3537,1,3,'in_progress'):
  raise ValueError('OBF recovery inventory falsified')
 if rec.get('executable_java_bytecode_changed') is not False or rec.get('api_map_changed') is not False:
  raise ValueError('Unexpected OBF/API source drift')
 if (w.get('status'),w.get('native_gameplay_tested'))!=('blocked',False) or D['text_completeness']['status']!='in_progress':
  raise ValueError('Windows or full text coverage falsely declared complete')
 if D['bar_shared_her_1052']['reviewed_gender_getter_callsites']!=13 or D['personality_ui_1051']['jvm_ldc_operand_changes']!=2:
  raise ValueError('Prior JVM proof missing')
 check(root)
 if review_check(root,previous,ledger)['total_reviewed']!=324:raise ValueError('Historical API review altered')
 return {'release':'1.0.53','gate_count':18,'target_1_1_blocked':True,
  'recovery_obf_string_rows_verified':3,'active_obf_rows':3537,'historical_api_offline_reviewed':324,
  'unreviewed_api_history':3334,'unresolved_other_getter_calls':186,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);a.add_argument('--gates',type=Path,required=True)
 a.add_argument('--previous',type=Path,required=True);a.add_argument('--ledger',type=Path,required=True)
 p=a.parse_args();print(json.dumps(audit(p.worktree,p.gates,p.previous,p.ledger),indent=2))
