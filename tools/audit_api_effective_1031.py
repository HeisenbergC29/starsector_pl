#!/usr/bin/env python3
"""Verifiable status-vs-actual-patch audit for Starsector 0.98a-RC8 API.

Only original private game JARs may be passed at runtime; never publish them.
The current Go patcher applies *all* map rows independent of status.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,struct,zipfile
from pathlib import Path

ORIGINAL_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
PATCHED_1030_SHA='f1927b0fbea90e41c049e95b954f97acfcf9e59496c89371b774ad0e12cea4e6'
DRAFT_STATUSES=('DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME')


def class_literals(data:bytes)->collections.Counter:
    """Return exact JVM CONSTANT_String usage, not arbitrary UTF8 identifiers."""
    if len(data)<10 or data[:4]!=b'\xca\xfe\xba\xbe':raise ValueError('bad class magic')
    count=struct.unpack_from('>H',data,8)[0]
    cp={};pos=10;i=1
    while i<count:
        if pos>=len(data):raise ValueError('truncated constant pool')
        tag=data[pos];pos+=1
        if tag==1:
            n=struct.unpack_from('>H',data,pos)[0];pos+=2
            cp[i]=(tag,data[pos:pos+n]);pos+=n
        elif tag in (3,4,9,10,11,12,17,18):pos+=4
        elif tag in (5,6):pos+=8;i+=1
        elif tag in (7,8,16,19,20):cp[i]=(tag,struct.unpack_from('>H',data,pos)[0]);pos+=2
        elif tag==15:pos+=3
        else:raise ValueError(f'unknown JVM constant tag {tag}')
        i+=1
        if pos>len(data):raise ValueError('truncated JVM pool entry')
    result=collections.Counter()
    for kind,index in cp.values():
        if kind!=8:continue
        if index not in cp or cp[index][0]!=1:raise ValueError('invalid CONSTANT_String reference')
        result[cp[index][1].decode('utf-8',errors='replace')]+=1
    return result


def rows_from_csv(path:Path)->list[dict]:
    with path.open(encoding='utf8',newline='') as f:
        r=csv.DictReader(f)
        if r.fieldnames!=['source_class','english_literal','polish_ascii_draft','status']:
            raise ValueError('mapping header mismatch')
        rows=list(r)
    keys=[(x['source_class'],x['english_literal']) for x in rows]
    if len(keys)!=len(set(keys)):raise ValueError('duplicate map keys')
    return rows


def audit(rows:list[dict],original:Path,patched:Path)->dict:
    for p,sha in ((original,ORIGINAL_SHA),(patched,PATCHED_1030_SHA)):
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        if digest!=sha:raise ValueError(f'JAR hash mismatch: {p.name}: {digest}')
    by_class=collections.defaultdict(list)
    for r in rows:by_class[r['source_class'].replace('.','/')+'.class'].append(r)
    bystatus=collections.defaultdict(collections.Counter)
    missing=[]
    with zipfile.ZipFile(original) as org,zipfile.ZipFile(patched) as mod:
        oldfiles=set(org.namelist());newfiles=set(mod.namelist())
        for path,batch in sorted(by_class.items()):
            before=class_literals(org.read(path)) if path in oldfiles else collections.Counter()
            after=class_literals(mod.read(path)) if path in newfiles else collections.Counter()
            for r in batch:
                stats=bystatus[r['status']];stats['map_rows']+=1
                src=r['english_literal'];dst=r['polish_ascii_draft']
                if src not in before:
                    stats['not_in_original_api']+=1
                    missing.append({'source_class':r['source_class'],'reason':'no original API CONSTANT_String',
                                    'source_sha256':hashlib.sha256(src.encode()).hexdigest()})
                elif src not in after and dst in after:
                    stats['confirmed_patched']+=1
                else:
                    stats['unconfirmed']+=1
                    missing.append({'source_class':r['source_class'],'reason':'not confirmed on patched output',
                                    'source_sha256':hashlib.sha256(src.encode()).hexdigest()})
    expected={
        'DRAFT_ONLY_NOT_INSTALLED':{'map_rows':1008,'confirmed_patched':1006,'not_in_original_api':2},
        'OPTIONAL_PATCHER_NOT_GAME_TESTED':{'map_rows':2295,'confirmed_patched':2295},
        'DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME':{'map_rows':355,'confirmed_patched':355},
    }
    for status,exp in expected.items():
        for field,n in exp.items():
            if bystatus[status][field]!=n:raise AssertionError((status,field,bystatus[status][field],n))
    total=sum(v['map_rows'] for v in bystatus.values())
    installed=sum(v['confirmed_patched'] for v in bystatus.values())
    assert (total,installed,len(missing))==(5219,5217,2),(total,installed,len(missing))
    return {'game_version':'0.98a-RC8','installed_version':'1.0.30',
            'original_api_sha256':ORIGINAL_SHA,'patched_api_sha256':PATCHED_1030_SHA,
            'total_mapping_rows':total,'total_confirmed_patched':installed,
            'status_counts':{k:dict(v) for k,v in sorted(bystatus.items())},
            'draft_optional_rows':sum(bystatus[k]['map_rows'] for k in DRAFT_STATUSES),
            'draft_optional_confirmed_patched':sum(bystatus[k]['confirmed_patched'] for k in DRAFT_STATUSES),
            'draft_uninstalled_label_misleading':True,'not_found':missing,
            'native_gameplay_tested':False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--map',type=Path,required=True)
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--patched',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    result=audit(rows_from_csv(args.map),args.original,args.patched)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('total_mapping_rows','total_confirmed_patched','draft_optional_rows','draft_optional_confirmed_patched','draft_uninstalled_label_misleading')},indent=2))
if __name__=='__main__':main()
