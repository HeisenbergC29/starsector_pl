#!/usr/bin/env python3
"""Fail-closed target v1.1 gates after 25 verified historical API reviews."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1061 import check as source_check
from build_review_1061 import check as review_check
GATE='gate_hauler_jvm_1061'

def metadata(current:Path,previous:Path)->dict:
 c=json.loads(Path(current).read_text('utf8'))
 old=json.loads(Path(previous).read_text('utf8'))
 if any((x.get('schema_version'),x.get('target_version'))!=(1,'1.1') for x in (c,old)):
  raise ValueError('Expected target 1.1 and exact schema')
 now=c['gates'];older=old['gates'];a={x['id']:x for x in now};b={x['id']:x for x in older}
 if (len(now),len(a),len(older),len(b))!=(26,26,25,25) or set(a)!=set(b)|{GATE}:
  raise ValueError('Duplicate, missing or renamed 1.1 gates')
 if any(x.get('status')=='completed' for x in now):raise ValueError('False 1.1 completion')
 mutable={'draft_semantics','text_completeness','windows_runtime'}
 if any(a[k]!=b[k] for k in b if k not in mutable):
  raise ValueError('Previously verified release gates were silently changed')
 prior=b['draft_semantics'];draft=a['draft_semantics'];p=a['pronoun_contexts'];w=a['windows_runtime'];f=a[GATE]
 if (prior.get('total_draft_rows'),prior.get('reviewed_offline'),prior.get('unresolved_count'),prior.get('review_ledger'))!=(3658,391,3267,'docs/API_SEMANTIC_REVIEW_1055.json'):
  raise ValueError('Base release history was revised')
 if (draft.get('total_draft_rows'),draft.get('reviewed_offline'),draft.get('unresolved_count'),draft.get('review_ledger'),draft.get('status'))!=(3658,416,3242,'docs/API_SEMANTIC_REVIEW_1061.json','blocked'):
  raise ValueError('Historical API review accounting mismatch')
 if (f.get('status'),f.get('previous_historical_reviews'),f.get('new_historical_reviews'),
  f.get('total_historical_reviews'),f.get('changed_existing_translations'),f.get('added_missing_literals'),
  f.get('original_jvm_ldc_verified'),f.get('changed_classes'),f.get('tested_render_variants'))!=(
   'in_progress',391,25,416,15,3,49,1,93):
  raise ValueError('1.0.61 semantic and JVM evidence mismatched')
 if (f.get('changed_game_data_files'),f.get('changed_jvm_executable_instructions'),f.get('native_windows_gameplay_tested'))!=(0,0,False):
  raise ValueError('Unsafe changes or false gameplay status')
 if (p.get('unresolved_count'),p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(186,555,742):
  raise ValueError('Getter or dialogue counts illegally advanced')
 if (w.get('native_gameplay_tested'),w.get('status'),a['text_completeness'].get('status'))!=(False,'blocked','in_progress'):
  raise ValueError('Windows gameplay / completeness falsely claimed')
 return {'release':'1.0.61','target_1_1_blocked':True,'number_of_release_gates':26,
  'historical_api_reviewed':416,'historical_api_remaining':3242,
  'original_jvm_ldc_verified':49,'remaining_dynamic_gender_tokens':1953,
  'getter_calls_unresolved':186,'native_windows_gameplay_tested':False}

def audit(root:Path,current:Path,previous:Path,prior_semantic:Path,new_semantic:Path)->dict:
 r=metadata(current,previous)
 actual=source_check(root)
 if (actual['reviewed_historical_rows'],actual['new_literals'],actual['grammar_combinations'])!=(25,3,93):
  raise ValueError('Gate accounting unsupported by actual files')
 review_check(root,Path(__file__).resolve().parent.parent/'docs/GATE_HAULER_REVIEW_1061.json',prior_semantic,new_semantic)
 return r

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 p.add_argument('--prior-semantic',type=Path,required=True);p.add_argument('--semantic',type=Path,required=True)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
