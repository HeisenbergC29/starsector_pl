#!/usr/bin/env python3
"""Guard target 1.1 against premature completion after 1.0.57 grammar edits."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1057 import check

def metadata(gates:Path,previous:Path)->dict:
 new=json.loads(Path(gates).read_text('utf8'))
 old=json.loads(Path(previous).read_text('utf8'))
 now=new.get('gates',[]);then=old.get('gates',[])
 a={r['id']:r for r in now};b={r['id']:r for r in then}
 if (new.get('schema_version'),new.get('target_version'))!=(1,'1.1') or (old.get('schema_version'),old.get('target_version'))!=(1,'1.1'):
  raise ValueError('Release-gate schema mismatch')
 if len(then)!=21 or len(b)!=21 or len(now)!=22 or len(a)!=22 or set(a)!=set(b)|{'rules_reflexive_1057'}:
  raise ValueError('Missing, duplicated or renamed release gate')
 if any(r.get('status')=='completed' for r in now):raise ValueError('Target 1.1 falsely complete')
 for key in b:
  if key not in ('pronoun_contexts','text_completeness','windows_runtime') and a[key]!=b[key]:
   raise ValueError(('Previously approved gate was modified',key))
 oldp=b['pronoun_contexts'];p=a['pronoun_contexts'];d=a['draft_semantics'];w=a['windows_runtime'];f=a['rules_reflexive_1057']
 if (oldp.get('reviewed_rules_rows_offline'),oldp.get('removed_visible_gender_variable_refs'))!=(363,530):
  raise ValueError('Previous unique review counts cannot be verified')
 if (p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'),p.get('pending_windows_ui_rules_rows'))!=(433,606,433):
  raise ValueError('New dialogue edits double counted or missing')
 if (p.get('unresolved_count'),p.get('total_jvm_getter_calls'),p.get('shared_her_conflict_open'),p.get('shared_her_pending_native_windows_validation'))!=(186,219,False,True):
  raise ValueError('Unchecked JVM getters or shared literal status falsified')
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'),d.get('review_ledger'),d.get('status'))!=(3658,391,3267,'docs/API_SEMANTIC_REVIEW_1055.json','blocked'):
  raise ValueError('Unreviewed API translations falsely marked complete')
 if (f.get('status'),f.get('corrected_rules_rows'),f.get('corrected_grammar_fragments'),f.get('removed_dynamic_gender_refs'))!=('in_progress',70,74,76):
  raise ValueError('Dialogue correction gate contains unsupported counts')
 if (f.get('previous_affected_rows'),f.get('remaining_affected_rows'),f.get('previous_placeholder_occurrences'),f.get('remaining_placeholder_occurrences'))!=(1029,1028,2165,2089):
  raise ValueError('Remaining dynamic texts falsely accounted for')
 if f.get('protected_prior_reviewed_ids')!=363 or f.get('changes_to_conditions_scripts_ids_options')!=0 or f.get('pending_windows_ui')!=70 or f.get('native_windows_gameplay_tested') is not False:
  raise ValueError('Protection or live-test status is invalid')
 if w.get('status')!='blocked' or w.get('native_gameplay_tested') is not False or a['text_completeness'].get('status')!='in_progress':
  raise ValueError('Invalid 1.1 completion assertion')
 return {'current_version':'1.0.57','target':'1.1','target_blocked':True,'gates':22,
  'new_dialogue_rows':70,'unique_dialogue_rows_reviewed_offline':433,
  'remaining_gender_tokens':2089,'remaining_jvm_getter_calls':186,
  'remaining_historical_api_reviews':3267,'native_windows_gameplay_tested':False}

def audit(worktree:Path,gates:Path,previous:Path)->dict:
 result=metadata(gates,previous)
 actual=check(worktree)
 if (actual['corrected_dialogue_rows'],actual['corrected_grammar_fragments'],actual['remaining_gender_placeholders'])!=(70,74,2089):
  raise ValueError('Release gate is unsupported by patched game data')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous),indent=2))
