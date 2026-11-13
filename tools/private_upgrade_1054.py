#!/usr/bin/env python3
"""Private original commercial JAR integration; never publish JAR files."""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
from audit_jvm_1054 import verify as verify_jvm,ORIGINAL,PREVIOUS,CURRENT
ORIG_OBF='5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8'
CURRENT_OBF='85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(original_api,original_obf,prior_api,prior_obf,api_bin,obf_bin):
 original_api,original_obf,prior_api,prior_obf,api_bin,obf_bin=map(Path,(original_api,original_obf,prior_api,prior_obf,api_bin,obf_bin))
 for p,digest in ((original_api,ORIGINAL),(original_obf,ORIG_OBF),(prior_api,PREVIOUS),(prior_obf,CURRENT_OBF)):
  if sha(p)!=digest:raise ValueError(('Unexpected original/private source digest',p,sha(p)))
 if not api_bin.is_file() or not obf_bin.is_file():raise FileNotFoundError('No patcher binary')
 def invoke(b,args,success=True):
  p=subprocess.run([str(b),*map(str,args)],capture_output=True,text=True,timeout=70)
  if (p.returncode==0)!=success:raise ValueError(('Unexpected patcher status',b,p.returncode,p.stdout[-1000:],p.stderr[-1000:]))
  return p.stdout+p.stderr
 with tempfile.TemporaryDirectory(prefix='starsector1054-') as d:
  base=Path(d);fresh=base/'fresh'/'starsector-core';upgrade=base/'upgrade'/'starsector-core';fresh.mkdir(parents=True);upgrade.mkdir(parents=True)
  for core in (fresh,upgrade):
   shutil.copyfile(original_obf,core/'starfarer_obf.jar') if core==fresh else shutil.copyfile(prior_obf,core/'starfarer_obf.jar')
  shutil.copyfile(original_api,fresh/'starfarer.api.jar')
  shutil.copyfile(prior_api,upgrade/'starfarer.api.jar')
  shutil.copyfile(original_api,upgrade/'starfarer.api.jar.PL_ASCII_backup_1053')
  shutil.copyfile(original_obf,upgrade/'starfarer_obf.jar.PL_ASCII_backup_OBF_0999')
  for core in (fresh,upgrade):
   invoke(obf_bin,['-game',core.parent,'-mode','apply'])
   invoke(api_bin,['-game',core.parent,'-apply','-yes'])
  actual=[(sha(x/'starfarer.api.jar'),sha(x/'starfarer_obf.jar')) for x in (fresh,upgrade)]
  if actual!=[(CURRENT,CURRENT_OBF)]*2:raise ValueError(('Fresh vs update output differs',actual))
  jvm=verify_jvm(original_api,prior_api,upgrade/'starfarer.api.jar')
  for core in (fresh,upgrade):
   invoke(obf_bin,['-game',core.parent,'-mode','apply'])
   invoke(api_bin,['-game',core.parent,'-apply','-yes'])
   if (sha(core/'starfarer.api.jar'),sha(core/'starfarer_obf.jar'))!=(CURRENT,CURRENT_OBF):raise ValueError('Repeated apply modified files')
  old=(upgrade/'starfarer.api.jar').read_bytes();tampered=bytearray(old);tampered[55]^=1
  (upgrade/'starfarer.api.jar').write_bytes(tampered);digest=sha(upgrade/'starfarer.api.jar')
  invoke(api_bin,['-game',upgrade.parent,'-apply','-yes'],success=False)
  if sha(upgrade/'starfarer.api.jar')!=digest:raise ValueError('Corrupt API JAR overwritten')
  (upgrade/'starfarer.api.jar').write_bytes(old)
  for core in (fresh,upgrade):
   invoke(api_bin,['-game',core.parent,'-restore','-yes'])
   invoke(obf_bin,['-game',core.parent,'-mode','restore'])
   if (sha(core/'starfarer.api.jar'),sha(core/'starfarer_obf.jar'))!=(ORIGINAL,ORIG_OBF):raise ValueError('Commercial originals not restored')
 return {'version':'1.0.54','old_patched_api_sha256':PREVIOUS,'patched_api_sha256':CURRENT,
  'patched_obf_sha256_unchanged':CURRENT_OBF,'fresh_and_upgrade_identical':True,
  'repeat_api_and_obf_patchers_noop':True,'damaged_api_refused_without_overwrite':True,
  'both_private_original_JARs_restored_byte_identically':True,
  'changed_java_classes_vs_1053':jvm['changed_class_count'],
  'new_executable_code_changes':0,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for name in ('original-api','original-obf','prior-api','prior-obf','api-bin','obf-bin'):
  p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--report',type=Path);a=p.parse_args()
 info=run(a.original_api,a.original_obf,a.prior_api,a.prior_obf,a.api_bin,a.obf_bin)
 if a.report:a.report.write_text(json.dumps(info,indent=2)+'\n',encoding='utf8')
 print(json.dumps(info,indent=2))
