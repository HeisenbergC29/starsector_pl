#!/usr/bin/env python3
"""Fail-closed v1.1 while verifying real v1.0.55 source and historical ledger."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1055 import check
from verify_review_1055 import check as review
from check_release_gates_1054 import IDS as OLDER_IDS

IDS=OLDER_IDS|{'api_blockade_duration_1055'}

def audit(root,gates,previous,ledger):
 d=json.loads(Path(gates).read_text('utf8'));a=d.get('gates',[])
 g={x['id']:x for x in a}
 if d.get('schema_version')!=1 or d.get('target_version')!='1.1' or len(a)!=20 or set(g)!=IDS or any(x.get('status')=='completed' for x in a):
  raise ValueError('Release gates absent, duplicated, or prematurely closed')
 p=g['pronoun_contexts'];r=g['draft_semantics'];w=g['windows_runtime'];f=g['api_blockade_duration_1055']
 if (p.get('unresolved_count'),p.get('total_jvm_getter_calls'),p.get('shared_her_conflict_open'),p.get('shared_her_pending_native_windows_validation'))!=(186,219,False,True):
  raise ValueError('Unresolved gender callsite backlog falsified')
 if (r.get('total_draft_rows'),r.get('reviewed_offline'),r.get('unresolved_count'),r.get('review_ledger'),r.get('status'))!=(3658,391,3267,'docs/API_SEMANTIC_REVIEW_1055.json','blocked'):
  raise ValueError('Historical semantic backlog incorrectly marked finished')
 if (f.get('added_api_rows'),f.get('corrected_api_rows'),f.get('changed_classes'),f.get('pending_windows_ui'),f.get('reviewed_historical_ui_fragments'),f.get('status'))!=(8,2,3,10,48,'in_progress'):
  raise ValueError('Blocked/time UI gate falsified')
 if (g['api_dynamic_fragments_1054'].get('new_api_rows'),g['api_dynamic_fragments_1054'].get('corrected_api_rows'))!=(7,6):
  raise ValueError('Prior API gate modified')
 if g['obf_recovery_1053'].get('total_obf_entries')!=3537 or g['personality_ui_1051'].get('jvm_ldc_operand_changes')!=2:
  raise ValueError('Prior original-JVM validation discarded')
 if (w.get('native_gameplay_tested'),w.get('status'),g['text_completeness'].get('status'))!=(False,'blocked','in_progress'):
  raise ValueError('Native Windows status falsely closed')
 if (check(root)['rows_api'],review(root,previous,ledger)['historical_reviewed'])!=(5298,391):
  raise ValueError('Map and semantic review ledger diverged')
 return {'release':'1.0.55','target_1_1_blocked':True,'gates':20,
  'offline_historical_api_reviewed':391,'historical_api_remaining':3267,
  'unreviewed_java_gender_callsites':186,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 for k in ('gates','previous','ledger'):p.add_argument('--'+k,required=True,type=Path)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.ledger),indent=2))
