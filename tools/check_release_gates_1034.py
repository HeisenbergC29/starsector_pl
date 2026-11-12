#!/usr/bin/env python3
"""Block 1.1 until remaining 219 Java pronoun calls and runtime/UI gates are cleared."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_review_1033 import readrows,verify as verify_api_review
from verify_review_1034 import check as verify_rules_review

REQUIRED={'story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime'}

def check(root,gates_path,prior_ledger,ledger,rules_ledger,strict=False):
 obj=json.loads(gates_path.read_text('utf8'))
 assert obj['schema_version']==1 and obj['target_version']=='1.1'
 gates={g['id']:g for g in obj['gates']}
 assert len(gates)==len(obj['gates']) and set(gates)==REQUIRED
 for g in gates.values():
  assert g['status'] in {'blocked','in_progress','verified'} and g.get('source')
  if g['status']=='verified':assert g.get('evidence_file') and g.get('human_or_game_review')
 data=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1033.csv'
 result=verify_api_review(readrows(data),json.loads(prior_ledger.read_text('utf8')),json.loads(ledger.read_text('utf8')))
 r=verify_rules_review(root,rules_ledger)
 d=gates['draft_semantics']
 assert d['review_ledger']=='docs/API_SEMANTIC_REVIEW_1033.json'
 assert d['total_draft_rows']==3658 and d['reviewed_offline']==result['reviewed_offline']==58
 assert d['unresolved_count']==result['pending_offline_semantics']==3600
 assert d['gameplay_unverified_count']==result['api_pending_windows_in_tracked_cohorts']==3681
 assert d['new_literal_count']==23
 story=gates['story_contexts']
 assert story['reviewed_offline']==81 and story['unresolved_count']==0
 assert story['pending_windows_ui']==81 and story['status']=='in_progress'
 p=gates['pronoun_contexts']
 assert p['unresolved_count']==219 and p['status']=='blocked'
 assert p['reviewed_rules_rows_offline']==27
 assert p['removed_visible_gender_variable_refs']==75
 assert p['pending_windows_ui_rules_rows']==27
 assert p['rules_review_ledger']=='docs/RULES_PRONOUN_REVIEW_1034.json'
 assert gates['windows_runtime']['status']=='blocked'
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['gameVersion']=='0.98a-RC8'
 blocked=[k for k in sorted(gates) if gates[k]['status']!='verified']
 if (strict or meta['version']=='1.1') and blocked:raise RuntimeError('1.1 is blocked: '+', '.join(blocked))
 assert meta['version']=='1.0.34'
 return {'current_version':'1.0.34','story_reviewed_offline':81,'story_pending_windows':81,
         'pronoun_java_calls_not_resolved':219,'rules_reviewed_offline_rows':27,
         'rules_unrendered_pronoun_variables':75,'rules_pending_windows_ui_rows':27,
         'api_pending_offline_semantics':3600,'api_pending_windows':3681,
         'blocked_gates':blocked,'release_11_allowed':False}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('worktree',type=Path)
 ap.add_argument('--gates',type=Path,default=Path('docs/RELEASE_GATES_11.json'))
 ap.add_argument('--prior-ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1032.json'))
 ap.add_argument('--ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1033.json'))
 ap.add_argument('--rules-ledger',type=Path,default=Path('docs/RULES_PRONOUN_REVIEW_1034.json'))
 ap.add_argument('--strict',action='store_true')
 a=ap.parse_args();print(json.dumps(check(a.worktree,a.gates,a.prior_ledger,a.ledger,a.rules_ledger,a.strict),indent=2))
