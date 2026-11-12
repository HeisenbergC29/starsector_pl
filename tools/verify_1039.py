#!/usr/bin/env python3
"""Full inverse and non-text-delta proof for 1.0.39 dialogue translations."""
from __future__ import annotations
import argparse,hashlib,io,csv,json,zipfile
from pathlib import Path
from apply_1039 import PATCHES,PRONOUN,SOURCE,OLD_SHA,NEW_SHA,patch_bytes,sha
from apply_1034 import rows_with_spans

def revert(blob):
    if sha(blob)!=NEW_SHA:raise ValueError('Unexpected 1.0.39 checksum')
    spans=rows_with_spans(blob);pieces=[];prev=0;found=set()
    for start,end,row in spans[1:]:
        k=row[0]
        if k not in PATCHES:continue
        if k in found:raise AssertionError(('Repeated ID',k))
        found.add(k);chunk=blob[start:end]
        for before,after in reversed(PATCHES[k]):
            b,a=after.encode('ascii'),before.encode('ascii')
            if chunk.count(b)!=1:raise AssertionError(('Nonreversible',k,after))
            chunk=chunk.replace(b,a,1)
        pieces.extend((blob[prev:start],chunk));prev=end
    pieces.append(blob[prev:]);prior=b''.join(pieces)
    assert found==set(PATCHES) and sha(prior)==OLD_SHA
    return prior

def parse(blob):
    with io.StringIO(blob.decode('ascii'),newline='') as f: rows=list(csv.DictReader(f))
    assert len(rows)==11107
    return rows

def verify(root,previous=None):
    mod=root/'mod';target=mod/SOURCE;blob=target.read_bytes();assert sha(blob)==NEW_SHA
    prior=revert(blob);again,stats=patch_bytes(prior);assert again==blob
    assert stats['changed_rows']==62 and stats['precise_replacements']==68
    assert stats['removed_pronoun_placeholders']==77 and stats['remaining']==0
    old=parse(prior);new=parse(blob)
    for i,(a,b) in enumerate(zip(old,new)):
        assert a['id']==b['id'],('changed id',i)
        actual={k for k in a if a[k]!=b[k]}
        required={'text'} if a['id'] in PATCHES else set()
        assert actual==required,(i,a['id'],actual,required)
        if required:assert not PRONOUN.search(b['text'].encode('ascii'))
    data={p.relative_to(mod/'data').as_posix():p.read_bytes() for p in (mod/'data').rglob('*') if p.is_file()}
    assert len(data)==870 and all(z.isascii() for z in data.values())
    if previous:
        with zipfile.ZipFile(previous) as z:
            assert z.testzip() is None
            olddata={k.removeprefix('Starsector_PL_ASCII/data/'):z.read(k) for k in z.namelist() if k.startswith('Starsector_PL_ASCII/data/')}
        assert set(data)==set(olddata) and len(olddata)==870
        changed=[k for k in data if data[k]!=olddata[k]]
        assert changed==['campaign/rules.csv'],changed
        assert olddata['campaign/rules.csv']==prior
    info=json.loads((mod/'mod_info.json').read_text('utf8'))
    assert info['version']=='1.0.39' and info['gameVersion']=='0.98a-RC8' and len(info['replace'])==41
    assert all((mod/k).is_file() for k in info['replace'])
    assert 'STARSECTOR PL ASCII 1.0.39' in (mod/'CZYTAJ.txt').read_text('utf8')
    api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
    obf=root/'buildtools/NARZEDZIA_OBF'
    assert 'const version = "1038"' in (api/'main.go').read_text('utf8')
    assert 'const currentPatchState = "patched 10133"' in (obf/'main.go').read_text('utf8')
    assert 'const edition = "1.0.39"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
    hashes={
        'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go':'d3744cb10f338a614d745b8ab04ae4a0ab2ae33f917f9d52cd91b3773fcea700',
        'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1038.csv':'9f6bdfcffbb020a848269490aab6cb948c7bdf3312e416b853f22d4f00ad49cb',
        'buildtools/NARZEDZIA_OBF/main.go':'f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc',
        'buildtools/NARZEDZIA_OBF/TLUMACZENIA_OBF_10133.csv':'f2ffdb534d870a49fce81dea47b4ebbac8fdccc218b79d5bed0f3752485cd484',
    }
    assert all(sha((root/k).read_bytes())==v for k,v in hashes.items()),'Unexpected Java patcher/map changes'
    with (api/'translations/TLUMACZENIA_JAR_1038.csv').open(encoding='utf8',newline='') as ff:
        assert len(list(csv.DictReader(ff)))==5254
    from importlib.util import spec_from_file_location,module_from_spec
    path=root/'maintenance/check_rules_options.py';spec=spec_from_file_location('rule_test',path);mdl=module_from_spec(spec);spec.loader.exec_module(mdl)
    n,errors=mdl.audit(blob);assert n==7371 and not errors,(n,errors[:3])
    return {**stats,'total_csv_records':len(new),'verified_options':n,'other_data_files_unchanged':869,'reverted_sha256':sha(prior),'jvm_map':'unchanged_since_1038'}

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('worktree',type=Path);pa.add_argument('--previous-zip',type=Path);a=pa.parse_args()
    print(json.dumps(verify(a.worktree,a.previous_zip),indent=2))
