"""Verify the exact source literal occurs in each original class and has an ldc opcode."""
import argparse,json,zipfile,subprocess,re,hashlib
from pathlib import Path
from apply_1026 import OBF
from audit_1015_jars import parse_class, EXPECTED_ORIG

def audit(jar):
 assert hashlib.sha256(jar.read_bytes()).hexdigest()==EXPECTED_ORIG['OBF']
 report=[]
 with zipfile.ZipFile(jar) as z:
  for cl,mappings in OBF.items():
   cp,_=parse_class(z.read(cl.replace('.','/')+'.class'))
   const={cp[e[3]][2].decode('utf8') for e in cp if e and e[0]==8 and cp[e[3]][0]==1}
   assert set(mappings)<=const,(cl,set(mappings)-const)
   r=subprocess.run(['javap','-c','-p','-classpath',str(jar),cl],capture_output=True,text=True,timeout=45)
   assert r.returncode==0,(cl,r.stderr[:200])
   lines=r.stdout.splitlines()
   for source,target in mappings.items():
    sites=[i for i,x in enumerate(lines) if '// String ' in x and x.split('// String ',1)[1].strip()==source.strip() and re.search(r'\bldc(?:_w)?\s+#\d+',x)]
    assert sites,(cl,source)
    # An LDC used as an immediate arg for a UI label/header/list display, not e.g. getEnumByName.
    examples=[]
    for i in sites:
     follow=' '.join(lines[i+1:i+18]);window=follow[:1200]
     signatures=['com/fs/starfarer/ui/','com/fs/starfarer/campaign/ui/','com/fs/starfarer/coreui/','com/fs/graphics/','getRenderer','StringBuilder','createUI','addText','setText','createButton']
     ui=any(x in window for x in signatures)
     examples.append({'line':i+1,'ui_calls_nearby':ui})
    report.append({'class':cl,'source':source,'translation':target,'ldc_sites':len(sites),'any_ui_context':any(v['ui_calls_nearby'] for v in examples)})
 return report
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--obf',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
 result=audit(args.obf)
 s={'jar_sha256':EXPECTED_ORIG['OBF'],'approved_literals':len(result),'classes':len(OBF),'ldc_occurrences':sum(x['ldc_sites'] for x in result),'ui_context_detected':sum(x['any_ui_context'] for x in result),'warnings':'javap verifies LDC use and nearby UI calls; not a native gameplay test', 'rows':result}
 args.out.write_text(json.dumps(s,indent=2,ensure_ascii=True)+'\n')
 print({k:v for k,v in s.items() if k!='rows'})
 print('NO UI CONTEXT',[(x['class'],x['source']) for x in result if not x['any_ui_context']])