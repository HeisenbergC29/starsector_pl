#!/usr/bin/env python3
"""Adversarial offline regression tests for the 77-row 1.0.41 grammar-only delta."""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from apply_1041 import readmap
from verify_1041 import verify_delta

def run(worktree):
    root=Path(worktree)/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    old=readmap(root/'TLUMACZENIA_JAR_1040.csv')
    new=readmap(root/'TLUMACZENIA_JAR_1041.csv')
    passed=verify_delta(old,new)
    touched=[i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
    untouched=[i for i,(a,b) in enumerate(zip(old,new)) if a==b]
    assert len(touched)==77 and len(untouched)==5180
    cases=[]
    def attempt(label,change):
        a=copy.deepcopy(old);b=copy.deepcopy(new)
        change(a,b)
        try:verify_delta(a,b)
        except (AssertionError,ValueError,KeyError):cases.append(label);return
        raise AssertionError('Tampering escaped verification: '+label)
    ti=touched[0];tj=touched[1];ui=untouched[0]
    attempt('remove reviewed row',lambda a,b:b.pop(ti))
    attempt('add unapproved row',lambda a,b:b.append(copy.deepcopy(b[ti])))
    attempt('wrong translated quantity',lambda a,b:b[ti].__setitem__('polish_ascii_draft',a[ti]['polish_ascii_draft']))
    attempt('uppercase typo',lambda a,b:b[ti].__setitem__('polish_ascii_draft',b[ti]['polish_ascii_draft']+'!'))
    attempt('unapproved unrelated row',lambda a,b:b[ui].__setitem__('polish_ascii_draft',b[ui]['polish_ascii_draft']+'!'))
    attempt('unexpected edited status',lambda a,b:b[ti].__setitem__('status','FAKE_VERIFIED'))
    attempt('unexpected edited class',lambda a,b:b[ti].__setitem__('source_class','fake.Class'))
    attempt('unexpected edited English literal',lambda a,b:b[ti].__setitem__('english_literal','fake literal'))
    attempt('non-ASCII in Polish',lambda a,b:b[ti].__setitem__('polish_ascii_draft','błędne'))
    attempt('duplicate technical class and source pair',lambda a,b:b[tj].update({'source_class':b[ti]['source_class'],'english_literal':b[ti]['english_literal']}))
    attempt('input baseline changed',lambda a,b:a[ti].__setitem__('polish_ascii_draft',a[ti]['polish_ascii_draft']+'a'))
    attempt('input status changed',lambda a,b:a[ti].__setitem__('status','FAKE_REVIEW'))
    attempt('swapped approved translations',lambda a,b:(b[ti].__setitem__('polish_ascii_draft',new[tj]['polish_ascii_draft']),b[tj].__setitem__('polish_ascii_draft',new[ti]['polish_ascii_draft'])))
    attempt('extra map row with fake hidden entry',lambda a,b:b.insert(ui,copy.deepcopy(b[ui])))
    assert len(cases)==14
    return {'legitimate_delta':'PASS','negative_cases_passed':len(cases),'negative_cases':cases,'approved':passed}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);a=p.parse_args()
    print(json.dumps(run(a.worktree),indent=2))
