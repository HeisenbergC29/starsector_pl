#!/usr/bin/env python3
"""Audit real JVM CONSTANT_String values, not javap's escaped text display.

Important: a string absent from a translation map is NOT automatically UI-visible.
The private full report may include copyrighted text; do not publish its excerpts
or source JAR. Only this tool and summary counters belong in public GitHub.
"""
import argparse
import collections
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path
from audit_1015_jars import parse_class

SHA={
 'OBF':'5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8',
 'API':'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a',
}


def is_readable_candidate(s):
    """Ranking heuristic, deliberately does not certify in-game visibility."""
    if len(s)<20 or len(s)>7000 or not s.isprintable() and s.count('\n')>8:return False
    if not re.search(r'[A-Za-z]{3,} [A-Za-z]{3,}',s):return False
    if s.startswith(('graphics/','data/','package ','com.fs.','http://','https://')):return False
    if re.search(r'(?i)(error loading|failed to parse|exception:|not found in packages|debug|classnotfound)',s):return False
    return True


def audit(label,source,mapfile):
    actual=hashlib.sha256(source.read_bytes()).hexdigest()
    assert actual==SHA[label],(label,'unexpected game version',actual)
    fields=['source_class','english_literal','polish_ascii_draft','status']
    with mapfile.open(newline='',encoding='utf8') as f:
        reader=csv.DictReader(f);assert reader.fieldnames==fields
        maprows=list(reader)
    mapping=collections.defaultdict(set)
    for row in maprows:
        mapping[row['source_class'].replace('.','/')+'.class'].add(row['english_literal'])
    existing=collections.Counter();untranslated=collections.defaultdict(list)
    absent=[];sampled=[]
    jarclasses=set()
    with zipfile.ZipFile(source) as z:
        for name in z.namelist():
            if not name.endswith('.class'):continue
            jarclasses.add(name)
            try: cp,_=parse_class(z.read(name))
            except (AssertionError,IndexError):continue
            literals=set()
            for row in cp:
                if row is None or row[0]!=8:continue
                if row[3]>=len(cp) or cp[row[3]] is None or cp[row[3]][0]!=1:continue
                raw=cp[row[3]][2]
                try: val=raw.decode('utf8')
                except UnicodeDecodeError:continue # Modified UTF8; not a human-readable candidate
                literals.add(val)
            existing['classes_examined']+=1
            existing['total_unique_class_literals']+=len(literals)
            found=literals & mapping[name]
            existing['mapped_unique_literals']+=len(found)
            existing['unmapped_unique_literals']+=len(literals-found)
            ranked=[x for x in sorted(literals-mapping[name]) if is_readable_candidate(x)]
            existing['candidate_literals_heuristic']+=len(ranked)
            if ranked:
                untranslated[name]=ranked
                sampled.append((len(ranked),name))
            notfound=mapping[name]-literals
            for key in notfound:absent.append({'class':name.removesuffix('.class').replace('/','.'),'source_literal':key})
    # Historical map rows may address external source files or the *other* JAR.
    # Missing whole classes must be counted, not silently dropped from the audit.
    missing_classes=sorted(set(mapping)-jarclasses)
    for name in missing_classes:
        for key in mapping[name]:
            absent.append({'class':name.removesuffix('.class').replace('/','.'),
                           'source_literal':key,'reason':'target_class_absent_from_jar'})
    existing['source_rows']=len(maprows)
    existing['missing_mapped_classes']=len(missing_classes)
    existing['not_found_map_rows']=len(absent)
    existing['classes_with_candidates']=len(untranslated)
    return {'version':label,'sha256':actual,'stats':dict(existing),
       'top_candidate_classes':[{'class':n.removesuffix('.class').replace('/','.'),'candidate_count':k} for k,n in sorted(sampled,reverse=True)[:100]],
       'unmapped_readable_candidates':[{'class':n.removesuffix('.class').replace('/','.'),'strings':vals} for n,vals in untranslated.items()],
       'mapped_but_not_present':absent,
       'warning':'UNMAPPED is not proof of player visibility; heuristic candidates need bytecode context review.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',choices=['OBF','API'],required=True)
    p.add_argument('--jar',type=Path,required=True);p.add_argument('--csv',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();res=audit(a.label,a.jar,a.csv)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(res,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
    print(json.dumps({'jar':a.label,'stats':res['stats'],'output':str(a.out)},indent=2))

if __name__=='__main__':main()
