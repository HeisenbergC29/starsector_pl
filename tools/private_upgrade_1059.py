#!/usr/bin/env python3
"""Private v1.0.58 -> v1.0.59 original-JAR install/upgrade/restore test.

Original commercial JAR files are never copied to the repository or reports.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,tempfile,zipfile
from pathlib import Path
from apply_1059 import sha

BASE_API='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
BASE_OBF='5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8'
PREV_API='57004e66715ce8ccaec236a85d73961290cb4ebbbdc0282abd12a31c9b0c6be8'
PREV_OBF='85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1'
CLASS='com/fs/starfarer/api/impl/campaign/MonthlyReportNodeTooltipCreator.class'

def run(jars,root):
 jars=Path(jars);root=Path(root);api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';obf=root/'buildtools/NARZEDZIA_OBF'
 for name,expected in (('starfarer.api.jar',BASE_API),('starfarer_obf.jar',BASE_OBF)):
  if sha((jars/name).read_bytes())!=expected:raise ValueError(('Wrong original game binary',name))
 def cmd(args,cwd=None):
  p=subprocess.run(list(map(str,args)),cwd=cwd,env={**os.environ,'GO111MODULE':'off'},capture_output=True,text=True,timeout=150)
  if p.returncode:raise RuntimeError((args,p.returncode,p.stderr[-450:],p.stdout[-450:]))
 with tempfile.TemporaryDirectory() as temp:
  temp=Path(temp);b=temp/'bin';b.mkdir()
  cmd(['go','build','-o',b/'api1059','.'],api)
  cmd(['go','build','-o',b/'obf','.'],obf)
  older=temp/'older_source';shutil.copytree(api,older)
  main=older/'main.go';s=main.read_text('utf8')
  pairs=[('const version = "1059"','const version = "1058"'),
         ('const exeVersion = "1.0.59"','const exeVersion = "1.0.58"'),
         ('"1057", "1058", version}','"1057", version}'),
         ('PL ASCII patch up to 1.0.59','PL ASCII patch up to 1.0.58')]
  for old,new in pairs:
   if s.count(old)!=1:raise ValueError(('Old patcher reconstruction failed',old))
   s=s.replace(old,new)
  main.write_text(s,encoding='utf8')
  cmd(['go','build','-o',b/'api1058','.'],older)
  result={};oldj=None;newj=None
  for scenario in ('fresh','upgrade'):
   core=temp/scenario/'starsector-core';core.mkdir(parents=True)
   for file in ('starfarer.api.jar','starfarer_obf.jar'):shutil.copyfile(jars/file,core/file)
   if scenario=='upgrade':
    cmd([b/'obf','--game',core,'--mode','apply'])
    cmd([b/'api1058','--game',core,'--apply','--yes'])
    if sha((core/'starfarer.api.jar').read_bytes())!=PREV_API or sha((core/'starfarer_obf.jar').read_bytes())!=PREV_OBF:
     raise ValueError('1.0.58 reconstruction JAR hash mismatch')
    with zipfile.ZipFile(core/'starfarer.api.jar') as z:oldj={n:z.read(n) for n in z.namelist() if n.endswith('.class')}
   else:cmd([b/'obf','--game',core,'--mode','apply'])
   cmd([b/'api1059','--game',core,'--apply','--yes'])
   nowapi=(core/'starfarer.api.jar').read_bytes();nowobf=(core/'starfarer_obf.jar').read_bytes()
   if sha(nowobf)!=PREV_OBF:raise ValueError('OBF changed unexpectedly')
   result[scenario]={'api_sha256':sha(nowapi),'obf_sha256':sha(nowobf)}
   if scenario=='fresh':
    with zipfile.ZipFile(core/'starfarer.api.jar') as z:newj={n:z.read(n) for n in z.namelist() if n.endswith('.class')}
   digest=sha(nowapi)
   cmd([b/'api1059','--game',core,'--apply','--yes'])
   if sha((core/'starfarer.api.jar').read_bytes())!=digest:raise ValueError('Repeat apply not idempotent')
   cmd([b/'api1059','--game',core,'--restore','--yes'])
   cmd([b/'obf','--game',core,'--mode','restore'])
   if sha((core/'starfarer.api.jar').read_bytes())!=BASE_API or sha((core/'starfarer_obf.jar').read_bytes())!=BASE_OBF:
    raise ValueError('Original restore failed')
  if result['fresh']!=result['upgrade']:raise ValueError('Fresh != upgrade')
  if set(oldj)!=set(newj):raise ValueError('Class list was changed')
  different=[k for k in sorted(oldj) if oldj[k]!=newj[k]]
  if different!=[CLASS]:raise ValueError(('Non-target JVM class changed',different[:5],len(different)))
  bad=temp/'corrupted'/'starsector-core';bad.mkdir(parents=True)
  for f in ('starfarer.api.jar','starfarer_obf.jar'):shutil.copy2(jars/f,bad/f)
  jar=bad/'starfarer.api.jar';jar.write_bytes(jar.read_bytes()+b'tamper')
  before=sha(jar.read_bytes())
  p=subprocess.run([str(b/'api1059'),'--game',str(bad),'--apply','--yes'],capture_output=True,text=True,timeout=120)
  if p.returncode==0 or sha(jar.read_bytes())!=before:raise ValueError('Tamper not rejected')
  return {'release':'1.0.59','fresh_equal_upgrade':True,'repeat_apply_noop':True,
   'original_restore_byte_exact':True,'corrupted_API_rejected':True,
   'changed_class_count':1,'only_class':CLASS,'new_api_sha256':result['fresh']['api_sha256'],
   'obf_unchanged_sha256':PREV_OBF,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jars',required=True,type=Path);p.add_argument('--worktree',required=True,type=Path);p.add_argument('--out',type=Path)
 a=p.parse_args();r=run(a.jars,a.worktree)
 if a.out:a.out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
 print(json.dumps(r,indent=2))
