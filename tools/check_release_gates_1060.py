#!/usr/bin/env python3
"""Fail closed on target 1.1, accounting only verified v1.0.60 UI work."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1060 import check
GATE='trade_route_and_procurement_1060'

def metadata(current:Path,previous:Path)->dict:
 new=json.loads(Path(current).read_text('utf8'));old=json.loads(Path(previous).read_text('utf8'))
 if any((x.get('schema_version'),x.get('target_version'))!=(1,'1.1') for x in (new,old)):
  raise ValueError('Wrong release gate schema')
 now=new['gates'];prior=old['gates'];a={x['id']:x for x in now};b={x['id']:x for x in prior}
 if (len(now),len(a),len(prior),len(b))!=(25,25,24,24) or set(a)!=set(b)|{GATE}:
  raise ValueError('Missing/duplicate/renamed cumulative release gate')
 if any(x.get('status')=='completed' for x in now):raise ValueError('1.1 marked complete before native testing')
 for key in b:
  if key not in ('text_completeness','windows_runtime') and a[key]!=b[key]:
   raise ValueError(('Previously verified release gate was silently modified',key))
 f=a[GATE];s=a['draft_semantics'];p=a['pronoun_contexts'];w=a['windows_runtime']
 if (f.get('status'),f.get('new_class_scoped_literals'),f.get('repaired_previously_unverified_literals'),
     f.get('original_jvm_ldc_callsites'),f.get('modified_classes'),f.get('composed_sentences_tested'))!=(
      'in_progress',5,2,7,2,16):
  raise ValueError('1.0.60 translation or JVM evidence incorrectly claimed')
 if (f.get('mod_data_changed'),f.get('new_executable_java_instruction_changes'),f.get('native_windows_gameplay_tested'))!=(0,0,False):
  raise ValueError('Data/JVM/gameplay safety gate not supported')
 if (s.get('total_draft_rows'),s.get('reviewed_offline'),s.get('unresolved_count'),s.get('status'),s.get('review_ledger'))!=(
     3658,391,3267,'blocked','docs/API_SEMANTIC_REVIEW_1055.json'):
  raise ValueError('Historical API review count cannot be advanced from new literal additions')
 if (p.get('unresolved_count'),p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(186,555,742):
  raise ValueError('Getter or dialogue review count was falsely advanced')
 if (w.get('native_gameplay_tested'),w.get('status'),a['text_completeness'].get('status'))!=(False,'blocked','in_progress'):
  raise ValueError('Required native game tests marked completed')
 return {'release':'1.0.60','target':'1.1','blocked':True,'release_gates':25,
  'new_literals':5,'revised_literals':2,'original_jvm_ldc_verified':7,
  'historical_api_reviewed':391,'api_history_unreviewed':3267,
  'getter_calls_unresolved':186,'remaining_dynamic_gender_placeholders':1953,
  'native_windows_gameplay_tested':False}

def audit(root:Path,current:Path,previous:Path)->dict:
 result=metadata(current,previous)
 actual=check(root)
 if (actual['added_literals'],actual['corrected_literals'],actual['rendered_combinations'],actual['unchanged_data_files'])!=(5,2,16,870):
  raise ValueError('Release gate not supported by physical mapping and game data')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous),indent=2))
