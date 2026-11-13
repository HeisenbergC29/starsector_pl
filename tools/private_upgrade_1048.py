#!/usr/bin/env python3
"""Real private original-JAR regression and 1047->1048 upgrade; NEVER publishes JAR.

Uses SHA-pinned user-supplied Starsector 0.98a-RC8 originals and public Go
patchers built for Linux. Operates only on temp copies of the original game.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,tempfile,zipfile
from pathlib import Path
from private_jar_integration_1046 import ORIGINAL_SHA,sha,invoke,verify_jar,verify_class
from apply_1048 import plan,readmap,OLD

EXPECTED_OLD='98cc36aec4aa87e37717082469704f973ad7a91f51b7d0222a10a18770e2a277'

def run(original_api,original_obf,old_bin,new_bin,obf_bin,prior_map):
    paths=[Path(x).resolve() for x in (original_api,original_obf,old_bin,new_bin,obf_bin)]
    origapi,origobf,old,new,obf=paths
    if sha(origapi)!=ORIGINAL_SHA['API'] or sha(origobf)!=ORIGINAL_SHA['OBF']:
        raise ValueError('Incorrect original proprietary Starsector JAR hash')
    for f in (old,new,obf):
        if not f.is_file() or f.stat().st_size<4_000_000:raise ValueError('Missing/broken Go patcher binary')
    with tempfile.TemporaryDirectory(prefix='ss1047_private_') as rootname:
        root=Path(rootname)
        def makecore(tag):
            core=root/tag;core.mkdir()
            api=core/'starfarer.api.jar';obfj=core/'starfarer_obf.jar'
            shutil.copy2(origapi,api);shutil.copy2(origobf,obfj)
            return core,api,obfj
        clean,cleanapi,cleanobf=makecore('fresh')
        r=invoke(new,clean,'--apply')
        if r.returncode:raise ValueError(('Fresh 1.0.48 API install failed',r.stderr[-1300:]))
        freshsha=sha(cleanapi)
        java=verify_jar(origapi,cleanapi,'API')
        if java['changed_classes']!=938:raise ValueError(('Changed Java class count',java['changed_classes']))
        r=invoke(obf,clean,'--apply')
        if r.returncode:raise ValueError(('Fresh OBF install failed',r.stderr[-700:]))
        obfjar=verify_jar(origobf,cleanobf,'OBF')
        if obfjar['changed_classes']!=539:raise ValueError('OBF Java class-count changed')
        upgrade,api,obfj=makecore('upgrade')
        r=invoke(obf,upgrade,'--apply')
        if r.returncode:raise ValueError('OBF prerequisite failed')
        r=invoke(old,upgrade,'--apply')
        if r.returncode or sha(api)!=EXPECTED_OLD:
            raise ValueError(('1.0.47 original-version install failed',r.stderr[-900:],sha(api)))
        old_bytes=api.read_bytes()
        r=invoke(new,upgrade,'--apply')
        if r.returncode or sha(api)!=freshsha:
            raise ValueError(('Real 1.0.47 -> 1.0.48 upgrade failed',r.stderr[-1200:],sha(api),freshsha))
        actualchanged=[]
        with zipfile.ZipFile(cleanapi) as updated,zipfile.ZipFile(__import__('io').BytesIO(old_bytes)) as previous:
            if set(updated.namelist())!=set(previous.namelist()):raise ValueError('ZIP member list changed')
            for entry in previous.namelist():
                a=previous.read(entry);b=updated.read(entry)
                if a==b:continue
                if not entry.endswith('.class'):raise ValueError(('Nonclass member changed between releases',entry))
                v=verify_class(a,b,entry)
                actualchanged.append((entry,v))
        changes,_,_=plan(readmap(prior_map))
        expected_classes={cls.replace('.','/')+'.class' for cls,en in changes}
        if {e for e,v in actualchanged}!=expected_classes or len(actualchanged)!=19:
            raise ValueError(('Unexpected classes touched between releases',len(actualchanged),sorted(expected_classes-{e for e,v in actualchanged})))
        # True no-op and original restore on both originally modified JARs.
        for binary,path in ((new,api),(obf,obfj)):
            digest=sha(path)
            r=invoke(binary,upgrade,'--apply')
            if r.returncode or sha(path)!=digest:
                raise ValueError(('Same-version no-op failed',binary.name,r.stderr[-900:]))
        # A changed ZIP header is a hard error; refusal must not overwrite data.
        corrupted=bytearray(api.read_bytes());i=corrupted.find(b'PK\x01\x02')
        if i<0:raise ValueError('No ZIP central directory')
        corrupted[i+12]^=1;api.write_bytes(corrupted)
        with zipfile.ZipFile(api) as z:
            if z.testzip():raise ValueError('Should only alter ZIP header metadata')
        r=invoke(new,upgrade,'--apply')
        if r.returncode==0 or api.read_bytes()!=corrupted:
            raise ValueError('Corruption not refused or corrupted JAR was changed')
        api.write_bytes(cleanapi.read_bytes())
        for binary,path,expected in ((new,api,ORIGINAL_SHA['API']),(obf,obfj,ORIGINAL_SHA['OBF'])):
            r=invoke(binary,upgrade,'--restore')
            if r.returncode or sha(path)!=expected:raise ValueError(('Restore failed',binary.name,r.stderr[-900:]))
        return {'schema_version':1,'version':'1.0.48','original_api_sha256':ORIGINAL_SHA['API'],
          'patched_api_1047_sha256':EXPECTED_OLD,'patched_api_1048_sha256':freshsha,
          'api_classes_modified_from_original':938,'obf_classes_modified_from_original':539,
          'class_files_changed_from_1047_to_1048':len(actualchanged),
          'approved_numeric_text_translations_updated':len(changes),
          'all_class_executable_sections_identical':True,'upgrade_output_identical_to_fresh_install':True,
          'same_version_reapply_noop':'PASS','tampered_zip_header_rejected_unchanged':'PASS',
          'both_original_jars_restored_exactly':'PASS',
          'native_windows_gameplay_tested':False,'commercial_jar_bytes_published':False}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--original-api',type=Path,required=True)
    p.add_argument('--original-obf',type=Path,required=True)
    p.add_argument('--previous-api',type=Path,required=True)
    p.add_argument('--new-api',type=Path,required=True)
    p.add_argument('--obf-patcher',type=Path,required=True)
    p.add_argument('--prior-map',type=Path,required=True)
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    v=run(a.original_api,a.original_obf,a.previous_api,a.new_api,a.obf_patcher,a.prior_map)
    if a.out:a.out.write_text(json.dumps(v,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(v,indent=2))
