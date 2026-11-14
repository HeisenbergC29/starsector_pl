#!/usr/bin/env python3
"""Private original-JVM evidence for v1.0.61 GateHaulerIntel translations.

Runs on the owner's locally held Starsector 0.98a-RC8 API JAR; neither the JAR
nor class bytes are shipped with the public localization source repository.
"""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess,zipfile,struct
from pathlib import Path
from apply_1061 import CLASS,NEW_LITERALS,sha
from apply_1054 import readmap
ORIGINAL_JAR_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
EXPECTED_PREVIOUS=30
EXPECTED_NEW=3
EXPECTED_ACTIVE_LDCS=49

def read_uses(jar:Path):
 p=subprocess.run(['javap','-classpath',str(jar),'-c','-p',CLASS],check=True,capture_output=True,text=True,timeout=45)
 method=None;out=[]
 for line in p.stdout.splitlines():
  m=re.search(r'\b([A-Za-z_$][\w$]*)\([^;]*\);\s*$',line)
  if m:method=m.group(1)
  x=re.match(r'^\s*(\d+):\s+ldc(?:_w)?\s+#(\d+)\s+// String\s*(.*)$',line)
  if x:out.append({'method':method,'offset':int(x.group(1)),'constant_pool_index':int(x.group(2)),'shown_literal':x.group(3).replace("\\'","'")})
 return out

def assert_literal_space_is_real(jar:Path)->bool:
 path=CLASS.replace('.','/')+'.class';data=zipfile.ZipFile(jar).read(path)
 if data[:4]!=b'\xca\xfe\xba\xbe':raise ValueError('Incorrect JVM class header')
 n=struct.unpack_from('>H',data,8)[0];i=1;p=10;cp=[None]*n
 while i<n:
  tag=data[p];p+=1
  if tag==1:
   length=struct.unpack_from('>H',data,p)[0];p+=2;cp[i]=('utf8',data[p:p+length]);p+=length
  elif tag in (3,4):p+=4
  elif tag in (5,6):p+=8;i+=1
  elif tag in (7,8,16,19,20):cp[i]=('ptr',struct.unpack_from('>H',data,p)[0]);p+=2
  elif tag in (9,10,11,12,17,18):p+=4
  elif tag==15:p+=3
  else:raise ValueError(('Unknown CP tag',i,tag))
  i+=1
 spaces=sum(e and e[0]=='ptr' and cp[e[1]]==('utf8',b' ') for e in cp if e)
 if spaces!=1:raise ValueError(('Unexpected number of Java string space constants',spaces))
 return True

def audit(jar:Path,root:Path)->dict:
 jar=Path(jar);root=Path(root)
 if sha(jar.read_bytes())!=ORIGINAL_JAR_SHA:raise ValueError('Unexpected copyrighted original JAR SHA')
 original=readmap(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1060.csv')
 known=[r['english_literal'] for r in original if r['source_class']==CLASS]
 if len(known)!=EXPECTED_PREVIOUS or len(set(known))!=EXPECTED_PREVIOUS:raise ValueError('Missing older mapped class strings')
 target=set(known)|set(NEW_LITERALS)
 if len(target)!=EXPECTED_PREVIOUS+EXPECTED_NEW:raise ValueError('New literal collided')
 uses=read_uses(jar);included=[]
 for use in uses:
  options=[s for s in target if s.strip()==use['shown_literal'].strip() and (s!=' ' or use['constant_pool_index']==879)]
  if len(options)==1:
   included.append({**use,'english_literal':options[0]})
  elif len(options)>1:raise ValueError(('Ambiguous visible Java string',use))
 if len(included)!=EXPECTED_ACTIVE_LDCS or set(x['english_literal'] for x in included)!=target:
  raise ValueError(('Incomplete original JAR literal callsite coverage',len(included),len({x['english_literal'] for x in included})))
 if sum(x['english_literal']=='day' for x in included)!=5 or sum(x['english_literal']=='days' for x in included)!=5:
  raise ValueError('Wrong day / days Java branch count')
 spaces=[x for x in included if x['english_literal']==' ']
 if [(x['method'],x['offset']) for x in spaces]!=[('createSmallDescription',551)]:
  raise ValueError('The sentence separator is used elsewhere or at a different offset')
 assert_literal_space_is_real(jar)
 used_methods=set(x['method'] for x in included)
 if not {'getName','getSortString','getIntelTags','addBulletPoints','createSmallDescription'}<=used_methods:
  raise ValueError('Player-facing methods not covered')
 return {'release':'1.0.61','game_version':'0.98a-RC8','original_jar_sha256':ORIGINAL_JAR_SHA,
  'class':CLASS,'class_scoped_map_entries':len(target), 'old_literal_count':EXPECTED_PREVIOUS,
  'new_literal_count':EXPECTED_NEW,'confirmed_original_jvm_ldc_uses':len(included),
  'day_singular_uses':5,'day_plural_uses':5,'separator_uses':1,
  'space_cp_constant_verified':True,'uses':included,
  'native_windows_gameplay_tested':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jar',required=True,type=Path)
 p.add_argument('--worktree',required=True,type=Path);p.add_argument('--out',type=Path)
 a=p.parse_args();r=audit(a.jar,a.worktree)
 if a.out:a.out.write_text(json.dumps(r,ensure_ascii=True,indent=2)+'\n','utf8')
 print(json.dumps({k:v for k,v in r.items() if k!='uses'},indent=2))
