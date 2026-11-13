#!/usr/bin/env python3
"""Real original-owned JAR upgrade from 1.0.54, no commercial bytes in reports."""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
from audit_jvm_1055 import run as audit,ORIGINAL,PREVIOUS
ORIG_OBF='5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8'
PATCH_OBF='85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1'
NEW_API='57004e66715ce8ccaec236a85d73961290cb4ebbbdc0282abd12a31c9b0c6be8'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def invoke(exe,args,expected=True):
 p=subprocess.run([str(exe),*map(str,args)],capture_output=True,text=True,timeout=110)
 if (p.returncode==0)!=expected:raise ValueError(('Incorrect patcher result',exe,p.returncode,p.stdout[-700:],p.stderr[-700:]))
 return p.stdout+p.stderr

def test(original_api,original_obf,prior_api,prior_obf,api_bin,obf_bin,root,previous_review):
 original_api,original_obf,prior_api,prior_obf,api_bin,obf_bin=map(Path,(original_api,original_obf,prior_api,prior_obf,api_bin,obf_bin))
 for p,h in ((original_api,ORIGINAL),(original_obf,ORIG_OBF),(prior_api,PREVIOUS),(prior_obf,PATCH_OBF)):
  if sha(p)!=h:raise ValueError(('Incorrect original or previous source JAR',p,sha(p)))
 if not api_bin.is_file() or not obf_bin.is_file():raise FileNotFoundError('Missing patcher binary')
 with tempfile.TemporaryDirectory(prefix='starsector1055-') as tmp:
  bases={name:Path(tmp)/name/'starsector-core' for name in ('fresh','upgrade')}
  for name,core in bases.items():
   core.mkdir(parents=True)
   shutil.copyfile(original_api if name=='fresh' else prior_api,core/'starfarer.api.jar')
   shutil.copyfile(original_obf if name=='fresh' else prior_obf,core/'starfarer_obf.jar')
   if name=='upgrade':
    shutil.copyfile(original_api,core/'starfarer.api.jar.PL_ASCII_backup_1054')
    shutil.copyfile(original_obf,core/'starfarer_obf.jar.PL_ASCII_backup_OBF_0999')
  for core in bases.values():
   invoke(obf_bin,['-game',core.parent,'-mode','apply'])
   invoke(api_bin,['-game',core.parent,'-apply','-yes'])
  expected=(NEW_API,PATCH_OBF)
  for core in bases.values():
   result=(sha(core/'starfarer.api.jar'),sha(core/'starfarer_obf.jar'))
   if result!=expected:raise ValueError(('Upgrade/fresh JAR mismatch',core,result,expected))
  jvm=audit(root,previous_review,original_api,prior_api,bases['fresh']/'starfarer.api.jar')
  for core in bases.values():
   invoke(obf_bin,['-game',core.parent,'-mode','apply']);invoke(api_bin,['-game',core.parent,'-apply','-yes'])
   if (sha(core/'starfarer.api.jar'),sha(core/'starfarer_obf.jar'))!=expected:raise ValueError('Repeated patch changed files')
  target=bases['upgrade']/'starfarer.api.jar';old=target.read_bytes();corrupted=bytearray(old);corrupted[55]^=1;target.write_bytes(corrupted);tampered_sha=sha(target)
  invoke(api_bin,['-game',target.parent.parent,'-apply','-yes'],expected=False)
  if sha(target)!=tampered_sha:raise ValueError('Corrupt JAR overwritten')
  target.write_bytes(old)
  for core in bases.values():
   invoke(api_bin,['-game',core.parent,'-restore','-yes'])
   invoke(obf_bin,['-game',core.parent,'-mode','restore'])
   if (sha(core/'starfarer.api.jar'),sha(core/'starfarer_obf.jar'))!=(ORIGINAL,ORIG_OBF):
    raise ValueError('Original game files not fully restored')
 return {'release':'1.0.55','api_new_sha256':NEW_API,'obf_unchanged_sha256':PATCH_OBF,
  'fresh_and_upgrade_1054_to_1055_identical':True,'both_patchers_reapplication_idempotent':True,
  'corrupt_zip_header_rejected_without_overwrite':True,'both_proprietary_originals_restored_byte_for_byte':True,
  'java_classes_changed_vs_1054':jvm['changed_java_classes'],
  'new_executable_bytecode_edits':jvm['new_jvm_executable_bytecode_changes'],
  'original_jvm_reviewed_historical_fragments':jvm['reviewed_historical_source_literals'],
  'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for x in ('original-api','original-obf','prior-api','prior-obf','api-bin','obf-bin','root','previous-review'):
  p.add_argument('--'+x,required=True,type=Path)
 p.add_argument('--report',type=Path);a=p.parse_args()
 o=test(a.original_api,a.original_obf,a.prior_api,a.prior_obf,a.api_bin,a.obf_bin,a.root,a.previous_review)
 if a.report:a.report.write_text(json.dumps(o,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps(o,indent=2))
