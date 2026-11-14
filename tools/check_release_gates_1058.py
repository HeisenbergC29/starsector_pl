#!/usr/bin/env python3
"""Reconcile strictly incremental 1.1 release-gate accounting after 1.0.58."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1058 import check

NEW_GATE='rules_speech_attributions_1058'

def metadata(gates:Path,previous:Path)->dict:
 now=json.loads(Path(gates).read_text('utf8'));old=json.loads(Path(previous).read_text('utf8'))
 a=now.get('gates',[]);b=old.get('gates',[])
 new={g['id']:g for g in a};prior={g['id']:g for g in b}
 if any((x.get('schema_version'),x.get('target_version'))!=(1,'1.1') for x in [now,old]):raise ValueError('Invalid version 1.1 release schema')
 if (len(b),len(prior),len(a),len(new))!=(22,22,23,23) or set(new)!=set(prior)|{NEW_GATE}:
  raise ValueError('Release gates were dropped, duplicated or renamed')
 if any(g.get('status')=='completed' for g in a):raise ValueError('False 1.1 completion')
 for id in prior:
  if id not in ('pronoun_contexts','text_completeness','windows_runtime') and new[id]!=prior[id]:
   raise ValueError(('Older release gate mutated',id))
 prev=prior['pronoun_contexts'];p=new['pronoun_contexts'];d=new['draft_semantics'];w=new['windows_runtime'];f=new[NEW_GATE]
 if (prev.get('reviewed_rules_rows_offline'),prev.get('removed_visible_gender_variable_refs'))!=(433,606):
  raise ValueError('Prior 1.0.57 dialogue ledger was altered')
 if (p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'),p.get('pending_windows_ui_rules_rows'))!=(555,742,555):
  raise ValueError('New ID/placeholder accounting inconsistent')
 if (p.get('unresolved_count'),p.get('total_jvm_getter_calls'),p.get('shared_her_conflict_open'),p.get('shared_her_pending_native_windows_validation'))!=(186,219,False,True):
  raise ValueError('Java getter review silently marked complete')
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'),d.get('review_ledger'),d.get('status'))!=(3658,391,3267,'docs/API_SEMANTIC_REVIEW_1055.json','blocked'):
  raise ValueError('Historic API review status falsely advanced')
 if (f.get('status'),f.get('corrected_rules_rows'),f.get('removed_dynamic_gender_refs'),f.get('previous_affected_rows'),f.get('remaining_affected_rows'),f.get('previous_placeholder_occurrences'),f.get('remaining_placeholder_occurrences'))!=('in_progress',122,136,1028,1006,2089,1953):
  raise ValueError('Invalid 1.0.58 dialogue release gate evidence')
 if (f.get('protected_prior_reviewed_ids'),f.get('changes_to_conditions_scripts_ids_options'),f.get('pending_windows_ui'),f.get('native_windows_gameplay_tested'))!=(433,0,122,False):
  raise ValueError('Metadata/logic changes or false runtime test')
 if w.get('status')!='blocked' or w.get('native_gameplay_tested') is not False or new['text_completeness'].get('status')!='in_progress':
  raise ValueError('Prematurely declared Starsector 1.1 complete')
 return {'current_release':'1.0.58','target_release':'1.1','target_blocked':True,
  'release_gates':23,'new_dialogues_reviewed':122,'cumulative_unique_reviewed_dialogues':555,
  'remaining_gender_variables':1953,'remaining_java_getters':186,
  'remaining_historical_api_reviews':3267,'native_windows_gameplay_tested':False}

def audit(worktree:Path,gates:Path,previous:Path)->dict:
 state=metadata(gates,previous)
 actual=check(worktree)
 if (actual['new_reviewed_dialogue_rows'],actual['speech_attributions_corrected'],actual['remaining_gender_placeholders'])!=(122,136,1953):
  raise ValueError('Release gate lacks evidence in rebuilt dialogue data')
 return state

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous),indent=2))
