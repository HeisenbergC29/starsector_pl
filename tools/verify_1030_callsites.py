#!/usr/bin/env python3
"""Read-only proof of exact 1.0.30 ldcs in original and patched Java archives.

Original commercial files never leave user's private workspace.
"""
import argparse,hashlib,json,re,subprocess,struct,zipfile
from pathlib import Path
from apply_1030 import OBF,API,CORRECTION
ORIGINAL={'OBF':'5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8','API':'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'}

def literals(path,cls):
 # Resolve ldc #index against the *raw JVM CONSTANT_String* pool: javap drops
 # trailing spaces (e.g. Price: ), so its text comment cannot certify exact text.
 entry=cls.replace('.','/')+'.class'
 with zipfile.ZipFile(path) as z:data=z.read(entry)
 n=struct.unpack_from('>H',data,8)[0];idx=1;pos=10;cp={}
 while idx<n:
  tag=data[pos];pos+=1
  if tag==1:
   length=struct.unpack_from('>H',data,pos)[0];pos+=2
   cp[idx]=(tag,data[pos:pos+length]);pos+=length
  elif tag in (3,4,9,10,11,12,17,18):pos+=4
  elif tag in (5,6):pos+=8;idx+=1
  elif tag in (7,8,16,19,20):cp[idx]=(tag,struct.unpack_from('>H',data,pos)[0]);pos+=2
  elif tag==15:pos+=3
  else:raise ValueError((cls,tag))
  idx+=1
 assert data[:4]==b'\xca\xfe\xba\xbe'
 p=subprocess.run(['javap','-classpath',str(path),'-p','-c',cls],capture_output=True,text=True,check=True)
 result=[]
 for line in p.stdout.splitlines():
  match=re.search(r'\bldc(?:_w)?\s+#(\d+)\s+// String',line)
  if not match:continue
  index=int(match.group(1));tag,ref=cp[index]
  assert tag==8,(cls,index)
  tag,data=cp[ref];assert tag==1
  result.append(data.decode('utf8'))
 return result

def main(args):
 result={'original_sha256':ORIGINAL,'checked':[]}
 for kind,p,patched,mapping in [('OBF',args.obf,args.patched_obf,OBF),('API',args.api,args.patched_api,API)]:
  assert hashlib.sha256(p.read_bytes()).hexdigest()==ORIGINAL[kind]
  for cls,entries in mapping.items():
   old=literals(p,cls);new=literals(patched,cls)
   for en,pl in entries.items():
    assert en in old,(cls,en,'not used by original ldc')
    assert pl in new,(cls,pl,'not used by patched ldc')
    assert en not in new,(cls,en,'still unpatched')
    result['checked'].append({'jar':kind,'class':cls,'source':en,'target':pl,'original_ldc':old.count(en),'patched_ldc':new.count(pl)})
 # One corrected existing mapping must remain in original with the old English literal.
 cls=CORRECTION['source_class']
 assert CORRECTION['english_literal'] in literals(args.api,cls)
 assert CORRECTION['to_polish'] in literals(args.patched_api,cls)
 assert CORRECTION['from_polish'] not in literals(args.patched_api,cls)
 result['edited_existing']={'class':cls,'source':CORRECTION['english_literal'],'target':CORRECTION['to_polish']}
 result['new_ldc_use_count']=sum(e['original_ldc'] for e in result['checked'])
 if args.out: args.out.write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'new_literals':len(result['checked']),'new_ldc_uses':result['new_ldc_use_count'],'existing_corrected':1}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--obf',type=Path,required=True);p.add_argument('--api',type=Path,required=True);p.add_argument('--patched-obf',type=Path,required=True);p.add_argument('--patched-api',type=Path,required=True);p.add_argument('--out',type=Path)
 main(p.parse_args())
