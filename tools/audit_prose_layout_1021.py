#!/usr/bin/env python3
"""Read-only original-vs-localized TXT format checks for Starsector.

This guards directive IDs and numerical tokens in 19 narrative and manual
files. It is NOT a semantic accuracy or completeness test.
"""
import argparse,collections,json,re
from pathlib import Path

PREFIXES=('CATEGORY','CURRENT_CATEGORY','BEGIN','END','ICON','IMAGE','RELATED','RESET','COLOR')
NUMBER=re.compile(r'(?<![A-Za-z])[0-9]{1,4}(?:\.[0-9]+)?%?')
CONTROL=re.compile(r'\{\{([^{}]+)\}\}')

def protect(line):
    cmd=line.strip().split(' ',1)[0]
    if cmd not in PREFIXES:return None
    val=line.strip()[len(cmd):].strip()
    if cmd in ('CATEGORY','BEGIN'):
        # Title labels are player-visible; the key before the first pipe is not.
        return (cmd,val.split('|',1)[0],len(val.split('|')))
    return (cmd,val,None)

def audit(original,translated):
    violations=[];items=[]
    for new in sorted(p for p in translated.rglob('*.txt') if p.is_file()):
        rel=new.relative_to(translated).as_posix();old=original/rel
        if not old.is_file():continue
        if rel.startswith('codex/') or rel.startswith('missions/'):
            a=old.read_text('cp1252');b=new.read_text('ascii');al=a.splitlines();bl=b.splitlines()
            err=[]
            if len(al)!=len(bl):err.append('line count changed')
            for i,(x,y) in enumerate(zip(al,bl),1):
                xkey=protect(x);ykey=protect(y)
                if xkey!=ykey and (xkey or ykey):
                    err.append(f'directive mismatch at line {i}: {xkey[0] if xkey else None}/{ykey[0] if ykey else None}')
            if collections.Counter(NUMBER.findall(a))!=collections.Counter(NUMBER.findall(b)):
                err.append('numeric token values/counts differ')
            if a.count('\\n')!=b.count('\\n'):err.append('literal escaped newline count differs')
            # Keyboard chords, percentages are protected, but highlighted prose
            # is allowed to be translated within {{...}}.
            reserved=lambda s:collections.Counter(q for q in CONTROL.findall(s) if re.fullmatch(r'(?i:(?:Ctrl|Shift|Alt|Tab|Enter|Escape)[-+A-Za-z]*|[0-9]+%)',q))
            if reserved(a)!=reserved(b):err.append('keyboard/percentage markup differs')
            if err:violations.append({'file':rel,'problems':err})
            items.append({'path':rel,'lines':len(al),'directives':sum(protect(q)!=None for q in al),'format_status':'PASS' if not err else 'REVIEW'})
    return {'files':len(items),'status':'PASS' if not violations else 'REVIEW','violations':violations,
        'items':items,'limitations':['Does not check translation meaning, proper names, or all inline formatting','Codex directive IDs and line boundaries/numbers are checked, not all possible game parser constraints']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--original',type=Path,required=True);p.add_argument('--translated',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    r=audit(a.original,a.translated);a.out.write_text(json.dumps(r,indent=2,ensure_ascii=True)+'\n')
    print('Prose layout',r['status'],'files',r['files'],'violations',r['violations'])
    if r['violations']:raise SystemExit(1)