#!/usr/bin/env python3
"""Private original-JAR 1.0.63 audit: byte-accurate Java string pool and ldc uses.

The original Starsector archive is NEVER placed in public repository or ZIP.
Writes a JSON evidence inventory with exact class/literal/CP index/method/offset.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,struct,subprocess,zipfile
from pathlib import Path
from apply_1063 import CLASS,OLD,REPAIRS,DRAFT,sha
from apply_1054 import readmap
ORIGINAL_API='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'

def string_pool(classdata:bytes)->dict[int,str]:
 class P:
  def __init__(self,b):self.b=b;self.o=0
  def read(self,n):
   if self.o+n>len(self.b):raise ValueError('Invalid constant pool length')
   r=self.b[self.o:self.o+n];self.o+=n;return r
  def u1(self):return self.read(1)[0]
  def u2(self):return struct.unpack('>H',self.read(2))[0]
  def u4(self):return struct.unpack('>I',self.read(4))[0]
 p=P(classdata)
 if p.u4()!=0xCAFEBABE:raise ValueError('Not a JVM .class')
 p.u2();p.u2();count=p.u2();cp=[None]*count;index=1
 while index<count:
  tag=p.u1()
  if tag==1:cp[index]=(tag,p.read(p.u2()).decode('utf-8'))
  elif tag in (3,4):p.read(4);cp[index]=(tag,None)
  elif tag in (5,6):p.read(8);cp[index]=(tag,None);index+=1
  elif tag in (7,8,16,19,20):cp[index]=(tag,p.u2())
  elif tag in (9,10,11,12,17,18):p.read(4);cp[index]=(tag,None)
  elif tag==15:p.read(3);cp[index]=(tag,None)
  else:raise ValueError(('Unsupported JVM constant tag',index,tag))
  index+=1
 return {i:cp[data][1] for i,item in enumerate(cp) if item and item[0]==8 for data in [item[1]]}

def original_audit(jar:Path,root:Path)->dict:
 if sha(jar.read_bytes())!=ORIGINAL_API:raise ValueError('Original Starsector API JAR hash mismatch')
 path=CLASS.replace('.','/')+'.class'
 with zipfile.ZipFile(jar) as z:raw=z.read(path)
 pool=string_pool(raw)
 p=subprocess.run(['javap','-classpath',str(jar),'-c','-p',CLASS],capture_output=True,text=True,timeout=45,check=True)
 observed=[];method=''
 for line in p.stdout.splitlines():
  line_=line.strip()
  if line.startswith('  ') and not line.startswith('    ') and (line_.endswith(');') or line_=='static {};'):
   method=line_
  match=re.match(r'^\s*(\d+):\s+(ldc(?:_w|2_w)?)\s+#(\d+)\s+// String',line)
  if match:
   offset=int(match[1]);cp=int(match[3]);text=pool.get(cp)
   if text is None:raise ValueError(('Ldc not a string',method,offset,cp))
   observed.append({'method':method,'offset':offset,'opcode':match[2],'constant_pool_index':cp,'literal':text})
 t=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=[r for r in readmap(t/OLD) if r['source_class']==CLASS]
 literalset={x['literal'] for x in observed}
 if len(observed)!=83 or len(literalset)!=71 or len(old)!=47 or any(r['english_literal'] not in literalset for r in old):
  raise ValueError('Not the expected 83 uses / 71 strings / 47 class mappings inventory')
 drafts=[r for r in old if r['status'] in DRAFT]
 if len(drafts)!=35:raise ValueError('Wrong historical draft inventory')
 tags=[o for o in observed if o['literal']=='Colony threats']
 if len(tags)!=1 or tags[0]['offset']!=36 or 'getIntelTags(' not in tags[0]['method']:
  raise ValueError('Internal category key was not found in expected code')
 gettags=p.stdout.split('  public java.util.Set<java.lang.String> getIntelTags(')[1].split('  public ',1)[0]
 if not re.search(r'\b36: ldc_w\s+#\d+\s+// String Colony threats\n\s+39: invokeinterface\s+#\d+,\s+2\s+// InterfaceMethod java/util/Set.add:',gettags):
  raise ValueError('Colony threats is not a technical Set.add key at expected offsets')
 # Construct full evidence for each mapped literal from actual bytecode call sites.
 evidence=[]
 for item in old:
  uses=[{k:v for k,v in x.items() if k!='literal'} for x in observed if x['literal']==item['english_literal']]
  if not uses:raise ValueError(('Unreachable source literal',item['english_literal']))
  evidence.append({'english_literal':item['english_literal'],'status':item['status'],
   'source_sha256':sha(item['english_literal'].encode()),'uses':uses,
   'repair_1063':item['english_literal'] in REPAIRS})
 return {'release':'1.0.63','original_jar_sha256':ORIGINAL_API,'class_name':CLASS,
  'original_class_sha256':sha(raw),'original_class_utf8_strings_loaded':len(literalset),
  'original_java_ldc_string_uses':len(observed),'all_47_existing_mapped_strings_confirmed':True,
  'historical_unreviewed_rows':len(drafts),'approved_repairs':len(REPAIRS),
  'technical_category_guard':{'literal':'Colony threats','method':'getIntelTags','ldc_offset':36,'set_add_offset':39},
  'unresolved_dynamic_english_getter':'MarketAPI.getOnOrAt() returns on/at, cannot safely translate by class literal mapping',
  'mapped_source_literals':evidence,'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jar',required=True,type=Path)
 p.add_argument('--worktree',required=True,type=Path);p.add_argument('--out',type=Path)
 a=p.parse_args();report=original_audit(a.jar,a.worktree)
 if a.out:a.out.write_text(json.dumps(report,ensure_ascii=True,indent=2)+'\n','utf8')
 print(json.dumps({k:v for k,v in report.items() if k!='mapped_source_literals'},indent=2))
