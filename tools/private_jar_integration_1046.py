#!/usr/bin/env python3
"""Private real-JAR integration for Starsector PL 1.0.46.

Input original jars are commercially licensed and never bundled in reports,
mod packages or GitHub. The Linux patchers are built from public source in CI.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,shutil,struct,subprocess,tempfile,zipfile
from pathlib import Path

ORIGINAL_SHA={'OBF':'5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8',
              'API':'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def split_class(data):
    if data[:4]!=b'\xca\xfe\xba\xbe':raise ValueError('Not a JVM class')
    count=struct.unpack_from('>H',data,8)[0]
    pos=10;cp=[None];string_refs=set();i=1
    while i<count:
        start=pos;tag=data[pos];pos+=1
        if tag==1:
            n=struct.unpack_from('>H',data,pos)[0];pos+=2+n
        elif tag in (3,4,9,10,11,12,17,18):pos+=4
        elif tag in (5,6):pos+=8
        elif tag in (7,8,16,19,20):
            if tag==8:string_refs.add(struct.unpack_from('>H',data,pos)[0])
            pos+=2
        elif tag==15:pos+=3
        else:raise ValueError(('Bad CP tag',tag,i))
        cp.append((tag,data[start+1:pos]))
        if tag in (5,6):cp.append(None);i+=1
        i+=1
    return cp,string_refs,data[pos:]

def verify_class(original,patched,entry):
    a,arefs,atail=split_class(original);b,brefs,btail=split_class(patched)
    if atail!=btail:raise ValueError((entry,'Executable Java section differs'))
    if len(b)<len(a):raise ValueError((entry,'Constant pool shrunk'))
    changed=0
    for i,(x,y) in enumerate(zip(a,b)):
        if x==y:continue
        if x is None:
            if y is not None:raise ValueError((entry,'CP slot changed'))
            continue
        if y is None or x[0]!=y[0]:raise ValueError((entry,'CP tag changed',i))
        if x[0]==1:
            if i not in arefs:raise ValueError((entry,'Non-String UTF8 changed',i))
        elif x[0]!=8:raise ValueError((entry,'Unexpected nonstring CP change',x[0]))
        changed+=1
    for i,y in enumerate(b[len(a):],len(a)):
        if y is not None and y[0]!=1:raise ValueError((entry,'Unexpected new CP entry',i,y[0]))
    return {'changed_cp_entries':changed,'appended_entries':len(b)-len(a)}

def verify_jar(old,new,kind):
    if sha(old)!=ORIGINAL_SHA[kind]:raise ValueError('Wrong original '+kind)
    totals=collections.Counter();changed_classes=0
    with zipfile.ZipFile(old) as a, zipfile.ZipFile(new) as b:
        if a.testzip() is not None or b.testzip() is not None:raise ValueError('Corrupt JAR ZIP')
        if set(a.namelist())!=set(b.namelist()):raise ValueError('JAR members altered')
        for name in a.namelist():
            o=a.read(name);p=b.read(name)
            if o==p:totals['unchanged_entries']+=1;continue
            if name.endswith('.class'):
                z=verify_class(o,p,name)
                changed_classes+=1
                totals.update(z)
            elif kind=='OBF' and name.upper()=='META-INF/MANIFEST.MF':totals['manifest_changes']+=1
            else:raise ValueError((kind,name,'Unexpected non-class member changed'))
    return {'jar':kind,'changed_classes':changed_classes,'patched_sha256':sha(new),**totals}

def invoke(binary,core,action):
    args=[str(binary),'--game',str(core),'--mode',action.removeprefix('--')] if binary.name.startswith('obf_') else [str(binary),'--game',str(core),action,'--yes']
    run=subprocess.run(args,capture_output=True,text=True,timeout=90)
    return run

def run(obf_bin,api_bin,obf_original,api_original):
    obf_bin=Path(obf_bin).resolve();api_bin=Path(api_bin).resolve()
    original={'OBF':Path(obf_original),'API':Path(api_original)}
    for k,p in original.items():
        if sha(p)!=ORIGINAL_SHA[k]:raise ValueError('Incorrect source SHA: '+k)
    with tempfile.TemporaryDirectory(prefix='ss46_private_') as temp:
        core=Path(temp)/'starsector-core';core.mkdir()
        names={'OBF':'starfarer_obf.jar','API':'starfarer.api.jar'}
        paths={k:core/name for k,name in names.items()}
        for k in paths:shutil.copy2(original[k],paths[k])
        # Fresh installation against two SHA-pinned original archives.
        for label,binary in [('OBF',obf_bin),('API',api_bin)]:
            r=invoke(binary,core,'--apply')
            if r.returncode:
                raise RuntimeError(('Fresh install failed',label,r.returncode,r.stdout[-1000:],r.stderr[-1000:]))
        result={'version':'1.0.46','fresh_install_results':[], 'no_private_jar_redistributed':True}
        hashes={k:sha(paths[k]) for k in paths}
        for k in ('OBF','API'):
            if hashes[k]==ORIGINAL_SHA[k]:raise ValueError((k,'No JAR modification'))
            result['fresh_install_results'].append(verify_jar(original[k],paths[k],k))
        # Real idempotence and byte-for-byte no-op.
        for k,binary in [('OBF',obf_bin),('API',api_bin)]:
            r=invoke(binary,core,'--apply')
            if r.returncode or sha(paths[k])!=hashes[k]:
                raise RuntimeError(('Invalid same-version reapply',k,r.returncode,r.stdout[-500:],r.stderr[-500:]))
        result['same_version_noop']='PASS'
        # Tamper only with central ZIP metadata; archive remains structurally readable.
        bad=bytearray(paths['API'].read_bytes());cen=bad.find(b'PK\x01\x02')
        if cen<0:raise ValueError('ZIP central directory missing')
        bad[cen+12]^=1;paths['API'].write_bytes(bad)
        with zipfile.ZipFile(paths['API']) as z:
            if z.testzip() is not None:raise ValueError('Tamper invalid ZIP payload')
        r=invoke(api_bin,core,'--apply')
        if r.returncode==0 or paths['API'].read_bytes()!=bad:
            raise ValueError('Patch failed to refuse tampered installed JAR')
        result['tampered_zip_metadata_refusal']='PASS'
        # Retest a valid patch after refusing the damaged archive.
        # Reconstruct the known-good state from the private original; never
        # silently 'repair' the corrupted ZIP while it is under test.
        paths['API'].write_bytes(original['API'].read_bytes())
        r=invoke(api_bin,core,'--apply')
        if r.returncode or sha(paths['API'])!=hashes['API']:
            raise ValueError(('Clean fresh API patch after tamper refused',r.returncode,r.stderr[-500:]))
        for k,binary in [('API',api_bin),('OBF',obf_bin)]:
            r=invoke(binary,core,'--restore')
            if r.returncode or sha(paths[k])!=ORIGINAL_SHA[k]:
                raise RuntimeError(('Original restore failed',k,r.returncode,r.stdout[-600:],r.stderr[-600:]))
        result['both_original_jars_restored_byte_identical']='PASS'
        return result
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--obf-linux',type=Path,required=True);p.add_argument('--api-linux',type=Path,required=True)
    p.add_argument('--original-obf',type=Path,required=True);p.add_argument('--original-api',type=Path,required=True)
    p.add_argument('--out',type=Path)
    a=p.parse_args();result=run(a.obf_linux,a.api_linux,a.original_obf,a.original_api)
    if a.out:a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
