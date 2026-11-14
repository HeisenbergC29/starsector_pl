#!/usr/bin/env python3
"""Private proof that newly translated constants are active UI strings in original 0.98a-RC8.

Requires user's private original starfarer.api.jar; do not commit commercial bytes.
The generated JSON report contains only callsite offsets/class names, no JAR contents.
"""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from apply_1059 import CLASS,ADDITIONS,CORRECTION,sha
JAR_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
EXPECT={'Equipment':[255],'Ships':[329,561,720],'Resources':[491,650],
        'units':[1210],'unit':[1222],'Approximately %s ':[1242], ' of ':[1253]}

def audit(jar:Path):
 jar=Path(jar)
 if sha(jar.read_bytes())!=JAR_SHA:raise ValueError('Unexpected original game jar')
 p=subprocess.run(['javap','-classpath',str(jar),'-c','-p',CLASS],capture_output=True,text=True,timeout=30,check=True)
 lines=p.stdout.splitlines()
 seen={}
 for i,l in enumerate(lines):
  m=re.search(r'^\s*(\d+):\s+ldc(?:_w)?\s+#\d+\s+// String (.*)$',l)
  if not m:continue
  offset=int(m.group(1));value=m.group(2)
  for literal,allowed in EXPECT.items():
   if value==literal.rstrip(' '):
    seen.setdefault(literal,[]).append((offset,i))
 for k,locs in EXPECT.items():
  actual=sorted(n for n,_ in seen.get(k,[]))
  if actual!=locs:raise ValueError(('JVM use of literal changed',k,actual,locs))
  for offset,i in seen[k]:
   window='\n'.join(lines[i+1:i+30])
   expected='addSectionHeading' if k in {'Equipment','Ships','Resources'} else ('StringBuilder' if k==CORRECTION[0] else 'StringBuilder.append')
   if expected not in window:
    raise ValueError(('Not a verified UI callsite',k,offset))
 return {'release':'1.0.59','original_jar_sha256':JAR_SHA,'class':CLASS,
  'confirmed_java_ldc_callsites':sum(len(x) for x in EXPECT.values()),
  'literal_callsites':{k:v for k,v in EXPECT.items()},
  'technical_settings_keys_replaced':0,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--jar',type=Path,required=True);a.add_argument('--out',type=Path)
 opt=a.parse_args();result=audit(opt.jar)
 if opt.out:opt.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
 print(json.dumps(result,indent=2))
