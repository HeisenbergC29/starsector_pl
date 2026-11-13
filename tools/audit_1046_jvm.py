#!/usr/bin/env python3
"""Read-only class constant-pool audit of 1.0.46 API literals.

Does NOT redistribute proprietary game JAR; requires the user's private
Starsector 0.98a-RC8 starfarer.api.jar with the pinned SHA-256.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from apply_1046 import CHANGES,ADDITIONS

ORIGINAL_API_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'

def cp_literals(buf):
    if buf[:4]!=b'\xca\xfe\xba\xbe':raise ValueError('Not Java class')
    count=struct.unpack_from('>H',buf,8)[0]
    pos=10;utf={};refs=[];i=1
    while i<count:
        tag=buf[pos];pos+=1
        if tag==1:
            size=struct.unpack_from('>H',buf,pos)[0];pos+=2
            utf[i]=buf[pos:pos+size];pos+=size
        elif tag in (3,4):pos+=4
        elif tag in (5,6):pos+=8;i+=1
        elif tag in (7,8,16,19,20):
            index=struct.unpack_from('>H',buf,pos)[0];pos+=2
            if tag==8:refs.append(index)
        elif tag in (9,10,11,12,17,18):pos+=4
        elif tag==15:pos+=3
        else:raise ValueError(('Unknown CP tag',tag,i))
        i+=1
    return [utf[x] for x in refs]

def check(jar,keys=None):
    jar=Path(jar)
    if hashlib.sha256(jar.read_bytes()).hexdigest()!=ORIGINAL_API_SHA:raise ValueError('Incorrect original game API SHA256')
    keys=set(CHANGES)|set(ADDITIONS) if keys is None else set(keys)
    checks=[];cache={}
    with zipfile.ZipFile(jar) as z:
        if z.testzip() is not None:raise ValueError('Original JAR invalid ZIP')
        for cls,original in sorted(keys):
            if cls not in cache:
                cache[cls]=cp_literals(z.read(cls.replace('.','/')+'.class'))
            needle=original.encode('utf8')
            count=cache[cls].count(needle)
            if count!=1:raise ValueError(('CONSTANT_String not found exactly once',cls,original[:60],count))
            checks.append({'class':cls,'english_sha256':hashlib.sha256(needle).hexdigest(),'found_in_original_jvm_string_pool':True})
    return {'checked_class_scoped_literals':len(checks),'classes':len(cache),'original_api_sha256':ORIGINAL_API_SHA,
            'all_constants_verified':True,'details':checks}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--original-api',type=Path,required=True);p.add_argument('--out',type=Path)
    a=p.parse_args();r=check(a.original_api)
    if a.out:a.out.write_text(json.dumps(r,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in r.items() if k!='details'},indent=2))
