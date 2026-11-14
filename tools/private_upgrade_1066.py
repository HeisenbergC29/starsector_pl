#!/usr/bin/env python3
"""Private commercial-JAR v1.0.65 -> 1.0.66 update/fresh/restore regression.

Original game JARs must remain local; never commit, upload or publish them.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,tempfile,zipfile,re
from pathlib import Path
from apply_1066 import SIM,IND,TUT,sha
BASE_API='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
BASE_OBF='5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8'
PREV_API='59d884983c191f96eecb8c7d177a2e317e9ad1920c87e9aa862fc85414779ca4'
PREV_OBF='85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1'
TARGET={cl.replace('.','/')+'.class' for cl in (SIM,IND,TUT)}

def command(args,cwd=None,allow_fail=False):
 env={**os.environ,'GO111MODULE':'off'}
 p=subprocess.run(list(map(str,args)),cwd=cwd,env=env,capture_output=True,text=True,timeout=180)
 if not allow_fail and p.returncode:raise RuntimeError((args,p.returncode,p.stderr[-600:],p.stdout[-600:]))
 return p

def opcode_structure(jar:Path,classname:str):
 p=command(['javap','-classpath',jar,'-c','-p',classname])
 out=[]
 for line in p.stdout.splitlines():
  match=re.match(r'^\s*(\d+):\s+(\w+)\b',line)
  if match:out.append((int(match.group(1)),match.group(2)))
 return out

def run(jars:Path,root:Path)->dict:
 jars=Path(jars);root=Path(root)
 for name,expected in (('starfarer.api.jar',BASE_API),('starfarer_obf.jar',BASE_OBF)):
  if sha((jars/name).read_bytes())!=expected:raise ValueError(('Wrong game input JAR',name))
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO';obf=root/'buildtools/NARZEDZIA_OBF'
 with tempfile.TemporaryDirectory() as td:
  temp=Path(td);b=temp/'bin';b.mkdir()
  command(['go','build','-o',b/'api1066','.'],api)
  command(['go','build','-o',b/'obf','.'],obf)
  older=temp/'old_api';shutil.copytree(api,older)
  main=older/'main.go';code=main.read_text('utf8')
  for newest,previous in [
   ('const version = "1066"','const version = "1065"'),
   ('const exeVersion = "1.0.66"','const exeVersion = "1.0.65"'),
   ('"1064", "1065", version}','"1064", version}'),
   ('PL ASCII patch up to 1.0.66','PL ASCII patch up to 1.0.65')]:
   if code.count(newest)!=1:raise ValueError(('Cannot reconstruct v1065 Go patcher',newest))
   code=code.replace(newest,previous)
  main.write_text(code,'utf8');command(['go','build','-o',b/'api1065','.'],older)
  hashes={};earlier=None;newest=None
  for scenario in ('fresh','upgrade'):
   core=temp/scenario/'starsector-core';core.mkdir(parents=True)
   for file in ('starfarer.api.jar','starfarer_obf.jar'):shutil.copy2(jars/file,core/file)
   command([b/'obf','--game',core,'--mode','apply'])
   if scenario=='upgrade':
    command([b/'api1065','--game',core,'--apply','--yes'])
    if sha((core/'starfarer.api.jar').read_bytes())!=PREV_API or sha((core/'starfarer_obf.jar').read_bytes())!=PREV_OBF:
     raise ValueError('Reconstruction of the previous 1.0.65 patch failed')
    with zipfile.ZipFile(core/'starfarer.api.jar') as z:
     earlier={n:z.read(n) for n in z.namelist() if n.endswith('.class')}
   command([b/'api1066','--game',core,'--apply','--yes'])
   api_j=core/'starfarer.api.jar';obf_j=core/'starfarer_obf.jar'
   hashes[scenario]={'api_sha256':sha(api_j.read_bytes()),'obf_sha256':sha(obf_j.read_bytes())}
   if hashes[scenario]['obf_sha256']!=PREV_OBF:raise ValueError('OBF content unexpectedly changed')
   if scenario=='fresh':
    with zipfile.ZipFile(api_j) as z:newest={n:z.read(n) for n in z.namelist() if n.endswith('.class')}
    for c in (SIM,IND,TUT):
     before=opcode_structure(jars/'starfarer.api.jar',c)
     after=opcode_structure(api_j,c)
     if before!=after:raise ValueError(('Executable JVM opcode structure changed',c,len(before),len(after)))
   before=sha(api_j.read_bytes());command([b/'api1066','--game',core,'--apply','--yes'])
   if sha(api_j.read_bytes())!=before:raise ValueError('Repeated API patch should be no-op')
   command([b/'api1066','--game',core,'--restore','--yes'])
   command([b/'obf','--game',core,'--mode','restore'])
   if sha(api_j.read_bytes())!=BASE_API or sha(obf_j.read_bytes())!=BASE_OBF:
    raise ValueError('Restore did not recover original commercial JAR bytes')
  if hashes['fresh']!=hashes['upgrade']:raise ValueError('Fresh 1.0.66 != upgraded 1.0.65 -> 1.0.66')
  if set(earlier)!=set(newest):raise ValueError('Class inventory changed')
  changed=[n for n in sorted(earlier) if earlier[n]!=newest[n]]
  if set(changed)!=TARGET:raise ValueError(('Unexpected changed classes',changed[:8],len(changed)))
  bad=temp/'tampered'/'starsector-core';bad.mkdir(parents=True)
  for f in ('starfarer.api.jar','starfarer_obf.jar'):shutil.copyfile(jars/f,bad/f)
  file=bad/'starfarer.api.jar';file.write_bytes(file.read_bytes()+b'corruption')
  old=sha(file.read_bytes());p=command([b/'api1066','--game',bad,'--apply','--yes'],allow_fail=True)
  if p.returncode==0 or sha(file.read_bytes())!=old:raise ValueError('Damaged input was not rejected')
  return {'release':'1.0.66','fresh_equal_upgrade':True,'repeat_apply_noop':True,
   'original_restore_byte_exact':True,'tampered_jar_rejected':True,
   'changed_class_count':len(changed),'changed_classes':changed,
   'java_instruction_offsets_opcodes_identical':True,
   'new_api_sha256':hashes['fresh']['api_sha256'],
   'unchanged_obf_sha256':PREV_OBF,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jars',type=Path,required=True)
 p.add_argument('--worktree',type=Path,required=True);p.add_argument('--out',type=Path)
 a=p.parse_args();r=run(a.jars,a.worktree)
 if a.out:a.out.write_text(json.dumps(r,indent=2)+'\n','utf8')
 print(json.dumps(r,indent=2))
