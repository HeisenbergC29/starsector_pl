#!/usr/bin/env python3
"""Fail-closed structural diff of translated JVM archives against verified originals.

Permits only approved CONSTANT_String changes plus correct manifest digests
(for OBF). Does not modify any JAR. No commercial game files are included.
"""
import argparse
import base64
import collections
import csv
import hashlib
import json
import struct
import zipfile
from pathlib import Path

EXPECTED_ORIG = {
    "OBF": "5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8",
    "API": "a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a",
}


def parse_class(raw):
    if raw[:4] != b'\xca\xfe\xba\xbe':raise AssertionError('not a class file')
    n=struct.unpack_from('>H',raw,8)[0];pos=10;out=[None]*n;idx=1
    while idx<n:
        start=pos;tag=raw[pos];pos+=1;value=ref=None
        if tag==1:
            size=struct.unpack_from('>H',raw,pos)[0];pos+=2;value=raw[pos:pos+size];pos+=size
        elif tag in (3,4,9,10,11,12,17,18):pos+=4
        elif tag in (5,6):pos+=8
        elif tag in (7,8,16,19,20):ref=struct.unpack_from('>H',raw,pos)[0];pos+=2
        elif tag==15:pos+=3
        else:raise AssertionError('invalid constant pool tag '+str(tag))
        out[idx]=(tag,raw[start:pos],value,ref)
        if tag in (5,6):idx+=1
        idx+=1
    return out,raw[pos:]


def digest_manifest_checksums(oldmanifest,newmanifest,original,patched,changed):
    old=oldmanifest.split(b'\r\n\r\n');new=newmanifest.split(b'\r\n\r\n')
    assert len(old)==len(new),'manifest paragraphs changed'
    nmodified=0
    for a,b in zip(old,new):
        if a==b:continue
        al=a.split(b'\r\n');bl=b.split(b'\r\n')
        if al and al[0].startswith(b'Name: '):
            name=(al[0][6:]+b''.join(line[1:] for line in al[1:] if line.startswith(b' '))).decode('utf8')
            assert name in original.namelist(),name
            assert name in changed,('manifest changes for unchanged entry',name)
            assert len(al)==len(bl),name
            for x,y in zip(al,bl):
                if x==y:continue
                assert x.startswith((b'SHA-1-Digest: ',b'MD5-Digest: ')) and y.startswith(x.split(b':')[0]+b': '),name
                algorithm='sha1' if x.startswith(b'SHA-1') else 'md5'
                before=base64.b64encode(getattr(hashlib,algorithm)(original.read(name)).digest())
                after=base64.b64encode(getattr(hashlib,algorithm)(patched.read(name)).digest())
                assert x.split(b': ',1)[1]==before,(name,'bad original manifest digest')
                assert y.split(b': ',1)[1]==after,(name,'bad patched manifest digest')
            nmodified+=1
        else:raise AssertionError('non-digest manifest edit')
    return nmodified


def audit(label,source,target,mapping):
    dig=hashlib.sha256(source.read_bytes()).hexdigest();assert dig==EXPECTED_ORIG[label],(label,dig)
    table=collections.defaultdict(dict)
    with mapping.open(newline='',encoding='utf8') as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        path=r['source_class'].replace('.','/')+'.class'
        src=r['english_literal'].encode('utf8');dst=r['polish_ascii_draft'].encode('ascii')
        assert src not in table[path] or table[path][src]==dst
        table[path][src]=dst
    report=collections.Counter();changed={}
    with zipfile.ZipFile(source) as a,zipfile.ZipFile(target) as b:
        assert a.namelist()==b.namelist(),'ZIP entries changed'
        for name in a.namelist():
            old=a.read(name);new=b.read(name)
            if old==new:
                report['unchanged_entries']+=1;continue
            changed[name]=True
            if name=='META-INF/MANIFEST.MF':continue
            assert name.endswith('.class'),('non-class entry changed',name)
            before,tail1=parse_class(old);after,tail2=parse_class(new)
            assert old[:8]==new[:8] and tail1==tail2 and len(before)<=len(after),('bytecode changed',name)
            verified_appends=[]
            for i in range(1,len(before)):
                x=before[i];y=after[i]
                if x==y:continue
                assert x is not None and y is not None and x[0]==y[0]==8,('unapproved CP entry change',name,i)
                assert x[3]<len(before) and len(before)<=y[3]<len(after),('invalid new string ref',name,i)
                src=before[x[3]];dst=after[y[3]]
                assert src[0]==dst[0]==1 and table[name].get(src[2])==dst[2],('unapproved string',name,repr(src[2][:70]))
                verified_appends.append(y[3]);report['approved_string_refs']+=1
            assert set(verified_appends)==set(range(len(before),len(after))),('new strings not referenced or extra',name)
            for i in verified_appends:
                assert after[i][0]==1,('added non-utf8 constant',name,i)
            report['changed_classes']+=1
        if 'META-INF/MANIFEST.MF' in changed:
            report['changed_manifest_sections']=digest_manifest_checksums(a.read('META-INF/MANIFEST.MF'),b.read('META-INF/MANIFEST.MF'),a,b,changed)
        assert len(changed)==report['changed_classes']+int('META-INF/MANIFEST.MF' in changed)
        report['csv_rows']=len(rows)
    return dict(report)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('label',choices=['OBF','API']);ap.add_argument('original',type=Path);ap.add_argument('patched',type=Path);ap.add_argument('csv',type=Path)
    args=ap.parse_args();print(json.dumps(audit(args.label,args.original,args.patched,args.csv),indent=2))

if __name__=='__main__':main()