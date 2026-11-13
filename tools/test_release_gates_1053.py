#!/usr/bin/env python3
"""Negative-test blocked 1.1 conditions in the 1.0.53 OBF-only release."""
from __future__ import annotations
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1053 import audit

def run(root,gates,previous,ledger):
 source=json.loads(Path(gates).read_text('utf8'))
 audits={};ids=lambda obj:{x['id']:x for x in obj['gates']}
 cases={
  'claim_native_windows_tested':lambda x:ids(x)['windows_runtime'].update(native_gameplay_tested=True),
  'claim_complete_translation':lambda x:ids(x)['text_completeness'].update(status='completed'),
  'hide_unreviewed_pronouns':lambda x:ids(x)['pronoun_contexts'].update(unresolved_count=0),
  'falsely_raise_api_review':lambda x:ids(x)['draft_semantics'].update(reviewed_offline=3658),
  'remove_blocked_recovery_ui':lambda x:ids(x)['obf_recovery_1053'].update(status='completed'),
  'claim_executable_jvm_rewrite':lambda x:ids(x)['obf_recovery_1053'].update(executable_java_bytecode_changed=True),
  'drop_recovery_literal':lambda x:ids(x)['obf_recovery_1053'].update(new_obf_entries=2),
  'missing_bar_getter_proof':lambda x:ids(x)['bar_shared_her_1052'].update(reviewed_gender_getter_callsites=0),
  'relocate_api_map_without_audit':lambda x:ids(x)['obf_recovery_1053'].update(api_map_changed=True),
 }
 audit(root,gates,previous,ledger)
 for name,mutate in cases.items():
  damaged=copy.deepcopy(source);mutate(damaged)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'release_gates.json';p.write_text(json.dumps(damaged))
   try:audit(root,p,previous,ledger)
   except (ValueError,AssertionError):audits[name]='REJECTED'
   else:raise AssertionError(('False 1.1 readiness accepted',name))
 if len(audits)!=9:raise ValueError('Incomplete invalid-gate test corpus')
 return {'deliberately_invalid_1_1_gates_rejected':len(audits),'cases':audits,'1_1_remains_blocked':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',required=True,type=Path)
 p.add_argument('--previous',required=True,type=Path);p.add_argument('--ledger',required=True,type=Path)
 a=p.parse_args();print(json.dumps(run(a.worktree,a.gates,a.previous,a.ledger),indent=2))
