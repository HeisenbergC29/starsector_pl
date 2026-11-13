#!/usr/bin/env python3
"""Block falsely completed 1.1 release while verifying 1.0.50's reviewed time fragments."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1050 import check
from verify_review_1050 import verify
GATE_IDS={'story_contexts','pronoun_contexts','draft_semantics','rules_possessives',
 'rules_gender_neutral_1044','rules_gender_neutral_1045','numeric_quantities',
 'punctuation_regression','api_contexts_1046','api_numeric_1047','api_numeric_1048',
 'api_grammar_1049','api_time_fragments_1050','text_completeness','windows_runtime'}
def audit(root,gates,previous,ledger):
 obj=json.loads(Path(gates).read_text('utf8'));gates=obj.get('gates',[]);g={a['id']:a for a in gates}
 if obj.get('schema_version')!=1 or obj.get('target_version')!='1.1' or len(gates)!=15 or set(g)!=GATE_IDS or any(x['status']=='completed' for x in gates):raise ValueError('Release 1.1 prematurely completed')
 p,d,w=g['pronoun_contexts'],g['draft_semantics'],g['windows_runtime']
 if (p.get('unresolved_count'),p.get('total_jvm_getter_calls'),p.get('shared_her_conflict_open'))!=(186,219,True):raise ValueError('Shared her remains unresolved')
 if (p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(253,420):raise ValueError('Historical rules review counters modified')
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'))!=(3658,312,3346):raise ValueError('API semantics not yet fully reviewed')
 if d.get('review_ledger')!='docs/API_SEMANTIC_REVIEW_1050.json' or d['status']!='blocked':raise ValueError('API review gate falsely unlocked')
 q=g['api_time_fragments_1050']
 if (q.get('added_api_rows'),q.get('changed_classes'),q.get('original_jvm_ldc_uses'),q.get('pending_windows_ui'))!=(8,1,17,8) or q['status']!='in_progress':raise ValueError('Time-fragment release scope forged')
 if (g['api_grammar_1049'].get('added_api_rows'),g['api_numeric_1048'].get('corrected_api_rows'))!=(1,29):raise ValueError('Prior verified release gate removed')
 if w.get('native_gameplay_tested') is not False or w['status']!='blocked':raise ValueError('Windows native runtime not tested')
 if g['text_completeness']['status']!='in_progress' or g['story_contexts'].get('pending_windows_ui')!=81:raise ValueError('Full game completeness not established')
 m=check(root);r=verify(root,previous,ledger)
 if m['current_map_rows']!=5269 or r['historical_reviewed_offline']!=312:raise ValueError('Release gate contradicts installed translation')
 return {'release':'1.0.50','gates':15,'target_1_1_blocked':True,
  'shared_time_fragments_localized_offline':8,'original_jvm_time_string_ldc_uses':17,
  'historical_api_reviewed_offline':312,'historical_api_unreviewed':3346,
  'remaining_java_getter_calls':186,'shared_her_conflict_open':True,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True)
 p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.ledger),indent=2))
