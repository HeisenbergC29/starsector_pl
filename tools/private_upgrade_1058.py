#!/usr/bin/env python3
"""Optional private original-JAR regression for v1.0.57 -> v1.0.58.

Requires a privately owned Starsector 0.98a-RC8 starsector-core directory with
original starfarer.api.jar and starfarer_obf.jar. NEVER commit these JARs, patched
binaries, game paths, or raw gameplay logs to the public repository.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
from apply_1058 import once,sha

ROOT=Path(__file__).resolve().parent.parent
BASE_API_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
BASE_OBF_SHA='5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8'
PATCH_API_SHA='57004e66715ce8ccaec236a85d73961290cb4ebbbdc0282abd12a31c9b0c6be8'
PATCH_OBF_SHA='85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1'
GO_1057_SHA='56cdcdf6a08e4a07e9a5cabc667c48b262ea5638a9fc0dc1420fefdf5f814b2c'

def run(jars:Path,repo:Path=ROOT)->dict:
 jars=Path(jars).resolve();repo=Path(repo).resolve();work=repo/'worktree'
 for f,expected in [('starfarer.api.jar',BASE_API_SHA),('starfarer_obf.jar',BASE_OBF_SHA)]:
  p=jars/f
  if not p.is_file() or sha(p.read_bytes())!=expected:raise ValueError(('Wrong original game JAR',f))
 def command(args,cwd=None):
  p=subprocess.run([str(a) for a in args],cwd=cwd,capture_output=True,text=True,timeout=120,
                   env={**os.environ,'GO111MODULE':'off'})
  if p.returncode:raise RuntimeError(('Private integration command failed',str(args[0]),p.returncode,p.stderr[-300:]))
 with tempfile.TemporaryDirectory() as tmp:
  tmp=Path(tmp);bindir=tmp/'bin';bindir.mkdir()
  api=work/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';obf=work/'buildtools/NARZEDZIA_OBF'
  command(['go','build','-trimpath','-ldflags=-s -w','-o',bindir/'api_1058','.'],api)
  command(['go','build','-trimpath','-ldflags=-s -w','-o',bindir/'obf','.'],obf)
  old=tmp/'api_1057_source';shutil.copytree(api,old)
  s=(old/'main.go').read_text('utf8')
  for a,b in [
   ('const version = "1058"','const version = "1057"'),
   ('const exeVersion = "1.0.58"','const exeVersion = "1.0.57"'),
   ('"1056", "1057", version}','"1056", version}'),
   ('PL ASCII patch up to 1.0.58','PL ASCII patch up to 1.0.57')]:s=once(s,a,b)
  if sha(s.encode('utf8'))!=GO_1057_SHA:raise ValueError('Unexpected previous API patcher source')
  (old/'main.go').write_text(s,encoding='utf8')
  command(['go','build','-trimpath','-ldflags=-s -w','-o',bindir/'api_1057','.'],old)
  tests={}
  for scenario in ('fresh','upgrade_1057_to_1058'):
   core=tmp/scenario/'starsector-core';core.mkdir(parents=True)
   for name in ('starfarer.api.jar','starfarer_obf.jar'):shutil.copy2(jars/name,core/name)
   command([bindir/'obf','--game',core,'--mode','apply'])
   if sha((core/'starfarer_obf.jar').read_bytes())!=PATCH_OBF_SHA:raise ValueError('OBF patch mismatch')
   command([bindir/('api_1057' if scenario.startswith('upgrade') else 'api_1058'),'--game',core,'--apply','--yes'])
   if scenario.startswith('upgrade'):command([bindir/'api_1058','--game',core,'--apply','--yes'])
   if sha((core/'starfarer.api.jar').read_bytes())!=PATCH_API_SHA:raise ValueError('API fresh/upgrade mismatch')
   command([bindir/'api_1058','--game',core,'--apply','--yes'])
   if sha((core/'starfarer.api.jar').read_bytes())!=PATCH_API_SHA:raise ValueError('Repeated install is not idempotent')
   command([bindir/'api_1058','--game',core,'--restore','--yes'])
   command([bindir/'obf','--game',core,'--mode','restore'])
   if sha((core/'starfarer.api.jar').read_bytes())!=BASE_API_SHA or sha((core/'starfarer_obf.jar').read_bytes())!=BASE_OBF_SHA:
    raise ValueError('Restore is not byte-for-byte exact')
   tests[scenario]={'fresh_equals_upgrade':True,'idempotent':True,'restore_original_SHA':True}
  broken=tmp/'tampered'/'starsector-core';broken.mkdir(parents=True)
  for name in ('starfarer.api.jar','starfarer_obf.jar'):shutil.copy2(jars/name,broken/name)
  (broken/'starfarer.api.jar').write_bytes((broken/'starfarer.api.jar').read_bytes()+b'broken')
  digest=sha((broken/'starfarer.api.jar').read_bytes())
  r=subprocess.run([str(bindir/'api_1058'),'--game',str(broken),'--apply','--yes'],capture_output=True,text=True,timeout=120)
  if r.returncode==0 or sha((broken/'starfarer.api.jar').read_bytes())!=digest:raise ValueError('Tampered API was not rejected')
 return {'release':'1.0.58','game_version':'0.98a-RC8','test_results':tests,'tampered_API_refused':True,
         'original_API_SHA256':BASE_API_SHA,'original_OBF_SHA256':BASE_OBF_SHA,
         'patched_API_SHA256':PATCH_API_SHA,'patched_OBF_SHA256':PATCH_OBF_SHA,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jars',type=Path,required=True);p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--out',type=Path)
 a=p.parse_args();d=run(a.jars,a.repo)
 if a.out:a.out.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
 print(json.dumps(d,indent=2))
