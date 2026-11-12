#!/usr/bin/env python3
"""Release 1.1 still blocked after one 1.0.36 reflexive getter fix.

Offline/context review does NOT certify Windows gameplay, dynamic 'her' grammar,
or any of the remaining getter callsites.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_review_1036 import check as verify_api

REQUIRED={'story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime'}

def check(root,gates_path,prior_api,api_ledger,prior_rules,rules_ledger,strict=False):
 d=json.loads(gates_path.read_text('utf8'))
 assert d['schema_version']==1 and d['target_version']=='1.1'
 gates={g['id']:g for g in d['gates']}
 assert set(gates)==REQUIRED and len(gates)==len(d['gates'])
 for g in gates.values():
  assert g['status'] in {'blocked','in_progress','verified'} and g['source']
  if g['status']=='verified':
   assert g.get('evidence_file') and g.get('human_or_game_review')
 a=verify_api(root,prior_api,api_ledger)
 p=gates['pronoun_contexts']
 assert p['status']=='blocked'
 assert p['total_jvm_getter_calls']==219 and p['reviewed_reflexive_calls_offline']==1
 assert p['unresolved_count']==218 and p['pending_windows_ui_java_getter_calls']==219
 assert p['shared_her_conflict_open'] is True
 old=json.loads(prior_rules.read_text('utf8'));new=json.loads(rules_ledger.read_text('utf8'))
 assert old['installed_version']=='1.0.34' and old['reviewed_rows']==27
 assert new['installed_version']=='1.0.35' and new['cumulative_offline_rows']==91
 assert new['cumulative_removed_references']==183 and new['java_getter_calls_untouched']==219
 assert p['reviewed_rules_rows_offline']==91 and p['removed_visible_gender_variable_refs']==183
 assert p['pending_windows_ui_rules_rows']==91
 s=gates['story_contexts']
 assert s['reviewed_offline']==81 and s['unresolved_count']==0 and s['pending_windows_ui']==81 and s['status']=='in_progress'
 v=gates['draft_semantics']
 assert v['status']=='blocked'
 assert v['review_ledger']=='docs/API_SEMANTIC_REVIEW_1036.json'
 assert v['total_draft_rows']==3658 and v['reviewed_offline']==a['total_offline_reviewed']==78
 assert v['unresolved_count']==a['pending_historical_semantic_review']==3580
 assert v['gameplay_unverified_count']==a['runtime_unverified_tracked_api']==3683
 assert v['new_literal_count']==25
 assert gates['text_completeness']['status']=='in_progress'
 assert gates['windows_runtime']['status']=='blocked'
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['version']=='1.0.36' and meta['gameVersion']=='0.98a-RC8'
 blocked=[g['id'] for g in d['gates'] if g['status']!='verified']
 if strict or meta['version']=='1.1':
  if blocked:raise RuntimeError('Refusing premature 1.1: '+', '.join(blocked))
 return {'version':'1.0.36','java_getters_total':219,'java_getters_reviewed_offline':1,
  'java_getters_still_unresolved':218,'java_getter_ui_pending_windows':219,
  'visible_rules_rows_reviewed_offline':91,'rules_references_removed':183,
  'api_reviews_offline':78,'api_pending_semantics':3580,
  'story_points_offline':81,'story_points_pending_windows':81,
  'windows_gameplay_tested':False,'release_11_allowed':False,'blocked_gates':blocked}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,default=Path('docs/RELEASE_GATES_11.json'))
 p.add_argument('--prior-api-ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1033.json'))
 p.add_argument('--api-ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1036.json'))
 p.add_argument('--prior-rules-ledger',type=Path,default=Path('docs/RULES_PRONOUN_REVIEW_1034.json'))
 p.add_argument('--rules-ledger',type=Path,default=Path('docs/RULES_PRONOUN_REVIEW_1035.json'))
 p.add_argument('--strict',action='store_true')
 a=p.parse_args();print(json.dumps(check(a.worktree,a.gates,a.prior_api_ledger,a.api_ledger,a.prior_rules_ledger,a.rules_ledger,a.strict),indent=2))
