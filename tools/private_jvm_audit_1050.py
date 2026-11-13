#!/usr/bin/env python3
"""Private verification of 1.0.50 original JVM constant-pool uses. No JAR uploads."""
import argparse,hashlib,json,re,struct,subprocess,zipfile
from pathlib import Path
from apply_1050 import CLASS,CHANGES,EXPECTED_LDC,sha
from private_jvm_audit_1049 import cp_split,class_structure_check,class_strings
ORIGINAL_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
def inspect(original_api,patched_api,previous_api,static_path=None):
 original_api=Path(original_api);patched_api=Path(patched_api);previous_api=Path(previous_api)
 if sha(original_api.read_bytes())!=ORIGINAL_SHA:raise ValueError('Wrong original Starsector API JAR')
 classpath=CLASS.replace('.','/')+'.class'
 with zipfile.ZipFile(original_api) as old,zipfile.ZipFile(patched_api) as new,zipfile.ZipFile(previous_api) as prior:
  src=old.read(classpath);dst=new.read(classpath)
  items,_,_=cp_split(src)
  indexes={}
  for idx,obj in enumerate(items):
   if obj is None or obj[0]!=8:continue
   ref=struct.unpack('>H',obj[1])[0];raw=items[ref][1];n=struct.unpack_from('>H',raw,0)[0];t=raw[2:2+n].decode('utf8')
   if t in CHANGES:indexes.setdefault(t,[]).append(idx)
  if set(indexes)!=set(CHANGES) or any(len(x)!=1 for x in indexes.values()):raise ValueError(('Original constant pool inventory invalid',indexes))
  cp_changes=class_structure_check(src,dst)
  changed=[]
  for name in prior.namelist():
   if not name.endswith('.class') or prior.read(name)==new.read(name):continue
   class_structure_check(prior.read(name),new.read(name));changed.append(name)
  if changed!=[classpath]:raise ValueError(('Unexpected changed class inventory',changed))
  static_matched=0
  if static_path:
   doc=json.loads(Path(static_path).read_text('utf8'))
   if doc.get('version')!='1.0.50' or len(doc.get('reviewed',[]))!=60:raise ValueError('Wrong 60-review original corpus')
   visited=set()
   for rec in doc['reviewed']:
    key=(rec['source_class'],rec['english_literal'])
    if key in visited:raise ValueError(('Duplicated original JVM review',key))
    visited.add(key)
    entry=rec['source_class'].replace('.','/')+'.class'
    if entry not in old.namelist() or class_strings(old.read(entry)).count(rec['english_literal'])!=1:
     raise ValueError(('Reviewed original JVM literal missing/nonunique',key))
    static_matched+=1
 javap=subprocess.check_output(['javap','-classpath',str(original_api),'-c','-p',CLASS],text=True)
 counts={t:len(re.findall(r'^\s*\d+:\s+ldc(?:_w)?\s+#'+str(idx[0])+r'\b',javap,re.M)) for t,idx in indexes.items()}
 if counts!=EXPECTED_LDC:raise ValueError(('Changed method users',counts,EXPECTED_LDC))
 return {'release':'1.0.50','original_api_sha256':ORIGINAL_SHA,'patched_api_sha256':sha(patched_api.read_bytes()),
  'previous_patched_api_sha256':sha(previous_api.read_bytes()),'class':CLASS,'original_string_constants':len(indexes),
  'class_string_constant_indices':{k:v[0] for k,v in indexes.items()},'original_ldc_users_by_literal':counts,
  'total_original_ldc_uses':sum(counts.values()),'reviewed_static_original_jvm_matches':static_matched,'newly_modified_api_classes':len(changed),
  'new_class_vs_previous':changed,'no_executable_java_changes':True,'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original-api',type=Path,required=True);p.add_argument('--patched-api',type=Path,required=True);p.add_argument('--previous-api',type=Path,required=True);p.add_argument('--static-review',type=Path);p.add_argument('--out',type=Path)
 a=p.parse_args();r=inspect(a.original_api,a.patched_api,a.previous_api,a.static_review)
 if a.out:a.out.write_text(json.dumps(r,indent=2,ensure_ascii=True)+'\n')
 print(json.dumps(r,indent=2))
