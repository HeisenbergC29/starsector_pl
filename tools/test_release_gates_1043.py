#!/usr/bin/env python3
"""Try to falsely declare open 1.1 requirements satisfied; must reject all 15."""
import argparse,copy,json,tempfile
from pathlib import Path
from check_release_gates_1043 import validate_gates,LEDGERS

def test(root,gates,ledgers):
    data=json.loads(Path(gates).read_text('utf8'));byid={r['id']:r for r in data['gates']}
    assert validate_gates(root,gates,ledgers)['all_release_1_1_gates_still_open']
    mods=[('story complete','story_contexts','status','completed'),('story Windows count','story_contexts','pending_windows_ui',0),
         ('pronoun complete','pronoun_contexts','status','completed'),('JVM pending cleared','pronoun_contexts','unresolved_count',0),
         ('JVM UI claimed','pronoun_contexts','pending_windows_ui_java_getter_calls',0),('shared her claimed fixed','pronoun_contexts','shared_her_conflict_open',False),
         ('rules pending cleared','pronoun_contexts','pending_windows_ui_rules_rows',0),('rules reviews inflated','pronoun_contexts','reviewed_rules_rows_offline',185),
         ('API draft done','draft_semantics','unresolved_count',0),('API reviews inflated','draft_semantics','reviewed_offline',3658),
         ('numeric Windows falsely done','numeric_quantities','pending_windows_ui',0),('punctuation Windows falsely done','punctuation_regression','pending_windows_ui',0),
         ('new rules falsely done','rules_possessives','pending_windows_ui',0),('new rules reviews inflated','rules_possessives','reviewed_rows_offline',32),
         ('runtime falsely tested','windows_runtime','native_gameplay_tested',True)]
    with tempfile.TemporaryDirectory() as temp:
        for label,gid,key,value in mods:
            j=copy.deepcopy(data);next(x for x in j['gates'] if x['id']==gid)[key]=value
            f=Path(temp)/'wrong.json';f.write_text(json.dumps(j),'utf8')
            try:validate_gates(root,f,ledgers)
            except (AssertionError,ValueError,KeyError):continue
            raise AssertionError('Falsely accepted: '+label)
    return {'forged_release_gate_scenarios_rejected':len(mods),'all_release_1_1_gates_open':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--gates',type=Path,required=True)
    p.add_argument('--ledger34',type=Path);p.add_argument('--ledger35',type=Path);p.add_argument('--ledger39',type=Path);p.add_argument('--ledger',type=Path)
    x=p.parse_args();l=[x.ledger34,x.ledger35,x.ledger39,x.ledger]
    if any(y is None for y in l):l=[x.gates.parent/Path(y).name for y in LEDGERS]
    print(json.dumps(test(x.worktree,x.gates,l),indent=2))
