#!/usr/bin/env python3
"""Private fresh/install/upgrade/restore proof on owned original Starsector JARs.

No game-owned binaries are included in the public output.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,tempfile,zipfile
from pathlib import Path

SOURCE='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
OBF='5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8'
PRIOR='cf26c3aa2885df954f4914b584ff1552b3b3c8f8d9290adfb8a03a9d6dff7a13'
TARGET='5d53fa936ada275642a93b523f4a3e5ef45c10d3f16ed82465ed5476d27414c7'
sha=lambda b:hashlib.sha256(b).hexdigest()

def invoke(exe,folder,action,accept=True):
 p=subprocess.run([str(Path(exe).resolve()),'--game',str(folder),'--'+action,'--yes'],capture_output=True,text=True,timeout=120)
 if (p.returncode==0)!=accept:raise ValueError(('Unexpected patcher result',p.returncode,action,p.stdout[-500:],p.stderr[-500:]))
 return p

def audit(original,obf,prior_exe,current_exe):
 orig=Path(original).read_bytes();orig_obf=Path(obf).read_bytes()
 if sha(orig)!=SOURCE or sha(orig_obf)!=OBF:raise ValueError('Not 0.98a-RC8 original JARs')
 with tempfile.TemporaryDirectory(prefix='star_pl_1052_') as folder:
  root=Path(folder);fresh=root/'fresh';upgrade=root/'upgrade'
  for target in (fresh,upgrade):
   target.mkdir();(target/'starfarer.api.jar').write_bytes(orig);(target/'starfarer_obf.jar').write_bytes(orig_obf)
  invoke(prior_exe,upgrade,'apply');past=sha((upgrade/'starfarer.api.jar').read_bytes())
  if past!=PRIOR:raise ValueError(('1050 baseline unexpected',past))
  invoke(current_exe,fresh,'apply');new=sha((fresh/'starfarer.api.jar').read_bytes())
  invoke(current_exe,upgrade,'apply');updated=sha((upgrade/'starfarer.api.jar').read_bytes())
  if updated!=new or updated!=TARGET:raise ValueError(('Nonidentical fresh/upgrade 1052',updated,new))
  noop=invoke(current_exe,upgrade,'apply')
  if 'Version already installed. No files modified.' not in noop.stdout:raise ValueError('1052 reapply not idempotent')
  contaminated=bytearray((upgrade/'starfarer.api.jar').read_bytes());offset=contaminated.find(b'PK\x01\x02')
  if offset<0:raise ValueError('No ZIP central directory')
  contaminated[offset+12]^=1
  (upgrade/'starfarer.api.jar').write_bytes(contaminated)
  with zipfile.ZipFile(upgrade/'starfarer.api.jar') as archive:
   if archive.testzip() is not None:raise ValueError('Expected metadata-only tampering')
  invoke(current_exe,upgrade,'apply',False)
  if (upgrade/'starfarer.api.jar').read_bytes()!=contaminated:raise ValueError('Damaged library was modified')
  (upgrade/'starfarer.api.jar').write_bytes((fresh/'starfarer.api.jar').read_bytes())
  invoke(current_exe,fresh,'restore');invoke(current_exe,upgrade,'restore')
  if (fresh/'starfarer.api.jar').read_bytes()!=orig or (upgrade/'starfarer.api.jar').read_bytes()!=orig:
   raise ValueError('Restoration does not reproduce originals')
  return {'version':'1.0.52','original_api_sha256':SOURCE,'original_obf_sha256':OBF,
   'previous_api_sha256':PRIOR,'fresh_api_sha256':TARGET,'upgraded_api_sha256':TARGET,
   'clean_equals_upgrade':True,'idempotent':True,'corrupted_zip_rejected_without_overwrite':True,
   'restore_exact_original':True,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original-api',type=Path,required=True);p.add_argument('--original-obf',type=Path,required=True)
 p.add_argument('--prior-exe',type=Path,required=True);p.add_argument('--current-exe',type=Path,required=True);p.add_argument('--report',type=Path)
 a=p.parse_args();result=audit(a.original_api,a.original_obf,a.prior_exe,a.current_exe)
 if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
