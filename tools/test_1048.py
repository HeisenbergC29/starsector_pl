#!/usr/bin/env python3
"""Independent mutation-based negative tests and 87 numeric render samples."""
from __future__ import annotations
import argparse,copy,csv,hashlib,json,tempfile
from pathlib import Path
from apply_1048 import plan,readmap,OLD,NEW,grammar,EXPECTED
from verify_1048 import check,sha

def run(root):
    root=Path(root); f=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    base=readmap(f/OLD);new=readmap(f/NEW)
    expected,inventory,_=plan(base)
    render=0
    for cl,en,old,updated,status in inventory:
        for value in ('1','2','5'):
            rendered=updated.replace('%s',value)
            if 'jednostke' in rendered or 'kredytow' in rendered or ' punkt ' in rendered or ' punkt.' in rendered:
                raise ValueError(('Grammar not neutral',cl,en,value))
            if any(x in rendered for x in ('dn..','kred..','okr..','os..','pkt..')):
                raise ValueError('Repeated abbreviation punctuation')
            render+=1
    failures={}
    def must_fail(name,callback):
        try:callback()
        except (ValueError,KeyError,AssertionError):failures[name]='REJECTED'
        else:raise AssertionError(('Validator accepted damaged data',name))
    # Known review set must reject modifications of source inventory.
    def custom_mut(row_index,key,val):
        arr=copy.deepcopy(base);arr[row_index][key]=val;plan(arr)
    pick=next(i for i,v in enumerate(base) if (v['source_class'],v['english_literal']) in expected)
    must_fail('unreviewed original source text changed',lambda:custom_mut(pick,'polish_ascii_draft','BROKEN'))
    must_fail('duplicate review mapping row',lambda:plan(base+[base[pick]]))
    must_fail('unrecognized mapping size',lambda:plan(base[:-1]))
    must_fail('missing numeric placeholder',lambda:custom_mut(pick,'english_literal','placeholder tampered'))
    must_fail('non_ASCII_polish',lambda:custom_mut(pick,'polish_ascii_draft',base[pick]['polish_ascii_draft']+'ę'))
    must_fail('lost baseline input',lambda:plan([r for i,r in enumerate(base) if i!=pick]))
    with tempfile.TemporaryDirectory() as d:
        fake=Path(d);sub=fake/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations';sub.mkdir(parents=True)
        (sub/OLD).write_bytes((f/OLD).read_bytes())
        (sub/NEW).write_bytes((f/NEW).read_bytes()+b'\n')
        must_fail('bad target CSV SHA',lambda:check(fake))
    # Readmap can independently reject tampered headers.
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'wrong.csv';p.write_text('id,translation\nfoo,bar\n')
        must_fail('invalid CSV header',lambda:readmap(p))
    result=check(root)
    if len(failures)!=8 or result['corrected_api_rows']!=EXPECTED:raise AssertionError('Incomplete tests')
    return {'rendered_numeric_variants':render,'negative_mutations_rejected':len(failures),
            'negative_cases':failures,'mapping_verified':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
