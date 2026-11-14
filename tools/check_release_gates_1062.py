#!/usr/bin/env python3
"""Strict v1.1 blocked release-gate accounting after 31 PirateBaseIntel API reviews."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1062 import check as verify_sources
from build_review_1062 import check as verify_reviews
GATE='pirate_base_jvm_1062'

def metadata(current:Path,previous:Path)->dict:
 current=json.loads(Path(current).read_text('utf8'));prior=json.loads(Path(previous).read_text('utf8'))
 if any((obj.get('schema_version'),obj.get('target_version'))!=(1,'1.1') for obj in (current,prior)):
  raise ValueError('Unexpected target/schema release gate')
 now=current['gates'];old=prior['gates'];a={x['id']:x for x in now};b={x['id']:x for x in old}
 if (len(now),len(a),len(old),len(b))!=(27,27,26,26) or set(a)!=set(b)|{GATE}:
  raise ValueError('Missing or duplicate cumulative release gates')
 if any(x.get('status')=='completed' for x in now):raise ValueError('Unsupported 1.1 completion asserted')
 for key in b:
  if key not in {'draft_semantics','text_completeness','windows_runtime'} and a[key]!=b[key]:
   raise ValueError(('Previously verified release gate modified',key))
 prev=b['draft_semantics'];d=a['draft_semantics'];f=a[GATE];p=a['pronoun_contexts'];w=a['windows_runtime']
 if (prev.get('total_draft_rows'),prev.get('reviewed_offline'),prev.get('unresolved_count'),prev.get('review_ledger'))!=(3658,416,3242,'docs/API_SEMANTIC_REVIEW_1061.json'):
  raise ValueError('Incorrect previous review census')
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'),d.get('review_ledger'),d.get('status'))!=(3658,447,3211,'docs/API_SEMANTIC_REVIEW_1062.json','blocked'):
  raise ValueError('History review ledger invented or truncated')
 if (f.get('status'),f.get('previous_historical_reviews'),f.get('new_historical_reviews'),
  f.get('total_historical_reviews'),f.get('changed_existing_translations'),f.get('added_missing_literals'),
  f.get('original_jvm_ldc_verified'),f.get('changed_classes'),f.get('tested_render_variants'),
  f.get('restored_technical_category_strings'))!=('in_progress',416,31,447,5,2,42,1,18,2):
  raise ValueError('Incorrect class translation/JVM evidence or inflated counter')
 if (f.get('changed_game_data_files'),f.get('changed_jvm_executable_instructions'),f.get('native_windows_gameplay_tested'))!=(0,0,False):
  raise ValueError('Unsafe data, Java code or fabricated runtime test')
 if (p.get('unresolved_count'),p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(186,555,742):
  raise ValueError('Dialogue / getter review counter unexpectedly modified')
 if (w.get('status'),w.get('native_gameplay_tested'),a['text_completeness'].get('status'))!=('blocked',False,'in_progress'):
  raise ValueError('Target 1.1 falsely marked ready')
 return {'release':'1.0.62','target_1_1_blocked':True,'release_gates':27,
  'historical_api_reviewed':447,'historical_api_remaining':3211,
  'class_verified_original_jvm_ldc_uses':42,'getters_unresolved':186,
  'gender_variables_unreviewed':1953,'native_windows_gameplay_tested':False}

def audit(root:Path,current:Path,previous:Path,prior_semantic:Path,new_semantic:Path)->dict:
 result=metadata(current,previous)
 actual=verify_sources(root)
 if (actual['historical_newly_reviewed'],actual['original_jvm_ldc_uses'],actual['new_literal_translations'],actual['game_data_files_byte_identical'])!=(31,42,2,870):
  raise ValueError('Gate not supported by installed release files')
 repo=Path(__file__).resolve().parent.parent
 verify_reviews(root,repo/'docs/PIRATE_BASE_REVIEW_1062.json',prior_semantic,new_semantic)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 p.add_argument('--prior-semantic',required=True,type=Path);p.add_argument('--semantic',required=True,type=Path)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
