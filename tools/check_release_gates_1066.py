#!/usr/bin/env python3
"""Cumulative 1.1 release-gate audit, with post-1.1 in-game test scheduling."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1066 import check
from build_review_1066 import check as review_check
GATE='sim_industry_tutorial_jvm_1066'

def metadata(current:Path,previous:Path)->dict:
 now=json.loads(Path(current).read_text('utf8'));old=json.loads(Path(previous).read_text('utf8'))
 if any((x.get('schema_version'),x.get('target_version'))!=(1,'1.1') for x in (now,old)):
  raise ValueError('Unsupported versioned release gate metadata')
 a={x['id']:x for x in now['gates']};b={x['id']:x for x in old['gates']}
 if (len(now['gates']),len(a),len(old['gates']),len(b))!=(31,31,30,30) or set(a)!=set(b)|{GATE}:
  raise ValueError('Historical release gate dropped/duplicated')
 for k in b:
  if k not in ('draft_semantics','text_completeness') and a[k]!=b[k]:
   raise ValueError(('Previously established gate changed',k))
 q=a[GATE];d=a['draft_semantics'];w=a['windows_runtime'];p=a['pronoun_contexts'];pol=now['test_policy']
 if (q.get('status'),q.get('previous_historical_reviews'),q.get('historical_rows_rechecked'),
     q.get('new_historical_reviews'),q.get('total_historical_reviews'),q.get('added_literals'),
     q.get('corrected_fragments'),q.get('verified_original_jvm_ldc_calls'),q.get('mapped_jvm_literal_count'),
     q.get('simulated_composed_texts'),q.get('changed_jvm_classes'))!=(
      'in_progress',617,47,114,731,13,9,669,205,60,3):
  raise ValueError('Unsupported v1066 text/JVM/review claims')
 if (q.get('changed_game_data_files'),q.get('new_jvm_executable_instructions'),q.get('native_windows_gameplay_tested'))!=(0,0,False):
  raise ValueError('Incorrect technical edit or in-game test claim')
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'),d.get('review_ledger'),d.get('status'))!=(
     3658,731,2927,'docs/API_SEMANTIC_REVIEW_1066.json','blocked'):
  raise ValueError('Wrong historical API review/debt counter')
 if (w.get('status'),w.get('native_gameplay_tested'),w.get('required_before_1_1'),w.get('testing_phase'))!=(
     'deferred_post_1_1',False,False,'after_1_1_release'):
  raise ValueError('Native game testing must happen after 1.1 release')
 if (pol.get('native_windows_gameplay'),pol.get('native_gameplay_required_before_1_1'),
     pol.get('post_release_gameplay_status'))!=('after_release_1.1',False,'not_started'):
  raise ValueError('User test policy changed without authorization')
 if set(pol['pre_release_checks'])!={'offline_text_review','csv_integrity','jvm_patch_integrity','installer_build','ci_regression'}:
  raise ValueError('Pre-release offline checks disabled')
 if (p.get('unresolved_count'),p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(186,555,742):
  raise ValueError('Getter or gender progress fabricated')
 if a['text_completeness']['status']!='in_progress' or any(x.get('status')=='completed' for x in now['gates']):
  raise ValueError('Premature claim of 1.1 completion')
 return {'release':'1.0.66','target':'1.1','reviewed_history':731,'history_remaining':2927,
   'new_reviews':114,'repeated_old_reviews_excluded':47,'release_gate_count':31,
   'getter_calls_unresolved':186,'native_game_testing_after_release':True,
   'gameplay_not_tested':True,'fully_translated':False}

def audit(root:Path,current:Path,previous:Path,prior_semantic:Path,semantic:Path)->dict:
 out=metadata(current,previous);actual=check(root)
 if (actual['new_unique_historical_reviews'],actual['corrected_ui_fragments'],actual['original_jvm_ldc_uses'],
     actual['rendered_combinations'],actual['unchanged_game_data_files'])!=(114,9,669,60,870):
  raise ValueError('Release gate not backed by actual data/code')
 repo=Path(__file__).resolve().parent.parent
 review_check(root,repo/'docs/SIM_INDUSTRY_TUTORIAL_REVIEW_1066.json',prior_semantic,semantic)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 p.add_argument('--prior-semantic',type=Path,required=True);p.add_argument('--semantic',type=Path,required=True)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
