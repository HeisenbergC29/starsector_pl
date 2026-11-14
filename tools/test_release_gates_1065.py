#!/usr/bin/env python3
"""Negative metadata tests for complete translational vs deferred gameplay gates."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1065 import metadata,audit

def test(root:Path,current:Path,previous:Path,prior_semantic:Path,semantic:Path)->dict:
 base=json.loads(Path(current).read_text('utf8'))
 metadata(current,previous);rejected=[]
 def reject(name,mutator):
  data=copy.deepcopy(base);mutator(data)
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'bad.json';path.write_text(json.dumps(data)+'\n',encoding='utf8')
   try:metadata(path,previous)
   except (ValueError,KeyError,TypeError):rejected.append(name)
   else:raise AssertionError(('Invalid v1.1 gate accepted',name))
 def gate(d,id):return next(x for x in d['gates'] if x['id']==id)
 reject('game testing falsely completed',lambda d:gate(d,'windows_runtime').update(native_gameplay_tested=True))
 reject('game testing reinstated as 1.1 prerequisite',lambda d:gate(d,'windows_runtime').update(required_before_1_1=True))
 reject('gameplay testing status blocked instead of deferred',lambda d:gate(d,'windows_runtime').update(status='blocked'))
 reject('pre-release technical checks removed',lambda d:d['test_policy'].update(pre_release_checks=[]))
 reject('postrelease game test faked as passed',lambda d:d['test_policy'].update(post_release_gameplay_status='passed'))
 reject('unreviewed API falsely counted as finished',lambda d:gate(d,'draft_semantics').update(unresolved_count=0))
 reject('MarketCMD historical rows inflated',lambda d:gate(d,'marketcmd_raid_bombardment_1065').update(new_historical_reviews=3658))
 reject('MarketCMD game data falsely modified',lambda d:gate(d,'marketcmd_raid_bombardment_1065').update(changed_mod_data_files=1))
 reject('MarketCMD compiler code falsely modified',lambda d:gate(d,'marketcmd_raid_bombardment_1065').update(new_jvm_executable_instructions=1))
 reject('historical prior gate modified',lambda d:gate(d,'inspection_pathbase_jvm_1064').update(status='completed'))
 reject('v1.1 historical API falsely completed',lambda d:gate(d,'draft_semantics').update(status='completed'))
 reject('pronoun/JVM getter backlog suppressed',lambda d:gate(d,'pronoun_contexts').update(unresolved_count=0))
 result=audit(root,current,previous,prior_semantic,semantic)
 if len(rejected)!=12 or result['historical_api_reviewed']!=617:raise ValueError('Gate mutation coverage wrong')
 return {'release':'1.0.65','invalid_gate_states_rejected':len(rejected),
  'gameplay_tests_must_wait_until_post_1_1':True,'mutation_cases':rejected}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--gates',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
 p.add_argument('--prior-semantic',type=Path,required=True);p.add_argument('--semantic',type=Path,required=True)
 a=p.parse_args();print(json.dumps(test(a.worktree,a.gates,a.previous,a.prior_semantic,a.semantic),indent=2))
