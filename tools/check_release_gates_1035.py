#!/usr/bin/env python3
"""Never label a patch complete 1.1 while Java/getter, API and Windows gates remain."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_review_1033 import readrows,verify as verify_api_review
from verify_review_1035 import check as verify_dialogue_reviews

REQUIRED={'story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime'}

def check(root,gates_path,prior_api_ledger,api_ledger,prior_rules_ledger,rules_ledger,strict=False):
 obj=json.loads(gates_path.read_text('utf8'))
 assert obj['schema_version']==1 and obj['target_version']=='1.1'
 gates={g['id']:g for g in obj['gates']}
 assert len(gates)==len(obj['gates']) and set(gates)==REQUIRED
 for g in gates.values():
  assert g.get('source') and g['status'] in ('blocked','in_progress','verified')
  if g['status']=='verified':assert g.get('evidence_file') and g.get('human_or_game_review')
 api_file=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1033.csv'
 api=verify_api_review(readrows(api_file),json.loads(prior_api_ledger.read_text('utf8')),json.loads(api_ledger.read_text('utf8')))
 rules=verify_dialogue_reviews(root,prior_rules_ledger,rules_ledger)
 s=gates['story_contexts']
 assert s['reviewed_offline']==81 and s['unresolved_count']==0 and s['pending_windows_ui']==81 and s['status']=='in_progress'
 p=gates['pronoun_contexts']
 assert p['status']=='blocked' and p['unresolved_count']==219
 assert p['reviewed_rules_rows_offline']==rules['cumulative_reviewed_rows']==91
 assert p['removed_visible_gender_variable_refs']==rules['cumulative_removed_variable_references']==183
 assert p['pending_windows_ui_rules_rows']==rules['pending_native_windows_dialog_rows']==91
 assert p['rules_review_ledger']=='docs/RULES_PRONOUN_REVIEW_1035.json'
 assert p['prior_rules_review_ledger']=='docs/RULES_PRONOUN_REVIEW_1034.json'
 d=gates['draft_semantics']
 assert d['status']=='blocked' and d['review_ledger']=='docs/API_SEMANTIC_REVIEW_1033.json'
 assert d['total_draft_rows']==3658 and d['reviewed_offline']==api['reviewed_offline']==58
 assert d['unresolved_count']==api['pending_offline_semantics']==3600
 assert d['gameplay_unverified_count']==api['api_pending_windows_in_tracked_cohorts']==3681
 assert d['new_literal_count']==23
 assert gates['windows_runtime']['status']=='blocked'
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['gameVersion']=='0.98a-RC8'
 blocked=sorted(k for k in gates if gates[k]['status']!='verified')
 if (strict or meta['version']=='1.1') and blocked:raise RuntimeError('1.1 cannot be published: '+', '.join(blocked))
 assert meta['version']=='1.0.35'
 return {'version':'1.0.35','story_reviewed_offline':81,'story_ui_pending_windows':81,
  'java_pronoun_calls_unresolved':219,'dialogue_reviewed_offline_rows':91,
  'dialogue_unrendered_gender_variables':183,'dialogue_ui_pending_windows_rows':91,
  'api_pending_offline_semantics':3600,'api_pending_windows':3681,
  'blocked_gates':blocked,'release_11_allowed':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,default=Path('docs/RELEASE_GATES_11.json'))
 p.add_argument('--prior-api-ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1032.json'))
 p.add_argument('--api-ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1033.json'))
 p.add_argument('--prior-rules-ledger',type=Path,default=Path('docs/RULES_PRONOUN_REVIEW_1034.json'))
 p.add_argument('--rules-ledger',type=Path,default=Path('docs/RULES_PRONOUN_REVIEW_1035.json'))
 p.add_argument('--strict',action='store_true')
 a=p.parse_args()
 print(json.dumps(check(a.worktree,a.gates,a.prior_api_ledger,a.api_ledger,a.prior_rules_ledger,a.rules_ledger,a.strict),indent=2))
