#!/usr/bin/env python3
"""Prevent a misleading 1.1 release while Windows/UI, pronoun, or coverage gates remain open."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_review_1033 import readrows,verify

REQUIRED={'story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime'}
def check(root,gates_path,prior_ledger,ledger,strict=False):
 obj=json.loads(gates_path.read_text('utf8'))
 assert obj['schema_version']==1 and obj['target_version']=='1.1'
 gates={g['id']:g for g in obj['gates']}
 assert len(gates)==len(obj['gates']) and set(gates)==REQUIRED
 for g in gates.values():
  assert g['status'] in {'blocked','in_progress','verified'} and g.get('source')
  if g['status']=='verified':assert g.get('evidence_file') and g.get('human_or_game_review')
 data=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1033.csv'
 result=verify(readrows(data),json.loads(prior_ledger.read_text('utf8')),json.loads(ledger.read_text('utf8')))
 d=gates['draft_semantics']
 assert d['review_ledger']=='docs/API_SEMANTIC_REVIEW_1033.json'
 assert d['total_draft_rows']==3658 and d['reviewed_offline']==result['reviewed_offline']
 assert d['unresolved_count']==result['pending_offline_semantics']==3600
 assert d['gameplay_unverified_count']==result['api_pending_windows_in_tracked_cohorts']==3681
 assert d['new_literal_count']==23
 story=gates['story_contexts']
 assert story['reviewed_offline']==81 and story['unresolved_count']==0
 assert story['pending_windows_ui']==81 and story['status']=='in_progress'
 assert gates['pronoun_contexts']['unresolved_count']==219
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert meta['gameVersion']=='0.98a-RC8'
 blocked=[k for k in sorted(gates) if gates[k]['status']!='verified']
 if (strict or meta['version']=='1.1') and blocked:raise RuntimeError('1.1 is blocked: '+', '.join(blocked))
 assert meta['version']=='1.0.33'
 return {'current_version':meta['version'],'story_offline_reviewed':81,'story_pending_windows_ui':81,
         'api_pending_offline_review':3600,'api_pending_windows':3681,
         'blocked_gates':blocked,'release_11_allowed':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,default=Path('docs/RELEASE_GATES_11.json'))
 p.add_argument('--prior-ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1032.json'))
 p.add_argument('--ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1033.json'))
 p.add_argument('--strict',action='store_true')
 a=p.parse_args();print(json.dumps(check(a.worktree,a.gates,a.prior_ledger,a.ledger,a.strict),indent=2))
if __name__=='__main__':main()
