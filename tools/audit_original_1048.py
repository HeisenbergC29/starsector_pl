#!/usr/bin/env python3
"""Read-only original JVM proof for 1.0.48, no redistribution of game JAR."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from audit_1046_jvm import cp_literals,ORIGINAL_API_SHA
from audit_1047_jvm import verify_shared_her
from apply_1048 import readmap,plan,OLD

def check(jar,prior_map):
    jar=Path(jar)
    digest=hashlib.sha256(jar.read_bytes()).hexdigest()
    if digest!=ORIGINAL_API_SHA:raise ValueError('Wrong source JAR')
    rows=readmap(prior_map);changes,inv,review_sha=plan(rows)
    hits=[];cache={}
    with zipfile.ZipFile(jar) as z:
        if z.testzip() is not None:raise ValueError('Damaged original JVM JAR')
        for cl,en in sorted(changes):
            if cl not in cache:cache[cl]=cp_literals(z.read(cl.replace('.','/')+'.class'))
            if cache[cl].count(en.encode('utf8'))!=1:raise ValueError(('Original JVM literal missing/ambiguous',cl))
            hits.append({'class':cl,'english_sha256':hashlib.sha256(en.encode()).hexdigest(),'source_const_string_count':1})
    shared=verify_shared_her(jar)
    if not shared['same_ldc_constant']:raise ValueError('Unexpected shared her bytecode')
    return {'schema_version':1,'version':'1.0.48','original_api_sha256':digest,
        'original_jvm_string_literals_verified':len(hits),'original_classes':len(cache),
        'review_sha256':review_sha,'details':hits,
        'shared_her_conflict_unresolved':True,'shared_her_evidence':shared,
        'no_original_game_files_published':True,'native_windows_gameplay_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--original-api',required=True,type=Path)
    p.add_argument('--prior-map',required=True,type=Path);p.add_argument('--out',type=Path)
    a=p.parse_args();v=check(a.original_api,a.prior_map)
    if a.out:a.out.write_text(json.dumps(v,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in v.items() if k!='details'},indent=2))
