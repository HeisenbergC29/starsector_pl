#!/usr/bin/env python3
"""Exact verifiable delta for 1.0.41 and (with private game JARs) bytecode audit."""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,sys,zipfile
from pathlib import Path
from apply_1041 import FIELDS,plan,readmap,REPLACEMENTS

API_ORIGINAL_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
API_1040_SHA='5e76f0ba08927564b35ded6ffa5dfba7c32134df152394c7cca19f5e96bf3ef5'
API_1041_SHA='be752bc07ca3965435ad34bab2e12febd80a7883818a430d8c007999b562e5c9'
OBF_1040_SHA='03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify_delta(old,after):
    affected,groups,digest=plan(old)
    if len(old)!=len(after) or len(old)!=5257:raise AssertionError('wrong map row count')
    targets={(cls,en):(pol,new,status) for cls,en,pol,new,status in affected}
    if len(targets)!=77:raise AssertionError('duplicate affected key')
    allkeys=set()
    modified=[]
    for idx,(a,b) in enumerate(zip(old,after)):
        key=(a['source_class'],a['english_literal'])
        if key in allkeys:raise AssertionError(('duplicate row key',key))
        allkeys.add(key)
        if (a['source_class'],a['english_literal'],a['status'])!=(b['source_class'],b['english_literal'],b['status']):
            raise AssertionError(('technical key or status changed',idx))
        if key in targets:
            expected=targets[key][1]
            if b['polish_ascii_draft']!=expected or a['polish_ascii_draft']==expected:
                raise AssertionError(('mismatching corrected translation',idx,key))
            for value in (1,2,5):
                actual=expected.replace('%s',str(value))
                if any(p in actual for p in (f'{value} jednostek',f'{value} punktow',f'{value} lat swietlnych')):
                    raise AssertionError(('bad numeric inflection',idx,value))
            modified.append(key)
        elif a!=b:raise AssertionError(('unapproved mapping modification',idx))
    if len(modified)!=77 or set(modified)!=set(targets):raise AssertionError('numeric coverage incomplete')
    if not all(x['polish_ascii_draft'].isascii() for x in after):raise AssertionError('non-ASCII UI text')
    return {'changed_map_rows':77,'changed_classes':len({x[0] for x in modified}),
        'groups':groups,'map_rows':len(after),'review_hash':digest,
        'numeric_samples':{'unit':'1 jedn.','points':'1 pkt','light_year':'1 l. sw.'}}

def verify(root,original=None,patched=None,previous_zip=None):
    root=Path(root);td=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    before=readmap(td/'TLUMACZENIA_JAR_1040.csv');after=readmap(td/'TLUMACZENIA_JAR_1041.csv')
    out=verify_delta(before,after)
    code=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
    assert 'const version = "1041"' in code and 'const exeVersion = "1.0.41"' in code
    assert '"1038", "1040", version}' in code
    assert 'if hash(current) != r.NewSHA256 {' in code
    assert 'installed JAR has unexpected ZIP bytes; refusing no-op on damaged or repacked archive' in code
    assert 'const edition = "1.0.41"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
    meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
    assert meta['version']=='1.0.41' and meta['gameVersion']=='0.98a-RC8' and len(meta['replace'])==41
    data={p.relative_to(root/'mod').as_posix():p.read_bytes() for p in (root/'mod/data').rglob('*') if p.is_file()}
    assert len(data)==870 and all(v.isascii() for v in data.values())
    if previous_zip:
        with zipfile.ZipFile(previous_zip) as z:
            previous={k.removeprefix('Starsector_PL_ASCII/'):z.read(k) for k in z.namelist() if k.startswith('Starsector_PL_ASCII/data/')}
        assert data==previous, 'non-translation assets changed unexpectedly'
        out['unchanged_data_files']=870
    if original or patched:
        assert original and patched
        if sha(original)!=API_ORIGINAL_SHA or sha(patched)!=API_1041_SHA:
            raise AssertionError('unexpected original or patched JAR hashes')
        sys.path.insert(0,str(Path(__file__).parent))
        from verify_story_1033 import class_entries,texts,proof_class_files
        allmap={(x['source_class'],x['english_literal']):x['polish_ascii_draft'] for x in after}
        proof=proof_class_files(Path(original),Path(patched),allmap)
        assert proof['modified_classes']==938 and proof['mapped_string_constants']==5255 and proof['executables_untouched']
        with zipfile.ZipFile(original) as o,zipfile.ZipFile(patched) as p:
            for cls,en,was,new,status in plan(before)[0]:
                path=cls.replace('.','/')+'.class'
                a=texts(class_entries(o.read(path))[0]);b=texts(class_entries(p.read(path))[0]);
                if en not in a or new not in b:raise AssertionError(('missing exact JVM translation',cls,en))
        out['jar_proof']=proof
        out['original_jar_sha256']=sha(original)
        out['patched_jar_sha256']=sha(patched)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--original-api',type=Path);p.add_argument('--patched-api',type=Path);p.add_argument('--previous-zip',type=Path)
    a=p.parse_args();print(json.dumps(verify(a.worktree,a.original_api,a.patched_api,a.previous_zip),indent=2))
