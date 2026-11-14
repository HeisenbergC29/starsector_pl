#!/usr/bin/env python3
"""Verify v1.0.65 contributions and user-chosen post-1.1 native game test policy.

CI builds, JVM integrity checks and file audits still occur pre-release.
Running and visually testing the game is expressly NOT a prerequisite for 1.1.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1065 import check
from build_review_1065 import check as review_check
GATE='marketcmd_raid_bombardment_1065'

def metadata(current:Path,previous:Path)->dict:
 now=json.loads(Path(current).read_text('utf8'))
 old=json.loads(Path(previous).read_text('utf8'))
 if any((x.get('schema_version'),x.get('target_version'))!=(1,'1.1') for x in (now,old)):
  raise ValueError('Unknown release-gate schema/target')
 n=now['gates'];p=old['gates'];a={x['id']:x for x in n};b={x['id']:x for x in p}
 if (len(n),len(a),len(p),len(b))!=(30,30,29,29) or set(a)!=set(b)|{GATE}:
  raise ValueError('Existing release gates silently dropped or new gate not unique')
 for key in b:
  if key not in ('draft_semantics','text_completeness','windows_runtime') and a[key]!=b[key]:
   raise ValueError(('Prior approved release-gate evidence changed',key))
 d=a['draft_semantics'];q=a[GATE];w=a['windows_runtime'];z=a['text_completeness']
 if (d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'),
     d.get('review_ledger'),d.get('status'))!=(3658,617,3041,'docs/API_SEMANTIC_REVIEW_1065.json','blocked'):
  raise ValueError('Historical API completion falsely claimed')
 if (q.get('previous_historical_reviews'),q.get('new_historical_reviews'),q.get('total_historical_reviews'),
     q.get('mapped_literal_count'),q.get('original_jvm_ldc_uses'),q.get('grammar_fragments_repaired'),
     q.get('rendered_combinations'),q.get('changed_jvm_classes'),q.get('status'))!=(530,87,617,111,363,17,55,1,'in_progress'):
  raise ValueError('MarketCMD original JVM review numbers not supported')
 if (q.get('changed_mod_data_files'),q.get('new_jvm_executable_instructions'),q.get('native_windows_gameplay_tested'))!=(0,0,False):
  raise ValueError('Unsupported game code/data or gameplay test claim')
 if (w.get('status'),w.get('native_gameplay_tested'),w.get('required_before_1_1'),w.get('testing_phase'))!=(
      'deferred_post_1_1',False,False,'after_1_1_release'):
  raise ValueError('User chose game testing ONLY after 1.1 release')
 pol=now.get('test_policy',{})
 if (pol.get('native_windows_gameplay'),pol.get('native_gameplay_required_before_1_1'),
     pol.get('post_release_gameplay_status'),pol.get('user_decision_date'))!=(
      'after_release_1.1',False,'not_started','2026-11-14'):
  raise ValueError('Game testing timing policy not recorded correctly')
 if set(pol.get('pre_release_checks',[]))!={
  'offline_text_review','csv_integrity','jvm_patch_integrity',
  'installer_build','ci_regression'}:
  raise ValueError('Offline pre-release checks cannot be suppressed')
 if z.get('status')!='in_progress' or z.get('native_gameplay_tested',False):
  raise ValueError('Unfinished localization or game testing falsely closed')
 ctx=a['pronoun_contexts']
 if (ctx.get('unresolved_count'),ctx.get('reviewed_rules_rows_offline'),ctx.get('removed_visible_gender_variable_refs'))!=(186,555,742):
  raise ValueError('Getter/dialogue progress was falsely advanced')
 if any(x.get('status')=='completed' for x in n if x['id']!= 'windows_runtime'):
  raise ValueError('v1.1 completion claimed without completing text review')
 return {'release':'1.0.65','target':'1.1','fully_translated':False,
  'release_gates':len(n),'historical_api_reviewed':617,'historical_api_pending':3041,
  'remaining_jvm_getters':186,'dynamic_gender_refs':1953,
  'native_gameplay_after_1_1':True,'native_gameplay_tested':False}

def audit(root:Path,current:Path,previous:Path,prior_semantic:Path,semantic:Path)->dict:
 result=metadata(current,previous)
 actual=check(root)
 if (actual['historical_api_reviewed_total'],actual['original_jvm_ldc_uses'],actual['repaired_literals'],actual['rendered_combinations'],actual['unchanged_game_data_files'])!=(617,363,17,55,870):
  raise ValueError('Gate not supported by real game files')
 repo=Path(__file__).resolve().parent.parent
 review_check(root,repo/'docs/MARKETCMD_REVIEW_1065.json',prior_semantic,semantic)
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 p.add_argument('--prior-semantic',type=Path,required=True);p.add_argument('--semantic',type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(audit(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
