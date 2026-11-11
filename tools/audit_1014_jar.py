#!/usr/bin/env python3
"""Verify exact allowed JVM constant-pool mutations from official original to 1.0.14."""
from pathlib import Path
import csv, zipfile, struct, collections, hashlib, sys

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse(raw):
    if raw[:4] != b'\xca\xfe\xba\xbe':raise ValueError('bad class')
    count=struct.unpack_from('>H',raw,8)[0];pos=10;result=[None]*count;i=1
    while i<count:
        start=pos;kind=raw[pos];pos+=1;payload=None;ref=None
        if kind==1:
            size=struct.unpack_from('>H',raw,pos)[0];pos+=2
            payload=raw[pos:pos+size];pos+=size
        elif kind in (3,4,9,10,11,12,17,18):pos+=4
        elif kind in (5,6):pos+=8
        elif kind in (7,8,16,19,20):ref=struct.unpack_from('>H',raw,pos)[0];pos+=2
        elif kind==15:pos+=3
        else:raise ValueError('bad CP tag '+str(kind))
        result[i]=(kind,raw[start:pos],payload,ref)
        if kind in (5,6):i+=1
        i+=1
    return result,raw[pos:]

def audit(original,translated,mapping):
    counts=collections.Counter();errors=[]
    with open(mapping,newline='') as f:
        maps=collections.defaultdict(dict)
        for row in csv.DictReader(f):
            maps[row['source_class'].replace('.','/')+'.class'][row['english_literal'].encode('utf8')]=row['polish_ascii_draft'].encode('utf8')
    with zipfile.ZipFile(original) as a,zipfile.ZipFile(translated) as b:
        assert a.namelist()==b.namelist()
        for name in a.namelist():
            old=a.read(name);new=b.read(name)
            if old==new:
                counts['unchanged_entries']+=1;continue
            if not name.endswith('.class'):
                errors.append('non-class changed: '+name);continue
            before,oldtail=parse(old);after,newtail=parse(new)
            counts['changed_classes']+=1
            if old[:8]!=new[:8] or oldtail!=newtail or len(before)>len(after):
                errors.append('bytecode or header changed: '+name);continue
            actual={}
            for idx in range(1,len(before)):
                x=before[idx];y=after[idx]
                if x==y:continue
                if x is None and y is None:continue
                if not x or not y or x[0]!=8 or y[0]!=8:
                    errors.append('unexpected original CP mutation '+name+' '+str(idx));continue
                if x[3]>=len(before) or y[3]<len(before) or y[3]>=len(after):
                    errors.append('invalid string CP ref '+name+' '+str(idx));continue
                src=before[x[3]];tgt=after[y[3]]
                if src[0]!=1 or tgt[0]!=1:
                    errors.append('invalid string payload ref '+name+' '+str(idx));continue
                expected=maps[name].get(src[2])
                if expected is None or expected!=tgt[2]:
                    errors.append('unapproved string change '+name+' '+repr(src[2][:60]));continue
                actual[tgt[2]]=1;counts['approved_string_refs']+=1
            for x in after[len(before):]:
                if not x or x[0]!=1 or x[2] not in actual:
                    errors.append('unapproved appended CP entry '+name)
    assert not errors, '\n'.join(errors[:30])
    return dict(counts)

if __name__=='__main__':
    r=audit(*sys.argv[1:]);print('JAR_CONSTANT_POOL_AUDIT_PASS',r)