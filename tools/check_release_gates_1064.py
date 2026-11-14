#!/usr/bin/env python3
"""Protect cumulative target 1.1 from unsupported completeness claims after 1.0.64."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1064 import check
from build_review_1064 import check as review_check
GATE='inspection_pathbase_jvm_1064'

def metadata(current:Path,previous:Path)->dict:
 new=json.loads(Path(current).read_text('utf8'));old=json.loads(Path(previous).read_text('utf8'))
 if any((o.get('schema_version'),o.get('target_version'))!=(1,'1.1') for o in (new,old)):
  raise ValueError('Not v1.1 release gate metadata')
 now=new['gates'];was=old['gates'];a={x['id']:x for x in now};b={x['id']:x for x in was}
 if (len(now),len(a),len(was),len(b))!=(29,29,28,28) or set(a)!=set(b)|{GATE}:
  raise ValueError('Cumulative gates missing, duplicated or renamed')
 if any(x.get('status')=='completed' for x in now):raise ValueError('1.1 claimed complete without native gameplay')
 for key in b:
  if key not in ('draft_semantics','text_completeness','windows_runtime') and a[key]!=b[key]:
   raise ValueError(('Historical approved release gate mutated',key))
 d=a['draft_semantics'];g=a[GATE];w=a['windows_runtime'];p=a['pronoun_contexts']
 if (d.get('status'),d.get('total_draft_rows'),d.get('reviewed_offline'),d.get('unresolved_count'),d.get('review_ledger'))!=(
  'blocked',3658,530,3128,'docs/API_SEMANTIC_REVIEW_1064.json'):
  raise ValueError('History coverage falsified')
 if (g.get('status'),g.get('previous_historical_reviews'),g.get('new_historical_reviews'),g.get('total_historical_reviews'),
   g.get('corrected_fragments'),g.get('verified_mapped_literals'),g.get('original_jvm_ldc_uses'),
   g.get('test_render_variants'),g.get('preserved_technical_category_keys'),g.get('changed_classes'))!=(
   'in_progress',482,48,530,9,56,150,25,3,2):
  raise ValueError('New audited translation work falsely reported')
 if (g.get('game_data_changed'),g.get('new_jvm_instruction_changes'),g.get('native_windows_gameplay_tested'))!=(0,0,False):
  raise ValueError('Unverified JVM or Windows gameplay change')
 if (w.get('native_gameplay_tested'),w.get('status'),a['text_completeness'].get('status'))!=(False,'blocked','in_progress'):
  raise ValueError('Windows UI and text completeness falsely closed')
 if (p.get('unresolved_count'),p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(186,555,742):
  raise ValueError('Getter/dialogue debt changed without evidence')
 return {'release':'1.0.64','target':'1.1','target_blocked':True,'total_release_gates':29,
  'reviewed_historical_api':530,'remaining_historical_api':3128,
  'unreviewed_getter_calls':186,'raw_dialogue_gender_placeholders':1953,
  'native_windows_gameplay_tested':False}

def audit(worktree:Path,current:Path,previous:Path,old_review:Path,new_review:Path)->dict:
 info=metadata(current,previous);source=check(worktree)
 if (source['historical_api_reviewed_total'],source['original_jvm_ldc_uses'],source['corrected_literals'],source['rendered_combinations'])!=(530,150,9,25):
  raise ValueError('New release gates not supported by original data')
 record=Path(__file__).resolve().parent.parent/'docs/INSPECTION_PATHBASE_REVIEW_1064.json'
 review_check(worktree,record,old_review,new_review)
 return info

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 p.add_argument('--prior-semantic',type=Path,required=True);p.add_argument('--semantic',type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(audit(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
