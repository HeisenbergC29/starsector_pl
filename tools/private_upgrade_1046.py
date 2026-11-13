#!/usr/bin/env python3
"""Private 1.0.45 (API 1042) -> 1.0.46 (API 1046) JAR-upgrade test.

Rebuild historical Linux API patcher from extracted public source snapshot
(after reversing the four version-source substitutions verified by SHA).
Never touches real user installations; all JAR copies live in temp dirs.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile,shutil
from pathlib import Path
from verify_1046 import GO_1042_SHA,REVERSES
from private_jar_integration_1046 import ORIGINAL_SHA,sha,invoke,verify_jar

EXPECTED_1042_SHA='ae2cfb7bda28b58e20bd31976e1f399174c9eab564f5b98c192f2464ecf3bcf4'
EXPECTED_1046_SHA='581ebc605139ccf9a35ebe3c191e495c4664a255714756577b16d4361741d886'

def build_old(sourcedir,dest):
    sourcedir=Path(sourcedir)
    copy=Path(dest)/'historical_api_source'
    shutil.copytree(sourcedir,copy)
    main=copy/'main.go';new=main.read_text('utf8')
    for current,older in REVERSES:
        if new.count(current)!=1:raise ValueError(('Current source mismatch',current))
        new=new.replace(current,older)
    if hashlib.sha256(new.encode('utf8')).hexdigest()!=GO_1042_SHA:
        raise ValueError('Historical 1042 source not reproduced exactly')
    main.write_text(new,'utf8')
    binary=Path(dest)/'api_linux_1042'
    out=subprocess.run(['go','build','-o',str(binary),'.'],cwd=copy,env={**__import__('os').environ,'GO111MODULE':'off','GOOS':'linux','GOARCH':'amd64'},capture_output=True,text=True,timeout=120)
    if out.returncode or not binary.exists():raise RuntimeError(('Old Go build failed',out.stderr[-2000:]))
    return binary

def run(source,api_latest,obf_latest,origapi,origobf):
    for k,p in [('API',origapi),('OBF',origobf)]:
        if sha(p)!=ORIGINAL_SHA[k]:raise ValueError('Original JAR SHA mismatch '+k)
    with tempfile.TemporaryDirectory(prefix='ss1046_upgrade_') as td:
        root=Path(td);oldbin=build_old(source,root)
        core=root/'starsector-core';core.mkdir()
        a=core/'starfarer.api.jar';o=core/'starfarer_obf.jar'
        shutil.copyfile(origapi,a);shutil.copyfile(origobf,o)
        # Same obfuscated game strings for both releases.
        r=invoke(Path(obf_latest),core,'--apply')
        if r.returncode:raise RuntimeError(('OBF install failed',r.stdout[-500:],r.stderr[-500:]))
        # Genuine old 1.0.45 API state produced by the reconstructed 1042 tool.
        r=invoke(oldbin,core,'--apply')
        if r.returncode:raise RuntimeError(('1042 API install failed',r.stdout[-500:],r.stderr[-500:]))
        oldsha=sha(a)
        if oldsha!=EXPECTED_1042_SHA:raise ValueError(('Old 1042 patched JAR differs from documented version',oldsha))
        # Actual upgrade, not patching from a clean JAR.
        r=invoke(Path(api_latest),core,'--apply')
        if r.returncode:raise RuntimeError(('Real upgrade 1042->1046 failed',r.stdout[-800:],r.stderr[-800:]))
        newsha=sha(a)
        if newsha!=EXPECTED_1046_SHA:raise ValueError(('Upgrade differs from fresh 1046 patched API',newsha))
        verified=verify_jar(Path(origapi),a,'API')
        if verified['changed_classes']!=938:raise ValueError('API class count drift')
        r=invoke(Path(api_latest),core,'--apply')
        if r.returncode or sha(a)!=newsha:raise ValueError('1046 reapply is not a no-op')
        for k,b in [('API',api_latest),('OBF',obf_latest)]:
            r=invoke(Path(b),core,'--restore')
            if r.returncode:raise RuntimeError(('Restore failed',k,r.stderr[-500:]))
        if sha(a)!=ORIGINAL_SHA['API'] or sha(o)!=ORIGINAL_SHA['OBF']:
            raise ValueError('Originals not restored byte-for-byte')
        return {'upgrade':'1.0.45/API 1042 -> 1.0.46/API 1046',
           'old_api_sha256':oldsha,'upgraded_api_sha256':newsha,
           'fresh_and_upgraded_jars_identical':True,
           'patched_java_executable_code_unchanged':True,
           'changed_api_classes':938,'reapply_noop':True,
           'restored_both_original_jars':True,'private_jar_data_published':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--api-source',type=Path,required=True)
    p.add_argument('--latest-api',type=Path,required=True);p.add_argument('--latest-obf',type=Path,required=True)
    p.add_argument('--original-api',type=Path,required=True);p.add_argument('--original-obf',type=Path,required=True)
    p.add_argument('--out',type=Path)
    a=p.parse_args();r=run(a.api_source,a.latest_api,a.latest_obf,a.original_api,a.original_obf)
    if a.out:a.out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
