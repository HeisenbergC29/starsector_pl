#!/usr/bin/env python3
"""Conservative count of gender-token candidates remaining in visible dialogue text.

A token occurrence is NOT proof of visible English text: substitutions may be
localized at runtime. Never alter scripts/IDs or interpret the raw counter as
number of translation errors without checking all call contexts.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,re
from pathlib import Path

PAT=re.compile(r'\$[A-Za-z_0-9]*(?:heOrShe|hisOrHer|himOrHer|himOrHerself|manOrWoman)\b',re.I)
SHA='e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a'

def audit(file):
    file=Path(file);raw=file.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('Audit requires exact 1.0.45 rules.csv')
    with file.open('r',encoding='ascii',newline='') as f:
        data=list(csv.DictReader(f))
    counter=collections.Counter();rows=0
    for r in data:
        tokens=PAT.findall(r['text']);counter.update(tokens);rows+=bool(tokens)
    out={'release':'1.0.45','file':'data/campaign/rules.csv',
        'scope':'raw gender-pronoun placeholders, NOT independently confirmed visible English errors',
        'all_csv_rows':len(data),'affected_rows':rows,'placeholder_occurrences':sum(counter.values()),
        'previous_1044_affected_rows':1183,'previous_1044_occurrences':2368,
        'removed_in_1045':93,'repaired_rows_in_1045':44,
        'token_counts':dict(sorted(counter.items())),'java_getter_calls_untouched':219,
        'windows_gameplay_tested':False}
    if out['all_csv_rows']!=11107 or out['affected_rows']!=1139 or out['placeholder_occurrences']!=2275:
        raise ValueError(('Unreviewed corpus difference',len(data),rows,sum(counter.values())))
    if out['previous_1044_occurrences']-out['placeholder_occurrences']!=93 or out['previous_1044_affected_rows']-rows!=44:
        raise ValueError('Declared delta inconsistent with current source')
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('rules',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();result=json.dumps(audit(a.rules),indent=2,ensure_ascii=True)+'\n'
    if a.output:a.output.write_text(result,encoding='utf8')
    print(result,end='')
