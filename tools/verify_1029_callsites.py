#!/usr/bin/env python3
"""Check every 1.0.29 entry against real 0.98a-RC8 Java ldc sites (private JARs).

This is a source-verification gate, not an in-game UI test.
"""
import argparse,collections,hashlib,json,re,subprocess,zipfile,struct
from pathlib import Path
from apply_1029 import OBF,API
EXPECTED={'OBF':'5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8',
          'API':'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'}

def strings_in_cp(raw):
 if raw[:4]!=b"\xca\xfe\xba\xbe":raise ValueError("Invalid .class")
 n=struct.unpack_from(">H",raw,8)[0];index=1;pos=10;words={};srefs=[]
 while index<n:
  tag=raw[pos];pos+=1
  if tag==1:
   size=struct.unpack_from(">H",raw,pos)[0];pos+=2;words[index]=raw[pos:pos+size].decode("utf8","replace");pos+=size
  elif tag in (3,4,9,10,11,12,17,18):pos+=4
  elif tag in (5,6):pos+=8;index+=1
  elif tag in (7,16,19,20):pos+=2
  elif tag==8:srefs.append(struct.unpack_from(">H",raw,pos)[0]);pos+=2
  elif tag==15:pos+=3
  else:raise ValueError((tag,pos))
  index+=1
 return [words.get(v) for v in srefs]

def main(jars):
 result={'game_version':'0.98a-RC8','mapped_literals':{},'confirmed_ldc_instructions':{},'per_class':[]}
 for kind,mapping in (('OBF',OBF),('API',API)):
  jar=jars[kind]
  assert hashlib.sha256(jar.read_bytes()).hexdigest()==EXPECTED[kind],('wrong original JAR',kind)
  mapped=0;confirmed=0
  for cl,items in mapping.items():
   with zipfile.ZipFile(jar) as z:
    cp_strings=strings_in_cp(z.read(cl.replace('.', '/')+'.class'))
   p=subprocess.run(['javap','-classpath',str(jar),'-c','-p',cl],capture_output=True,text=True,check=True)
   lines=p.stdout.splitlines();per={}
   for text in items:
    assert text in cp_strings,(kind,cl,'CP missing',repr(text))
    # javap trims trailing ASCII spaces in its comments; the JVM CP check above is byte-exact.
    assert not (text.endswith(' ') and text.rstrip() in cp_strings),(kind,cl,'ambiguous javap label')
    uses=sum(bool(re.search(r'\bldc(?:_w)?\s+#\d+\s+// String ',line)) and line.split('// String ',1)[-1]==text.rstrip() for line in lines)
    assert uses>=1,(kind,cl,repr(text),'not used by ldc')
    per[text]=uses;mapped+=1;confirmed+=uses
   result['per_class'].append({'kind':kind,'class':cl,'literals':len(items),'ldc_uses':sum(per.values())})
  result['mapped_literals'][kind]=mapped;result['confirmed_ldc_instructions'][kind]=confirmed
 assert result['mapped_literals']=={'OBF':23,'API':7}
 print(json.dumps(result,indent=2,ensure_ascii=True))
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--obf',type=Path,required=True);p.add_argument('--api',type=Path,required=True);p.add_argument('--out',type=Path)
 a=p.parse_args();r=main({'OBF':a.obf,'API':a.api})
 if a.out:a.out.write_text(json.dumps(r,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
