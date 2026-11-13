#!/usr/bin/env python3
"""Explicit 1.0.46 API regression and negative mutation checks."""
from __future__ import annotations
import argparse,csv,hashlib,json,re,shutil,tempfile
from pathlib import Path
from apply_1046 import CHANGES,ADDITIONS,ADD_STATUS,NEW,FIELDS,load,plan,sha
from verify_1046 import check

def run(root):
    root=Path(root)
    base=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    previous=load(base/'TLUMACZENIA_JAR_1042.csv')
    new=load(base/NEW)
    assert len(previous)==5257 and len(new)==5260 and len(CHANGES)==13 and len(ADDITIONS)==3
    assert new[5257:]==[dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=ADD_STATUS) for (cl,en),pl in ADDITIONS.items()]
    # Invert precisely the reviewed literal texts, without rewriting any other columns.
    restored=[]
    for old,cur in zip(previous,new[:5257]):
        y=cur.copy();k=y['source_class'],y['english_literal']
        if k in CHANGES:y['polish_ascii_draft']=CHANGES[k][0]
        assert y==old
        restored.append(y)
    import io
    mem=io.StringIO(newline='');w=csv.DictWriter(mem,fieldnames=FIELDS,lineterminator='\r\n')
    w.writeheader();w.writerows(restored)
    assert sha(mem.getvalue().encode())=='abaa3521fb8906e9686603ea38252cde5e4b00745761ccb11a7588a410bbb9e9'
    samples=0
    for key,(old,now) in CHANGES.items():
        assert key[1].count('%s')==now.count('%s')
        # Synthetic 1, 2, and 5 values, preserving displayed placeholder ordering.
        for number in (1,2,5):
            display=now.replace('%s',str(number))
            assert not re.search(r'\b(?:1|2|5) (?:sekund|miesiecy|kredytow|dni)\b',display)
            assert display.isascii() and '%s' not in display
            samples+=1
    failures=0
    def rejected(action):
        nonlocal failures
        import copy
        before=[x.copy() for x in new]
        try:action(before)
        except ValueError:failures+=1;return
        try:
            # A mutant must never be interpretable as the approved 1.0.46 mapping.
            if before==new:raise AssertionError('No mutation')
            for a,b in zip(new,before):
                k=a['source_class'],a['english_literal']
                expected=CHANGES[k][1] if k in CHANGES else a['polish_ascii_draft']
                if b['polish_ascii_draft']!=expected or any(b[c]!=a[c] for c in FIELDS if c!='polish_ascii_draft'):
                    raise ValueError('Unapproved mutation')
            raise AssertionError('Mutant passed')
        except ValueError:failures+=1
    def mutate(i,field,newtext):
        def f(rows):rows[i][field]=newtext
        return f
    target=next(i for i,r in enumerate(new) if (r['source_class'],r['english_literal']) in CHANGES)
    untouched=next(i for i,r in enumerate(new) if (r['source_class'],r['english_literal']) not in CHANGES)
    rejected(mutate(target,'source_class','bad.Class'))
    rejected(mutate(target,'english_literal','Wrong original key'))
    rejected(mutate(target,'status','REVIEWED_GAMEPLAY_PASS'))
    rejected(mutate(target,'polish_ascii_draft','translated invalid text'))
    rejected(mutate(untouched,'polish_ascii_draft','silent extra patch'))
    rejected(mutate(target,'polish_ascii_draft',new[target]['polish_ascii_draft']+' %s'))
    rejected(mutate(target,'polish_ascii_draft',new[target]['polish_ascii_draft']+'\n'))
    rejected(mutate(target,'polish_ascii_draft',new[target]['polish_ascii_draft'].replace(' ', '  ',1)))
    # Exact two assembled positive/negative balance phrases from the original
    # JVM StringBuilder: prefix + cost/payout + (formerly English) suffix.
    root_map={(x['source_class'],x['english_literal']):x['polish_ascii_draft'] for x in new}
    cl='com.fs.starfarer.api.impl.campaign.AbandonMarketPluginImpl'
    prefix=root_map[(cl,'Abandoning %s, a size %s colony, requires %s in evacuation expenses. Shutting down all operations will generate %s credits, for a net ')]
    suffix=root_map[(cl,' of %s.')]
    assert prefix.endswith('Bilans: ')
    assert suffix==' %s.'
    assert prefix+'koszt'+suffix==prefix+root_map[(cl,'cost')]+suffix
    assert prefix+'zysk'+suffix==prefix+root_map[(cl,'payout')]+suffix
    for sign in ('cost','payout'):
        text=(prefix+root_map[(cl,sign)]+suffix).replace('%s','1')
        assert 'Bilans: '+('koszt' if sign=='cost' else 'zysk')+' 1.' in text
        assert ' of ' not in text and text.isascii()
    assert failures==8
    return {'corrected_existing_literals':13,'new_compound_literals':3,'source_map_restored_byte_identical':True,
            'synthetic_numeric_cases_checked':samples,'negative_mutations_rejected':failures,
            'native_windows_gameplay_tested':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    a=p.parse_args();print(json.dumps(run(a.worktree),indent=2))
