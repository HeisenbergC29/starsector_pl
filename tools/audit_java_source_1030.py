#!/usr/bin/env python3
"""Lex omitted Starsector .java scripts without treating comments as display strings.

Read-only supplement for the 529 unmodified data-file coverage audit.
The listing is diagnostic; UI reachability still requires inspecting call sites.
"""
from pathlib import Path
import argparse,collections,json,re

def java_strings(src: str):
    results=[];i=0;n=len(src);line=1;mode='code';q='';start=0;sl=0
    while i<n:
        c=src[i];nx=src[i+1] if i+1<n else ''
        if c=='\n':line+=1
        if mode=='code':
            if c=='/' and nx=='/':mode='line_comment';i+=2;continue
            if c=='/' and nx=='*':mode='block_comment';i+=2;continue
            if c in ('"',"'"):
                mode='string' if c=='"' else 'char';q=c;start=i+1;sl=line
        elif mode=='line_comment':
            if c=='\n':mode='code'
        elif mode=='block_comment':
            if c=='*' and nx=='/':mode='code';i+=2;continue
        else:
            if c=='\\':i+=2;continue
            if c==q:
                if mode=='string':results.append((sl,src[start:i]))
                mode='code'
        i+=1
    return results

def audit(original:Path,overlay:Path):
    src=original/'data' if (original/'data').is_dir() else original
    dst=overlay/'data' if (overlay/'data').is_dir() else overlay
    omitted=sorted(f for f in src.rglob('*.java') if not (dst/f.relative_to(src)).exists())
    assert len(omitted)==50,len(omitted)
    rows=[];multiword=[]
    for file in omitted:
        code=file.read_text('utf8')
        ls=java_strings(code)
        for line,value in ls:
            rec={'file':str(file.relative_to(src)),'line':line,'literal':value}
            rows.append(rec)
            if re.search(r'[A-Za-z]+\s+[A-Za-z]+',value) and not value.startswith(('graphics/','data/','com.')):
                multiword.append(rec)
    summary={'omitted_java_files':len(omitted),'active_lexical_string_literals':len(rows),
             'literals_with_two_or_more_english_words':len(multiword),
             'candidate_classes':sorted(set(r['file'] for r in multiword)),
             'cannot_infer_runtime_UI_solely_from_lexing':True}
    return summary,{'summary':summary,'source_literals':rows,'english_phrase_candidates':multiword}

def main():
    p=argparse.ArgumentParser()
    for s in ('original','localized','out','summary'):
        p.add_argument('--'+s,type=Path,required=True)
    args=p.parse_args();summary,full=audit(args.original,args.localized)
    args.out.write_text(json.dumps(full,ensure_ascii=True,indent=2)+'\n')
    args.summary.write_text(json.dumps(summary,ensure_ascii=True,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=True,indent=2))
if __name__=='__main__':main()
