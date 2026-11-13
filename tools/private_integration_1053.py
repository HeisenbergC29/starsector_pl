#!/usr/bin/env python3
"""Private original-JAR safety regression for 1.0.53. Never upload proprietary bytes.

Audit verifies actual JVM CONSTANT_String references and no executable-code changes,
then independently runs fresh install, upgrade, no-op, tamper refusal, restore.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,tempfile,zipfile,re,sys
from pathlib import Path
from apply_1053 import CHANGES,RECOVERY,OBF_PRIOR_PATCH_SHA,OBF_CURRENT_PATCH_SHA
from private_jvm_1051 import parse_class,getstr,verify_literal_only

ORIG_OBF_SHA='5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8'
ORIG_API_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
EXPECTED_API_SHA='5d53fa936ada275642a93b523f4a3e5ef45c10d3f16ed82465ed5476d27414c7'
ORIG_CLASS_SHA='99a94128288e065d3c89b25c8606eebb0db6081bf2ebcde07615c238770d87c0'
PRIOR_CLASS_SHA='31551ae09047535d5065c4b48cf353f106c20c906dbe1be922b9b9af6dc42a46'
NEW_CLASS_SHA='b94fa94cc7716e02d29a0d4f55ea6e385cd4b86b96229b599b2d655eaf6c481d'
CLASS=RECOVERY.replace('.','/')+'.class'

def sha(b):return hashlib.sha256(b).hexdigest()
def must(bool_,*message):
 if not bool_:raise ValueError(message)
def check_classes(original_obf,prior_obf,new_obf):
 files=list(map(Path,(original_obf,prior_obf,new_obf)))
 want=[ORIG_OBF_SHA,OBF_PRIOR_PATCH_SHA,OBF_CURRENT_PATCH_SHA]
 if [sha(f.read_bytes()) for f in files]!=want:raise ValueError('Wrong original/prior/current OBF JAR SHA')
 with zipfile.ZipFile(files[0]) as original,zipfile.ZipFile(files[1]) as prior,zipfile.ZipFile(files[2]) as new:
  members=original.namelist()
  if members!=prior.namelist() or members!=new.namelist() or any(z.testzip() is not None for z in (original,prior,new)):
   raise ValueError('JAR ZIP membership/CRC changed')
  old_changed=[x for x in members if original.read(x)!=prior.read(x)]
  now_changed=[x for x in members if prior.read(x)!=new.read(x)]
  if now_changed!=['META-INF/MANIFEST.MF',CLASS] or len([x for x in old_changed if x.endswith('.class')])!=539:
   raise ValueError(('Unexpected class changes',now_changed,len(old_changed)))
  # The JAR manifest carries SHA-1/MD5 per-class digests; an updated class
  # necessarily updates exactly its corresponding manifest entry.
  old_sections=prior.read('META-INF/MANIFEST.MF').split(b'\r\n\r\n')
  new_sections=new.read('META-INF/MANIFEST.MF').split(b'\r\n\r\n')
  diff=[(x,y) for x,y in zip(old_sections,new_sections) if x!=y]
  if len(old_sections)!=len(new_sections) or len(diff)!=1 or not diff[0][0].startswith(b'Name: '+CLASS.encode()+b'\r\n'):
   raise ValueError('Unexpected JAR manifest digest changes')
  a=original.read(CLASS);b=prior.read(CLASS);c=new.read(CLASS)

  if [sha(x) for x in (a,b,c)]!=[ORIG_CLASS_SHA,PRIOR_CLASS_SHA,NEW_CLASS_SHA]:
   raise ValueError('Original/reviewed recovery class changed')
  verify_literal_only(a,b,CLASS)
  verify_literal_only(b,c,CLASS)
  A,_,_=parse_class(a);B,_,_=parse_class(b);C,_,_=parse_class(c)
  originals={821:'ships',823:'ship',1248:' ships',816:'Select ships to recover'}
  translated={821:'okr.',823:'okr.',1248:' okr.',816:'Wybierz okrety do odzyskania'}
  for idx,english in originals.items():
   if getstr(a,A,idx)!=english or getstr(c,C,idx)!=translated[idx]:
    raise ValueError(('UI constant mismatch',idx,english,getstr(c,C,idx)))
  if getstr(b,B,816)!=translated[816] or any(getstr(b,B,i)!=originals[i] for i in (821,823,1248)):
   raise ValueError('Previously translated recovery heading or original untranslated words altered')
  original_class_names=set(x for x in members if x.endswith('.class'))
  if CLASS not in original_class_names:raise ValueError('Recovery UI class missing')
 dis=subprocess.check_output(['javap','-classpath',str(files[0]),'-c','-p',RECOVERY],text=True,timeout=40)
 instr={i:len(re.findall(r'^\s*\d+: ldc_w\s+#'+str(i)+r'\s+// String',dis,re.M)) for i in (816,821,823,1248)}
 if instr!={816:1,821:1,823:1,1248:1}:raise ValueError(('Unexpected original JVM usage',instr))
 return {'original_obf_sha256':ORIG_OBF_SHA,'old_patched_obf_sha256':OBF_PRIOR_PATCH_SHA,
  'new_patched_obf_sha256':OBF_CURRENT_PATCH_SHA,'changed_obf_classes_vs_1052':1,
  'changed_obf_classes_vs_original':539,'source_class_path':CLASS,
  'source_class_sha256':ORIG_CLASS_SHA,'new_class_sha256':NEW_CLASS_SHA,
  'verified_original_ldc_w_uses':instr,'checked_added_literals':len(CHANGES),
  'previously_translated_heading_confirmed':True,'executed_jvm_instructions_changed':0,'manifest_changed_only_for_target_class_digests':True,
  'native_windows_gameplay_tested':False}

def run_test(original_api,original_obf,prior_api,prior_obf,new_obf,obf_bin,api_bin):
 for file,expected in ((original_api,ORIG_API_SHA),(original_obf,ORIG_OBF_SHA),
  (prior_api,EXPECTED_API_SHA),(prior_obf,OBF_PRIOR_PATCH_SHA)):
  if sha(Path(file).read_bytes())!=expected:raise ValueError(('Wrong JAR test source',file))
 if any(not Path(x).is_file() for x in (obf_bin,api_bin)):raise ValueError('Missing actual Linux binary')
 def invoke(b,args,success=True):
  p=subprocess.run([str(b),*map(str,args)],text=True,capture_output=True,timeout=55)
  if (p.returncode==0)!=success:raise ValueError(('Bad patcher exit',b,args,p.returncode,p.stdout[-900:],p.stderr[-900:]))
  return p.stdout+p.stderr
 with tempfile.TemporaryDirectory(prefix='starsector-1053-') as td:
  t=Path(td);fresh=t/'fresh'/'starsector-core';upgrade=t/'upgrade'/'starsector-core';fresh.mkdir(parents=True);upgrade.mkdir(parents=True)
  def cp(src,to):shutil.copyfile(src,to)
  cp(original_api,fresh/'starfarer.api.jar');cp(original_obf,fresh/'starfarer_obf.jar')
  cp(prior_api,upgrade/'starfarer.api.jar');cp(prior_obf,upgrade/'starfarer_obf.jar')
  cp(original_api,upgrade/'starfarer.api.jar.PL_ASCII_backup_1052')
  cp(original_obf,upgrade/'starfarer_obf.jar.PL_ASCII_backup_OBF_0999')
  for core in (fresh,upgrade):
   invoke(obf_bin,['-game',core.parent,'-mode','apply'])
   invoke(api_bin,['-game',core.parent,'-apply','-yes'])
  out=[[sha((p/nam).read_bytes()) for nam in ('starfarer.api.jar','starfarer_obf.jar')] for p in (fresh,upgrade)]
  if out!=[[EXPECTED_API_SHA,OBF_CURRENT_PATCH_SHA]]*2:raise ValueError(('Fresh != upgrade',out))
  # No-op: both patchers must leave the same bytes untouched on repeat.
  for core in (fresh,upgrade):
   invoke(obf_bin,['-game',core.parent,'-mode','apply'])
   invoke(api_bin,['-game',core.parent,'-apply','-yes'])
   if [sha((core/n).read_bytes()) for n in ('starfarer.api.jar','starfarer_obf.jar')]!=out[0]:raise ValueError('Idempotence failed')
  # Damaged ZIP/unknown JAR must be refused without writing and without altering backup.
  original_obf_bytes=(upgrade/'starfarer_obf.jar').read_bytes()
  dirty=bytearray(original_obf_bytes);dirty[60]^=1
  (upgrade/'starfarer_obf.jar').write_bytes(dirty)
  before=sha((upgrade/'starfarer_obf.jar').read_bytes())
  invoke(obf_bin,['-game',upgrade.parent,'-mode','apply'],success=False)
  if sha((upgrade/'starfarer_obf.jar').read_bytes())!=before:raise ValueError('Unrecognized OBF was overwritten')
  (upgrade/'starfarer_obf.jar').write_bytes(original_obf_bytes)
  for core in (fresh,upgrade):
   invoke(api_bin,['-game',core.parent,'-restore','-yes'])
   invoke(obf_bin,['-game',core.parent,'-mode','restore'])
   restored=[sha((core/n).read_bytes()) for n in ('starfarer.api.jar','starfarer_obf.jar')]
   if restored!=[ORIG_API_SHA,ORIG_OBF_SHA]:raise ValueError(('Restore failed',restored))
 return {'fresh_equals_upgrade_api_sha256':EXPECTED_API_SHA,
  'fresh_equals_upgrade_obf_sha256':OBF_CURRENT_PATCH_SHA,'old_1052_obf_upgrade_supported':True,
  'old_1052_api_unchanged_sha256':True,'both_patchers_reapply_idempotent':True,
  'corrupt_jar_refused_without_write':True,'both_commercial_originals_restored_identically':True}

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for x in ('original-api','original-obf','prior-api','prior-obf','current-obf','obf-bin','api-bin'):
  p.add_argument('--'+x,type=Path,required=True)
 p.add_argument('--report',type=Path);a=p.parse_args()
 proof=check_classes(a.original_obf,a.prior_obf,a.current_obf)
 proof['upgrade']=run_test(a.original_api,a.original_obf,a.prior_api,a.prior_obf,a.current_obf,a.obf_bin,a.api_bin)
 if a.report:a.report.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
 print(json.dumps(proof,indent=2))
