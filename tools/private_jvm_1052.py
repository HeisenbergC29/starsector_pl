#!/usr/bin/env python3
"""Private, original-JAR-based JVM regression proof: 1.0.52 shared her/dative repair.

Does not publish any game-owned class bytes; only field counts and SHA summaries.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from apply_1052 import BASE,LUDDIC,SHIELD,ADDITIONS,CORRECTIONS,EXPECTED_ORIGINAL_CLASS_SHA
from private_jvm_1051 import parse_class,getstr,verify_literal_only

SOURCE_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
PRIOR_SHA='cf26c3aa2885df954f4914b584ff1552b3b3c8f8d9290adfb8a03a9d6dff7a13'
CURRENT_SHA='5d53fa936ada275642a93b523f4a3e5ef45c10d3f16ed82465ed5476d27414c7'
CLASSES=[BASE,LUDDIC,SHIELD]
PATHS=[x.replace('.','/')+'.class' for x in CLASSES]
def sha(data):return hashlib.sha256(data).hexdigest()

def original_constants(b):
 cp,_,_=parse_class(b)
 return [(i,getstr(b,cp,i)) for i in range(1,len(cp)) if cp[i] is not None and cp[i][0]==8]

def check(original_api,previous_api,new_api):
 paths=[Path(x) for x in (original_api,previous_api,new_api)]
 if [sha(x.read_bytes()) for x in paths]!=[SOURCE_SHA,PRIOR_SHA,CURRENT_SHA]:raise ValueError('API JAR original/previous/target SHA mismatch')
 with zipfile.ZipFile(paths[0]) as orig,zipfile.ZipFile(paths[1]) as prev,zipfile.ZipFile(paths[2]) as now:
  members=orig.namelist()
  if members!=prev.namelist() or members!=now.namelist() or any(z.testzip() is not None for z in (orig,prev,now)):
   raise ValueError('JAR ZIP membership/CRC changed')
  changed=[];translated=0;details=[]
  for name in members:
   aa=orig.read(name);bb=prev.read(name);cc=now.read(name)
   if aa!=cc:translated+=name.endswith('.class')
   if bb==cc:continue
   changed.append(name)
   if name not in PATHS:raise ValueError(('Unreviewed JVM or resource mutated',name))
   if sha(aa)!=EXPECTED_ORIGINAL_CLASS_SHA[CLASSES[PATHS.index(name)]]:
    raise ValueError(('Source class differs from reviewed original JVM',name))
   verify_literal_only(bb,cc,name)
   before=dict(original_constants(aa));after=dict(original_constants(cc))
   source_literals=collections.Counter(before.values())
   class_name=CLASSES[PATHS.index(name)]
   items={k:v for k,v in {**ADDITIONS,**{k:vv[1] for k,vv in CORRECTIONS.items()}}.items() if k[0]==class_name}
   for (_,english),polish in items.items():
    if source_literals[english]!=1:raise ValueError(('English text absent or ambiguous in original class',class_name,english,source_literals[english]))
    idx=next(i for i,s in before.items() if s==english)
    if after[idx]!=polish:raise ValueError(('Class text translated incorrectly',class_name,english,after[idx],polish))
   details.append({'class':class_name,'original_class_sha256':sha(aa),'mapping_changes':len(items),
     'all_new_and_corrected_original_constants_verified':True,'executable_code_tail_unchanged':True})
  if changed!=PATHS or translated!=938:raise ValueError(('Expected only 3 bar classes to change between releases',changed,translated))
  bar=orig.read(PATHS[0]);cp,_,_=parse_class(bar)
  required={123:'man',131:'woman',141:'him',143:'her',152:'his'}
  if any(getstr(bar,cp,i)!=s for i,s in required.items()):raise ValueError('Gender source constant pool unexpectedly changed')
  javap={}
  for cl in CLASSES:
   text=subprocess.check_output(['javap','-classpath',str(paths[0]),'-c','-p',cl],text=True,timeout=30)
   javap[cl]=text
  base=javap[BASE]
  methods={}
  for meth in ('getHimOrHer','getHisOrHer'):
   mat=re.search(r'protected java\.lang\.String '+meth+r'\(\);\s+Code:\s+(.+?)(?=\n\s+(?:protected|public|private|static) |\Z)',base,re.S)
   if not mat:raise ValueError(('Missing original inherited pronoun getter',meth))
   snippet=mat.group(1)
   if snippet.count('ldc           #143')!=1:raise ValueError(('Shared original her CP #143 not verified',meth))
   methods[meth]='female branch uses original shared literal #143; Polish jej'
  sites={}
  for cl in (LUDDIC,SHIELD):
   for meth in ('getHimOrHer','getHisOrHer','getManOrWoman'):
    sites[cl.split('.')[-1]+'.'+meth]=len(re.findall(r'// Method get'+meth.removeprefix('get')+r':',javap[cl]))
  expected={
   'LuddicPathBaseBarEvent.getHimOrHer':1,'LuddicPathBaseBarEvent.getHisOrHer':3,'LuddicPathBaseBarEvent.getManOrWoman':2,
   'PlanetaryShieldBarEvent.getHimOrHer':1,'PlanetaryShieldBarEvent.getHisOrHer':6,'PlanetaryShieldBarEvent.getManOrWoman':0}
  if sites!=expected:raise ValueError(('Bar getter callsites unexpectedly changed',sites))
  return {'release':'1.0.52','original_api_sha256':SOURCE_SHA,'previous_api_sha256':PRIOR_SHA,
    'new_api_sha256':CURRENT_SHA,'changed_classes_since_1051':details,
    'java_class_changes_since_v1051':3,'api_translated_class_count':translated,
    'new_executable_instruction_byte_changes':0,'inherited_prior_2_ldc_personality_operands_preserved':True,
    'base_shared_her_143_references':len(methods),'original_getter_callsites_verified':sites,
    'dative_and_possessive_same_feminine_jej_reviewed_offline':True,
    'native_windows_gameplay_tested':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original-api',type=Path,required=True);p.add_argument('--previous-api',type=Path,required=True);p.add_argument('--current-api',type=Path,required=True);p.add_argument('--report',type=Path)
 a=p.parse_args();out=check(a.original_api,a.previous_api,a.current_api)
 if a.report:a.report.write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
 print(json.dumps(out,indent=2))
