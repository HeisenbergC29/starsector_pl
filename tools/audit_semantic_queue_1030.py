#!/usr/bin/env python3
"""Generate a private, deterministic review queue for active draft/optional API strings.

This tool deliberately does not claim that machine heuristics prove semantic correctness.
Output contains English source strings from commercial Starsector and must remain private.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,re
from pathlib import Path
REVIEW={'OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
FORMAT=re.compile(r'%(?:\d+\$)?[-+#0,]*(?:\d+|\*)?(?:\.\d+)?[sdfc]|\$[a-zA-Z_][\w]*|\{\d+\}|\\[ntr]')
LITERAL_EN=re.compile(r'\b(?:story|points?|skills?|fleet|officer|hullmod|bonus|cargo|shield|supply|damage|combat|readiness|captain|colon(?:y|ies)|mission|credits)\b',re.I)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('mapping',type=Path)
    ap.add_argument('--private-out',type=Path,required=True)
    ap.add_argument('--summary-out',type=Path,required=True)
    args=ap.parse_args()
    with args.mapping.open(encoding='utf8',newline='') as f:
        rows=list(csv.DictReader(f))
    wanted=[r for r in rows if r['status'] in REVIEW]
    expected={'1029':3659,'1030':3658}.get(args.mapping.stem.rsplit('_',1)[-1])
    assert expected is not None and len(wanted)==expected,(args.mapping,len(wanted),collections.Counter(r['status'] for r in wanted))
    inconsistencies=collections.defaultdict(set)
    for r in rows:inconsistencies[r['english_literal']].add(r['polish_ascii_draft'])
    results=[]
    for r in wanted:
        src=r['english_literal'];target=r['polish_ascii_draft'];flags=[]
        if FORMAT.findall(src)!=FORMAT.findall(target):flags.append('CHECK_FORMAT_TOKENS')
        if src==target:flags.append('IDENTICAL_TRANSLATION')
        if LITERAL_EN.search(target):flags.append('ENGLISH_LEXEME_CANDIDATE')
        if len(inconsistencies[src])>1:flags.append('CONTEXT_SPECIFIC_TRANSLATIONS')
        if len(src)<15:flags.append('SHORT_CONTEXT_SENSITIVE')
        if src.startswith(' ')!=target.startswith(' ') or src.endswith(' ')!=target.endswith(' '):flags.append('SPACE_BOUNDARY')
        if src.count('\n')!=target.count('\n'):flags.append('NEWLINE_COUNT')
        id=hashlib.sha256((r['source_class']+'\x00'+src).encode('utf8')).hexdigest()[:16]
        priority=(0 if any(f in flags for f in ('CHECK_FORMAT_TOKENS','SPACE_BOUNDARY','NEWLINE_COUNT'))
                  else 1 if any(f in flags for f in ('ENGLISH_LEXEME_CANDIDATE','IDENTICAL_TRANSLATION'))
                  else 2 if 'CONTEXT_SPECIFIC_TRANSLATIONS' in flags else 3)
        results.append({'id':id,'priority':priority,'status':'UNREVIEWED','reason':flags,
                        'source_class':r['source_class'],'original':src,'translation':target,
                        'mapping_status':r['status']})
    results.sort(key=lambda r:(r['priority'],r['source_class'],r['id']))
    summary={'baseline':'1.0.'+args.mapping.stem.rsplit('_',1)[-1][-2:],'entries_needing_semantic_review':len(results),
             'status_counts':dict(collections.Counter(r['mapping_status'] for r in results)),
             'priority_counts':dict(collections.Counter(str(r['priority']) for r in results)),
             'flag_counts':dict(collections.Counter(f for r in results for f in r['reason'])),
             'meaning_verified_by_this_script':0,'warning':'Heuristic flags are not proof of a translation error; review full class and UI callsites.'}
    args.private_out.write_text(json.dumps({'summary':summary,'queue':results},ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    args.summary_out.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
