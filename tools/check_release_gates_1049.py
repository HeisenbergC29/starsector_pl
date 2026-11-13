#!/usr/bin/env python3
"""Fail-closed Starsector PL 1.1 gates for development build 1.0.49."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1049 import check
from verify_review_1049 import verify
GATE_IDS={'story_contexts','pronoun_contexts','draft_semantics','rules_possessives',
 'rules_gender_neutral_1044','rules_gender_neutral_1045','numeric_quantities',
 'punctuation_regression','api_contexts_1046','api_numeric_1047','api_numeric_1048',
 'api_grammar_1049','text_completeness','windows_runtime'}
def audit(root,gates,previous,ledger):
 data=json.loads(Path(gates).read_text('utf8'))
 if data.get('schema_version')!=1 or data.get('target_version')!='1.1':raise ValueError('Invalid gate header')
 items=data.get('gates',[]);g={x['id']:x for x in items}
 if len(items)!=14 or len(g)!=14 or set(g)!=GATE_IDS or any(x['status']=='completed' for x in items):
  raise ValueError('Release 1.1 prematurely completed or gate inventory changed')
 p,d,w=g['pronoun_contexts'],g['draft_semantics'],g['windows_runtime']
 if (p.get('unresolved_count'),p.get('total_jvm_getter_calls'),p.get('shared_her_conflict_open'))!=(186,219,True):
  raise ValueError('Java pronoun getter conflict still unresolved')
 if (p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(253,420):
  raise ValueError('Prior gender review counters changed')
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'))!=(3658,252,3406):
  raise ValueError('API semantic review counts incorrect')
 if d.get('status')!='blocked' or d.get('review_ledger')!='docs/API_SEMANTIC_REVIEW_1049.json':
  raise ValueError('Historical API reviews improperly unlocked')
 q=g['api_grammar_1049']
 if (q.get('corrected_api_rows'),q.get('added_api_rows'),q.get('changed_classes'),q.get('pending_windows_ui'))!=(13,1,7,14) or q.get('status')!='in_progress':
  raise ValueError('Latest 1049 grammar audit changed')
 if (g['api_numeric_1048'].get('corrected_api_rows'),g['api_numeric_1047'].get('corrected_api_rows'))!=(29,14):
  raise ValueError('Previous API audits tampered')
 if w.get('status')!='blocked' or w.get('native_gameplay_tested') is not False:
  raise ValueError('Windows gameplay is not confirmed')
 if g['text_completeness']['status']!='in_progress' or g['story_contexts']['pending_windows_ui']!=81:
  raise ValueError('Global translation/Windows tests not complete')
 src=check(root);rev=verify(root,previous,ledger)
 if src['new_map_rows']!=5261 or rev['historical_reviewed_offline']!=252:raise ValueError('Gate does not match source files')
 return {'release':'1.0.49','target_1_1_blocked':True,'gate_count':14,
  'fixed_api_texts':13,'new_class_scoped_suffix_rule':1,'static_ui_reviewed_offline':44,
  'historical_api_reviewed_offline':252,'historical_api_unreviewed':3406,
  'unreviewed_jvm_getter_calls':186,'shared_her_conflict_open':True,
  'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True)
 p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.ledger),indent=2))
