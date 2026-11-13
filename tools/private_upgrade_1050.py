#!/usr/bin/env python3
"""Private original Starsector 0.98a-RC8 API JAR: 1.0.48->1.0.49 upgrade regression.

Run locally with privately owned original game JARs and extracted Linux Go patchers.
No game-owned JARs or local paths are included in the public report.
"""
from __future__ import annotations
import argparse,subprocess,tempfile,shutil,zipfile,hashlib,json
from pathlib import Path
ORIGINAL_API_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
ORIGINAL_OBF_SHA='5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8'
def sha(b):return hashlib.sha256(b).hexdigest()
def call(exe,folder,action,success=True):
 p=subprocess.run([str(Path(exe).resolve()),'--game',str(folder),'--'+action,'--yes'],capture_output=True,text=True,timeout=90)
 if success and p.returncode!=0:raise AssertionError(('Patcher did not complete',action,p.stdout[-300:],p.stderr[-300:]))
 if not success and p.returncode==0:raise AssertionError('Expected damaged archive rejection')
 return p
def run(original_api,original_obf,previous_exe,current_exe):
 original_api=Path(original_api).read_bytes();original_obf=Path(original_obf).read_bytes()
 if sha(original_api)!=ORIGINAL_API_SHA or sha(original_obf)!=ORIGINAL_OBF_SHA:raise ValueError('Wrong original JAR build')
 with tempfile.TemporaryDirectory(prefix='starsector_pl_1050_') as d:
  first=Path(d)/'fresh';second=Path(d)/'upgrade'
  for folder in (first,second):
   folder.mkdir();(folder/'starfarer.api.jar').write_bytes(original_api);(folder/'starfarer_obf.jar').write_bytes(original_obf)
  call(previous_exe,second,'apply');prior_sha=sha((second/'starfarer.api.jar').read_bytes())
  call(current_exe,first,'apply');target_sha=sha((first/'starfarer.api.jar').read_bytes())
  call(current_exe,second,'apply');upgrade_sha=sha((second/'starfarer.api.jar').read_bytes())
  if target_sha!=upgrade_sha:raise ValueError('Upgrade differs from clean patch')
  noop=call(current_exe,second,'apply')
  if 'Version already installed. No files modified.' not in noop.stdout:raise ValueError('Reapply not idempotent')
  damaged=bytearray((second/'starfarer.api.jar').read_bytes());cen=damaged.find(b'PK\x01\x02')
  if cen<0:raise ValueError('No ZIP central-directory metadata')
  damaged[cen+12]^=1;(second/'starfarer.api.jar').write_bytes(damaged)
  with zipfile.ZipFile(second/'starfarer.api.jar') as z:
   if z.testzip() is not None:raise ValueError('Expected metadata-only mutation')
  call(current_exe,second,'apply',success=False)
  if (second/'starfarer.api.jar').read_bytes()!=damaged:raise ValueError('Damaged archive overwritten')
  (second/'starfarer.api.jar').write_bytes((first/'starfarer.api.jar').read_bytes())
  call(current_exe,first,'restore');call(current_exe,second,'restore')
  if any((folder/'starfarer.api.jar').read_bytes()!=original_api for folder in (first,second)):
   raise ValueError('Restore failed to reproduce original API JAR')
  return {'release':'1.0.50','original_api_sha256':ORIGINAL_API_SHA,'original_obf_sha256':ORIGINAL_OBF_SHA,
   'prior_api_sha256':prior_sha,'fresh_api_sha256':target_sha,'upgraded_api_sha256':upgrade_sha,
   'fresh_equals_upgrade':True,'reapply_idempotent':True,
   'corrupted_zip_metadata_rejected_unchanged':True,'restore_exact_original_api':True,
   'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original-api',required=True,type=Path);p.add_argument('--original-obf',required=True,type=Path)
 p.add_argument('--previous-exe',required=True,type=Path);p.add_argument('--current-exe',required=True,type=Path);p.add_argument('--report',type=Path)
 a=p.parse_args();out=run(a.original_api,a.original_obf,a.previous_exe,a.current_exe)
 if a.report:a.report.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
