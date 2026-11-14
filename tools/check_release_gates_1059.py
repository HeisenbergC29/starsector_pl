#!/usr/bin/env python3
"""Fail-closed 1.1 release-gates while recording concrete API UI progress."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from verify_1059 import check
NEW_ID='monthly_report_ui_1059'

def metadata(current:Path,prior:Path)->dict:
 now=json.loads(Path(current).read_text('utf8'));old=json.loads(Path(prior).read_text('utf8'))
 a=now.get('gates',[]);b=old.get('gates',[])
 d={x['id']:x for x in a};e={x['id']:x for x in b}
 if any((x.get('schema_version'),x.get('target_version'))!=(1,'1.1') for x in [now,old]):
  raise ValueError('Release-gate schema has changed')
 if (len(a),len(d),len(b),len(e))!=(24,24,23,23) or set(d)!=set(e)|{NEW_ID}:
  raise ValueError('Missing or duplicate release gate')
 if any(x.get('status')=='completed' for x in a):raise ValueError('Premature 1.1 completion')
 for k in e:
  if k not in ('text_completeness','windows_runtime') and d[k]!=e[k]:
   raise ValueError(('Previously approved gate changed',k))
 f=d[NEW_ID];api=d['draft_semantics'];p=d['pronoun_contexts'];w=d['windows_runtime']
 if (f.get('status'),f.get('new_class_scoped_literals'),f.get('revised_previously_reviewed_literal'),f.get('jvm_callsites_verified_original'),f.get('affected_classes'),f.get('prior_historical_api_reviews'))!=('in_progress',6,1,10,1,391):
  raise ValueError('New Java UI audit evidence is invalid')
 if (f.get('data_file_changes'),f.get('new_executable_bytecode_changes'),f.get('native_windows_gameplay_tested'))!=(0,0,False):
  raise ValueError('Unsupported logic or gameplay claim')
 if (api.get('reviewed_offline'),api.get('unresolved_count'),api.get('total_draft_rows'),api.get('review_ledger'),api.get('status'))!=(391,3267,3658,'docs/API_SEMANTIC_REVIEW_1055.json','blocked'):
  raise ValueError('Historical API reviews falsely inflated or altered')
 if (p.get('unresolved_count'),p.get('reviewed_rules_rows_offline'),p.get('removed_visible_gender_variable_refs'))!=(186,555,742):
  raise ValueError('Untested getter/dialogue progress falsely advanced')
 if w.get('native_gameplay_tested') is not False or w.get('status')!='blocked' or d['text_completeness'].get('status')!='in_progress':
  raise ValueError('Required final runtime testing prematurely marked complete')
 return {'release':'1.0.59','version_1_1_blocked':True,'gates':24,'new_java_ui_literals':6,
         'corrected_composed_ui_templates':1,'historical_api_review_count_unchanged':391,
         'historical_api_outstanding':3267,'jvm_getters_outstanding':186,
         'remaining_dialogue_gender_placeholders':1953,'native_windows_gameplay_tested':False}

def audit(root:Path,current:Path,prior:Path)->dict:
 result=metadata(current,prior);v=check(root)
 if (v['class_scoped_new_literals'],v['revised_old_literal'],v['monthly_report_quantity_renderings_checked'])!=(6,1,15):
  raise ValueError('No matching actual API translation evidence')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path);p.add_argument('--previous',required=True,type=Path)
 a=p.parse_args();print(json.dumps(audit(a.worktree,a.gates,a.previous),indent=2))
