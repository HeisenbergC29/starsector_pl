#!/usr/bin/env python3
"""Synthetic-only regression tests: no commercial game source is embedded."""
from __future__ import annotations
import importlib.util, json, pathlib, tempfile
from pathlib import Path

DIR=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('dynamic1030',DIR/'audit_dynamic_1030.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
spec2=importlib.util.spec_from_file_location('releasegates1030',DIR/'check_release_gates_1030.py')
gates=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(gates)

SYNTHETIC='''public class SyntheticDialog {
  public void first();
    Code:
       0: new           #1                  // class java/lang/StringBuilder
       3: getstatic     #2                  // Field com/fs/starfarer/api/util/Misc.STORY:Ljava/lang/String;
       6: ldc           #3                  // String  points
       8: invokevirtual #4                  // Method append:(Ljava/lang/String;)Ljava/lang/StringBuilder;
  public void second();
    Code:
       0: ldc           #5                  // String  point
       2: return
}'''.splitlines()

methods=mod.parse_methods(SYNTHETIC)
assert len(methods)==2 and methods[0][0].endswith('first();')
assert len(methods[0][1])==4 and len(methods[1][1])==2
# A local fake can demonstrate why no literal should be borrowed from a later method.
first=methods[0][1]
assert sum(mod.FIELD in x['raw'] for x in first)==1
assert mod.LITERAL.search(first[2]['raw']).group(1)==' points'
assert not any(mod.FIELD in x['raw'] for x in methods[1][1])

fake_gates={'schema_version':1,'target_version':'1.1','gates':[
 {'id':id,'status':'blocked','source':'synthetic'} for id in gates.REQUIRED]}
with tempfile.TemporaryDirectory() as folder:
    p=Path(folder);(p/'mod').mkdir();
    file=p/'gates.json';file.write_text(json.dumps(fake_gates))
    (p/'mod/mod_info.json').write_text(json.dumps({'version':'1.0.29','gameVersion':'0.98a-RC8'}))
    report=gates.check(p,file)
    assert len(report['blocked_gates'])==5 and not report['final_release_allowed']
    for should_block in ('1.1',):
        (p/'mod/mod_info.json').write_text(json.dumps({'version':should_block,'gameVersion':'0.98a-RC8'}))
        try:gates.check(p,file)
        except RuntimeError:pass
        else:raise AssertionError('incomplete final release was allowed')
    (p/'mod/mod_info.json').write_text(json.dumps({'version':'1.0.29','gameVersion':'0.98a-RC8'}))
    try:gates.check(p,file,strict=True)
    except RuntimeError:pass
    else:raise AssertionError('strict incomplete final release allowed')
    fake_gates['gates'][0]['status']='verified'
    file.write_text(json.dumps(fake_gates))
    try:gates.check(p,file)
    except AssertionError:pass
    else:raise AssertionError('missing evidence allowed')
print('Dynamic 1030 synthetic tests: PASS')
