#!/usr/bin/env python3
"""Evidence for v1.0.60 class-scoped UI mapping on original private Starsector JAR.

Does not publish or modify any proprietary classes. Rejects unknown game JARs.
"""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from apply_1060 import TRADE,PROCURE,ADDITIONS,REPAIRS,sha
ORIGINAL_JAR_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
# Exact method+bytecode-offset in original 0.98a-RC8; never map the nearby
# technical 'Trade'/'Smuggling' tags or sprite/configuration identifiers.
EXPECT={
 (TRADE,'addBulletPoints',141,'From '):'TooltipMakerAPI.addPara',
 (TRADE,'addBulletPoints',162,' to '):'TooltipMakerAPI.addPara',
 (TRADE,'getWhat',11,'goods'):'areturn',
 (TRADE,'getWhat',22,'materiel'):'areturn',
 (TRADE,'createSmallDescription',799,"It's noteworthy because it's carrying a large quantity of valuable "):'TooltipMakerAPI.addPara',
 (TRADE,'createSmallDescription',885,"It's noteworthy because it's carrying a large quantity of "):'TooltipMakerAPI.addPara',
 (PROCURE,'addBulletPoints',352,'Faction: '):'TooltipMakerAPI.addPara',
}

def read_uses(jar:Path,classname:str):
 p=subprocess.run(['javap','-classpath',str(jar),'-c','-p',classname],capture_output=True,text=True,timeout=45,check=True)
 lines=p.stdout.splitlines();current=None;result=[]
 for i,line in enumerate(lines):
  m=re.search(r'\b([A-Za-z_$][\w$]*)\([^;]*\);\s*$',line)
  if m:current=m.group(1)
  x=re.match(r'^\s*(\d+):\s+ldc(?:_w)?\s+#\d+\s+// String (.*)$',line)
  if x:result.append((current,int(x.group(1)),x.group(2),i,lines))
 return result

def audit(jar:Path)->dict:
 jar=Path(jar)
 if sha(jar.read_bytes())!=ORIGINAL_JAR_SHA:raise ValueError('Wrong original commercial game JAR')
 confirmed={}
 for classname in (TRADE,PROCURE):
  uses=read_uses(jar,classname)
  for cl,method,offset,literal in EXPECT:
   if cl!=classname:continue
   matches=[x for x in uses if x[0]==method and x[1]==offset and x[2].replace("\\'", "'").strip()==literal.strip()]
   if len(matches)!=1:raise ValueError(('Missing original JVM string use',classname,method,offset,literal))
   _,_,_,index,lines=matches[0]
   # Ensure the UI destination is verified, rather than a technical setting.
   if method=='getWhat':
    if not any('areturn' in line for line in lines[index+1:index+15]):
     raise ValueError('Commodity category not returned from getWhat')
   else:
    # A longer paragraph construction can span many instructions.
    end=lines.index('  public ',index) if '  public ' in lines[index:] else len(lines)
    window='\n'.join(lines[index:min(index+130,end)])
    if 'TooltipMakerAPI.addPara' not in window:
     raise ValueError(('String not shown to user by tooltip',cl,offset))
   confirmed[f'{classname}.{method}@{offset}']=literal
 if len(confirmed)!=7:raise ValueError('Unexpected JVM evidence inventory')
 return {'release':'1.0.60','original_jar_sha256':ORIGINAL_JAR_SHA,
  'confirmed_original_jvm_ldc':len(confirmed),'new_literals':len(ADDITIONS),
  'corrected_prior_literals':len(REPAIRS),'classes':sorted({x[0] for x in EXPECT}),
  'uses':confirmed,'excluded_technical_tag_literals':['Smuggling','Trade'],
  'native_windows_gameplay_tested':False}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--jar',type=Path,required=True);a.add_argument('--out',type=Path)
 opt=a.parse_args();r=audit(opt.jar)
 if opt.out:opt.out.write_text(json.dumps(r,indent=2,ensure_ascii=True)+'\n','utf8')
 print(json.dumps(r,indent=2))
