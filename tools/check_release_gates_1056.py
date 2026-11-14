#!/usr/bin/env python3
"""Fail closed on target 1.1 while validating the v1.0.56 dialogue release."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1056 import check

def metadata(gates:Path,prior:Path)->dict:
 d=json.loads(Path(gates).read_text('utf8'));old=json.loads(Path(prior).read_text('utf8'))
 a=d.get('gates',[]);b=old.get('gates',[])
 g={x['id']:x for x in a};h={x['id']:x for x in b}
 if d.get('schema_version')!=1 or d.get('target_version')!='1.1' or len(a)!=21 or len(g)!=21 or len(b)!=20 or len(h)!=20:
  raise ValueError('Incomplete/duplicated version 1.1 gates')
 if set(g)!=set(h)|{'rules_gender_neutral_1056'} or set(g)-set(h)!={'rules_gender_neutral_1056'}:
  raise ValueError('Prior gate deleted/renamed')
 if any(x.get('status')=='completed' for x in a):raise ValueError('Prematurely marked 1.1 complete')
 for key in h:
  if key not in ('pronoun_contexts','text_completeness','windows_runtime') and g[key]!=h[key]:
   raise ValueError(('Previously verified release gate mutated',key))
 oldp=h['pronoun_contexts'];p=g['pronoun_contexts'];r=g['draft_semantics'];w=g['windows_runtime'];f=g['rules_gender_neutral_1056']
 if (oldp.get('reviewed_rules_rows_offline'),oldp.get('removed_visible_gender_variable_refs'))!=(253,420):
  raise ValueError('Historical dialogue accounting baseline altered')
 if (p.get('unresolved_count'),p.get('total_jvm_getter_calls'),p.get('shared_her_conflict_open'),p.get('shared_her_pending_native_windows_validation'))!=(186,219,False,True):
  raise ValueError('Unresolved JVM getter review counts falsified')
 if (p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'),p.get('pending_windows_ui_rules_rows'))!=(363,530,363):
  raise ValueError('110 new dialogue corrections missing or double-counted')
 if (r.get('total_draft_rows'),r.get('reviewed_offline'),r.get('unresolved_count'),r.get('review_ledger'),r.get('status'))!=(3658,391,3267,'docs/API_SEMANTIC_REVIEW_1055.json','blocked'):
  raise ValueError('Historical API review count changed without new API audit')
 if (f.get('status'),f.get('corrected_rules_rows'),f.get('removed_dynamic_gender_refs'),f.get('previous_affected_rows'),f.get('remaining_affected_rows'),f.get('previous_placeholder_occurrences'),f.get('remaining_placeholder_occurrences'),f.get('pending_windows_ui'))!=('in_progress',110,110,1139,1029,2275,2165,110):
  raise ValueError('New text-only dialogue validation gate falsified')
 if f.get('changes_to_conditions_scripts_ids_options',1)!=0 or f.get('native_windows_gameplay_tested')!=False:
  raise ValueError('Unsafe script modifications or false gameplay test')
 if w.get('status')!='blocked' or w.get('native_gameplay_tested')!=False or g['text_completeness'].get('status')!='in_progress':
  raise ValueError('Prematurely declared native Windows or localization completeness')
 return {'release':'1.0.56','target_1_1_blocked':True,'gates':21,'api_history_reviewed':391,
  'api_history_unreviewed':3267,'rules_reviewed_offline':363,'rules_text_rows_changed':110,
  'remaining_gender_placeholder_occurrences':2165,'unreviewed_java_getter_calls':186,'native_gameplay_tested':False}

def audit(root:Path,gates:Path,prior:Path)->dict:
 result=metadata(gates,prior)
 v=check(root)
 if (v['changed_dialogue_rows'],v['remaining_gender_tokens'])!=(110,2165):
  raise ValueError('Release gate not supported by actual game rules')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous),indent=2))
