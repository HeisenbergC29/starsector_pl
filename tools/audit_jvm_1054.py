#!/usr/bin/env python3
"""Private original-JVM audit of 13 map edits. Do NOT publish original JAR bytes."""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from apply_1054 import ADDITIONS,CORRECTIONS,SIM,CODEX,readmap,sha
from private_jvm_1051 import parse_class,getstr,verify_literal_only
ORIGINAL='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
PREVIOUS='5d53fa936ada275642a93b523f4a3e5ef45c10d3f16ed82465ed5476d27414c7'
CURRENT='b5c256c78f92fb174456cb297660945d81690c33d21d513627b0547ed783eb14'
CLASS_COUNT=6

def literal_indices(data,literal):
 cp,_,_=parse_class(data)
 return [i for i,x in enumerate(cp) if x and x[0]==8 and getstr(data,cp,i)==literal]

def verify(original,previous,current):
 orig,old,new=map(Path,[original,previous,current])
 if [sha(p.read_bytes()) for p in [orig,old,new]]!=[ORIGINAL,PREVIOUS,CURRENT]:raise ValueError('Wrong JAR identity')
 keys={*ADDITIONS,*CORRECTIONS}
 with zipfile.ZipFile(orig) as a,zipfile.ZipFile(old) as b,zipfile.ZipFile(new) as c:
  names=a.namelist()
  if names!=b.namelist() or names!=c.namelist() or any(x.testzip() is not None for x in (a,b,c)):
   raise ValueError('ZIP structure/CRC unexpectedly changed')
  changed=[p for p in names if b.read(p)!=c.read(p)]
  expected={cl.replace('.','/')+'.class' for cl,en in keys}
  if set(changed)!=expected or len(changed)!=CLASS_COUNT:raise ValueError(('More than 6 JVM classes changed',changed))
  usage={};evidence=[]
  for classpath in sorted(expected):
   cl=classpath[:-6].replace('/','.')
   aa,bb,cc=(z.read(classpath) for z in (a,b,c))
   verify_literal_only(aa,bb,classpath) if cl != 'com.fs.starfarer.api.impl.campaign.FactionPersonalityPickerPluginImpl' else None
   verify_literal_only(bb,cc,classpath)
   originals={en:pl for (name,en),pl in ADDITIONS.items() if name==cl}
   originals.update({en:new for (name,en),(oldtext,new) in CORRECTIONS.items() if name==cl})
   code=subprocess.check_output(['javap','-classpath',str(orig),'-c','-p',cl],text=True,timeout=40)
   for en,pl in sorted(originals.items()):
    original_ids=literal_indices(aa,en)
    if len(original_ids)!=1:raise ValueError(('Original target missing/ambiguous',cl,en,original_ids))
    index=original_ids[0]
    # JVM ldc references original CONSTANT_String, not standalone UTF-8.
    hit=len(re.findall(r'^\s*\d+:\s+ldc(?:_w)?\s+#'+str(index)+r'\s+// String',code,re.M))
    if hit<1:raise ValueError(('Mapping targets no instruction',cl,en,index))
    if not pl and not literal_indices(cc,''):raise ValueError(('Zero-length suffix not translated',cl,en))
    if pl and not literal_indices(cc,pl):raise ValueError(('Polish string absent',cl,en,pl))
    # Verify corresponding original CONSTANT_String reference now points to new string.
    cp,_,_=parse_class(cc)
    if getstr(cc,cp,index)!=pl:raise ValueError(('Original CP String not remapped',cl,en,index,pl,getstr(cc,cp,index)))
    usage[cl+'::'+en]=hit
    evidence.append({'class':cl,'original_class_sha256':sha(aa),'english_literal':en,
      'polish_ascii':pl,'original_cp_index':index,'original_ldc_instructions':hit})
 return {'version':'1.0.54','original_api_sha256':ORIGINAL,'previous_api_sha256':PREVIOUS,
  'new_api_sha256':CURRENT,'changed_class_count':len(changed),'added_class_scoped_literals':len(ADDITIONS),
  'corrected_previous_literals':len(CORRECTIONS),'new_executable_code_changes':0,
  'original_ldc_use_count':sum(usage.values()),'evidence':evidence,'native_gameplay_windows_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for name in ('original','previous','current'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--report',type=Path);a=p.parse_args()
 result=verify(a.original,a.previous,a.current)
 if a.report:a.report.write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in result.items() if k!='evidence'},indent=2))
