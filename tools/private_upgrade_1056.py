#!/usr/bin/env python3
"""Private original commercial JAR integration; writes hashes only, never original bytes."""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
EXPECTED={
 'starfarer.api.jar':{'original':'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a','patched':'57004e66715ce8ccaec236a85d73961290cb4ebbbdc0282abd12a31c9b0c6be8'},
 'starfarer_obf.jar':{'original':'5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8','patched':'85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1'}
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def runbin(args,ok=True):
 r=subprocess.run([str(x) for x in args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=45)
 if (r.returncode==0)!=ok:raise RuntimeError(('Unexpected patcher exit',r.returncode,r.stdout[-1500:]))
 return r.stdout

def check(original:Path,obf:Path,api_old:Path,api_new:Path)->dict:
 original=Path(original)
 for name,hashes in EXPECTED.items():
  if sha(original/name)!=hashes['original']:raise ValueError(('Commercial original source hash mismatch',name))
 with tempfile.TemporaryDirectory(prefix='ss1056-private-') as td:
  root=Path(td);fresh=root/'fresh';upgrade=root/'upgrade';corrupted=root/'corrupted'
  for dst in [fresh,upgrade,corrupted]:
   dst.mkdir();[shutil.copy2(original/name,dst/name) for name in EXPECTED]
  for dest in [fresh,upgrade]:runbin([obf,'-game',dest,'-mode','apply'])
  runbin([api_new,'--game',fresh,'--apply','--yes'])
  runbin([api_old,'--game',upgrade,'--apply','--yes'])
  prior={name:sha(upgrade/name) for name in EXPECTED}
  runbin([api_new,'--game',upgrade,'--apply','--yes'])
  for name,hashes in EXPECTED.items():
   if sha(fresh/name)!=hashes['patched'] or sha(upgrade/name)!=hashes['patched']:
    raise ValueError(('Fresh vs upgrade differs',name))
  if prior!={name:sha(upgrade/name) for name in EXPECTED}:raise ValueError('Same API table overwrote previous patched JAR')
  before={name:sha(fresh/name) for name in EXPECTED}
  runbin([api_new,'--game',fresh,'--apply','--yes'])
  runbin([obf,'-game',fresh,'-mode','apply'])
  if before!={name:sha(fresh/name) for name in EXPECTED}:raise ValueError('Repeat patch changed bytes')
  j=corrupted/'starfarer.api.jar';bad=bytearray(j.read_bytes());bad[-29]^=0x08;j.write_bytes(bad);tampered=sha(j)
  runbin([api_new,'--game',corrupted,'--apply','--yes'],ok=False)
  if sha(j)!=tampered or (corrupted/'starfarer.api.jar.PL_ASCII_backup_JAR_0999').exists():
   raise ValueError('Tampered API JAR was changed or backed up')
  runbin([api_new,'--game',fresh,'--restore','--yes'])
  runbin([obf,'-game',fresh,'-mode','restore'])
  for name,h in EXPECTED.items():
   if sha(fresh/name)!=h['original']:raise ValueError(('Original restore failed',name))
 return {'release':'1.0.56','source':'private original Starsector 0.98a-RC8 API+OBF JAR',
  'fresh_install_equals_upgrade_1055_to_1056':True,'previous_version_was_noop_when_same_map':True,
  'idempotent_reapplication':True,'tampered_input_refused_unchanged':True,'both_original_jars_restored_sha_identical':True,
  'original_sha256':{key:value['original'] for key,value in EXPECTED.items()},
  'patched_sha256':{key:value['patched'] for key,value in EXPECTED.items()},
  'API_JVM_mapping_changed':False,'OBF_JVM_mapping_changed':False,
  'commercial_JARs_in_release':False,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ('original','obf','api_old','api_new'):p.add_argument('--'+k,required=True,type=Path)
 a=p.parse_args();print(json.dumps(check(a.original,a.obf,a.api_old,a.api_new),indent=2))
