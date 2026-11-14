#!/usr/bin/env python3
"""v1.0.63 requires history-preserving review and refuses false Starsector 1.1 completion."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1063 import check
from build_review_1063 import check as review_check
GATE='luddic_path_cells_jvm_1063'

def metadata(current:Path,previous:Path)->dict:
 new=json.loads(Path(current).read_text('utf8'));old=json.loads(Path(previous).read_text('utf8'))
 if any((d.get('schema_version'),d.get('target_version'))!=(1,'1.1') for d in (new,old)):
  raise ValueError('Not the target 1.1 release gate schema')
 now=new['gates'];prior=old['gates'];a={x['id']:x for x in now};b={x['id']:x for x in prior}
 if (len(now),len(a),len(prior),len(b))!=(28,28,27,27) or set(a)!=set(b)|{GATE}:
  raise ValueError('Cumulative release gate altered or duplicated')
 if any(x.get('status')=='completed' for x in now):raise ValueError('1.1 declared finished without native tests')
 for k in b:
  if k not in ('draft_semantics','text_completeness','windows_runtime') and a[k]!=b[k]:
   raise ValueError(('Older immutable 1.1 gate changed',k))
 draft=a['draft_semantics'];g=a[GATE];p=a['pronoun_contexts'];w=a['windows_runtime']
 if (draft.get('total_draft_rows'),draft.get('reviewed_offline'),draft.get('unresolved_count'),
     draft.get('review_ledger'),draft.get('status'))!=(3658,482,3176,'docs/API_SEMANTIC_REVIEW_1063.json','blocked'):
  raise ValueError('API historical coverage falsified')
 if (g.get('status'),g.get('previous_historical_reviews'),g.get('new_historical_reviews'),g.get('total_historical_reviews'),
     g.get('repaired_existing_literals'),g.get('mapped_source_literals'),g.get('original_jvm_ldc_uses'),
     g.get('rendered_dynamic_variants'),g.get('technical_category_keys_restored'),g.get('changed_classes'))!=(
      'in_progress',447,35,482,14,47,83,60,1,1):
  raise ValueError('API translation/JVM evidence not supported')
 if (g.get('game_data_changed'),g.get('new_jvm_instruction_changes'),g.get('native_windows_gameplay_tested'))!=(0,0,False):
  raise ValueError('Game data, code or live-test gate invalid')
 if (p.get('unresolved_count'),p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(186,555,742):
  raise ValueError('Historical getter/dialogue counts improperly advanced')
 if (w.get('native_gameplay_tested'),w.get('status'),a['text_completeness'].get('status'))!=(False,'blocked','in_progress'):
  raise ValueError('Windows live testing falsely completed')
 return {'release':'1.0.63','target':'1.1','blocked':True,'gates':28,
  'api_reviewed':482,'api_pending':3176,'dialogue_rows_reviewed':555,'getter_calls_pending':186,
  'gender_tokens_pending':1953,'native_windows_gameplay_tested':False}

def audit(root:Path,current:Path,previous:Path,old_semantic:Path,new_semantic:Path)->dict:
 result=metadata(current,previous)
 actual=check(root)
 if (actual['historical_api_reviewed_total'],actual['original_jvm_ldc_uses'],actual['repaired_literals'],actual['rendered_combinations'])!=(482,83,14,60):
  raise ValueError('Gate not supported by installed mappings')
 local=Path(__file__).resolve().parent.parent/'docs/LUDDIC_CELLS_REVIEW_1063.json'
 review_check(root,local,old_semantic,new_semantic)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 p.add_argument('--prior-semantic',required=True,type=Path);p.add_argument('--semantic',required=True,type=Path)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
