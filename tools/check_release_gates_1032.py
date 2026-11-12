#!/usr/bin/env python3
"""Gate Starsector PL 1.1 on actual review evidence, not status strings or CI success."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from verify_review_1032 import readrows,verify as review_verify

REQUIRED={'story_contexts','pronoun_contexts','draft_semantics','text_completeness','windows_runtime'}

def check(root,gates_path,prior_ledger,new_ledger,strict=False):
 gates=json.loads(gates_path.read_text('utf8'))
 assert gates['schema_version']==1 and gates['target_version']=='1.1'
 groups={g['id']:g for g in gates['gates']}
 assert len(groups)==len(gates['gates']) and set(groups)==REQUIRED
 for g in groups.values():
  assert g.get('status') in ('blocked','in_progress','verified') and g.get('source')
  if g['status']=='verified':assert g.get('evidence_file') and g.get('human_or_game_review')
 meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
 assert re.fullmatch(r'\d+(?:\.\d+)+',meta['version'])
 assert meta['gameVersion']=='0.98a-RC8'
 path=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1032.csv'
 rows=readrows(path)
 review=review_verify(rows,json.loads(prior_ledger.read_text('utf8')),json.loads(new_ledger.read_text('utf8')))
 d=groups['draft_semantics']
 assert d.get('review_ledger')=='docs/API_SEMANTIC_REVIEW_1032.json'
 assert d['total_draft_rows']==3658 and d['reviewed_offline']==55
 assert d['unresolved_count']==review['pending_offline_review']==3603
 assert d['gameplay_unverified_count']==review['total_pending_runtime_in_tracked_cohorts']==3664
 assert d.get('new_literal_count')==6
 blocked=[g for g in sorted(REQUIRED) if groups[g]['status']!='verified']
 if (strict or meta['version']=='1.1') and blocked:raise RuntimeError('Unverified 1.1 gates: '+', '.join(blocked))
 return {'current_version':meta['version'],'reviewed_offline':55,'pending_semantic_review':3603,
   'windows_runtime_pending_for_tracked_cohorts':3664,'blocked_gates':blocked,'release_11_allowed':not blocked}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,default=Path('docs/RELEASE_GATES_11.json'))
 p.add_argument('--prior-ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1031.json'))
 p.add_argument('--ledger',type=Path,default=Path('docs/API_SEMANTIC_REVIEW_1032.json'))
 p.add_argument('--strict',action='store_true')
 a=p.parse_args();print(json.dumps(check(a.worktree,a.gates,a.prior_ledger,a.ledger,a.strict),indent=2))
