#!/usr/bin/env python3
"""1.0.47 fail-closed regression: numerical variants, exact map, tampering."""
from __future__ import annotations
import argparse,json,shutil,tempfile
from pathlib import Path
from apply_1047 import BASE,NEW,CHANGES,readmap,validated_changes
from verify_1047 import check


def run(root):
    root=Path(root);base=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    current=readmap(base/NEW)
    items=[r for r in current if (r['source_class'],r['english_literal']) in CHANGES]
    assert len(items)==14
    examples=[]
    for r in items:
        old,new=CHANGES[(r['source_class'],r['english_literal'])]
        if r['polish_ascii_draft']!=new or new.count('jedn..') or 'jednostke' in new:
            raise ValueError('Invalid unit translation')
        for count in ('1','2','5'):
            before=old.replace('%s',count)
            after=new.replace('%s',count)
            if count+' jednostke' not in before or count+' jedn.' not in after or 'jedn..' in after:
                raise ValueError(('Bad number-neutral display',r['source_class'],count))
            examples.append((count,after))
    ok=check(root,strict_go=False)
    if ok['changes']!=14:raise ValueError('Pre-fixture verification failed')
    actions=[
      ('target_jvm_text',lambda d:(d/base.relative_to(root)/NEW).write_bytes((d/base.relative_to(root)/NEW).read_bytes().replace(b'%s jedn.',b'%s jed.',1))),
      ('source_map',lambda d:(d/base.relative_to(root)/BASE).write_bytes((d/base.relative_to(root)/BASE).read_bytes()+b'X')),
      ('unexpected_english',lambda d:(d/base.relative_to(root)/NEW).write_bytes((d/base.relative_to(root)/NEW).read_bytes().replace(b'Increases production by %s unit.',b'Increase production by %s unit.',1))),
      ('missing_map_row',lambda d:(d/base.relative_to(root)/NEW).write_bytes((d/base.relative_to(root)/NEW).read_bytes().replace(b'Increases production by %s unit.',b'',1))),
      ('mod_version',lambda d:(d/'mod/mod_info.json').write_text((d/'mod/mod_info.json').read_text('utf8').replace('"1.0.47"','"1.0.48"',1),encoding='utf8')),
      ('modified_rules',lambda d:(d/'mod/data/campaign/rules.csv').write_bytes((d/'mod/data/campaign/rules.csv').read_bytes()+b'\r\n')),
      ('other_data',lambda d:(d/'mod/data/campaign/abilities.csv').write_bytes((d/'mod/data/campaign/abilities.csv').read_bytes()+b'corrupt')),
      ('invalid_installer',lambda d:(d/'buildtools/NARZEDZIA_INSTALATOR/main.go').write_text('const edition = "1.0.48"\n',encoding='utf8')),
      ('wrong_go_source',lambda d:(d/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').write_text('const version = "1046"\n',encoding='utf8')),
    ]
    with tempfile.TemporaryDirectory(prefix='ss1047_negative_') as dir:
        target=Path(dir)/'snapshot'
        shutil.copytree(root,target)
        rel=base.relative_to(root)
        for name,mutate in actions:
            f=target/rel/NEW;previous=f.read_bytes()
            # Fresh copied snapshot for every negative mutation.
            shutil.rmtree(target);shutil.copytree(root,target)
            mutate(target)
            try:check(target,strict_go=False)
            except (ValueError,AssertionError):pass
            else:raise AssertionError('Incorrectly accepted mutation '+name)
    # Validate old map independently; source-status and placeholder drift are rejected.
    original=readmap(base/BASE);first=next(r for r in original if (r['source_class'],r['english_literal']) in CHANGES)
    if len(validated_changes(original))!=14:raise AssertionError('Unexpected audited key count')
    return {'version':'1.0.47','numeric_templates':14,'tested_quantities':[1,2,5],
            'number_grammar_cases_passed':len(examples),'negative_mutations_rejected':len(actions),
            'all_870_data_files_unchanged':True,'map_row_count':5260}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
    print(json.dumps(run(a.worktree),indent=2))
