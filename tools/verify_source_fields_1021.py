#!/usr/bin/env python3
"""Reproducible original-vs-translated Starsector data field integrity audit.

Checks immutable bytes outside quoted literals for 833 JSON-like/Java files;
checks 18 CSV files for immutable row/column shape and per-file allowed fields;
records 19 freely-translated prose files as an explicit manual-review scope.
This is a *structural* audit, not proof every literal is translated or displayed.
Usage: python tools/verify_source_fields_1021.py --original ORIGINAL/data --translated worktree/mod/data --out /tmp/source_audit.json
Do not commit proprietary original game data or line-by-line content reports.
"""
import argparse,collections,csv,io,json,re
from pathlib import Path

# Approved user-facing content fields in each original game CSV. Every other
# CSV field, notably id, condition, trigger, fleet id and script, is immutable.
CSV_TEXT_COLUMNS={
'campaign/abilities.csv':{'desc','name'},
'campaign/commodities.csv':{'name'},
'campaign/industries.csv':{'name','desc'},
'campaign/market_conditions.csv':{'name','desc'},
'campaign/procgen/name_gen_data.csv':{'name'},
'campaign/reports.csv':{'subject','summary','assessment'},
'campaign/rules.csv':{'text','options','script'},
'campaign/special_items.csv':{'name','desc','tech/manufacturer'},
'campaign/submarkets.csv':{'name','desc'},
'characters/personalities.csv':{'name','desc'},
'characters/skills/aptitude_data.csv':{'name','description'},
'characters/skills/skill_data.csv':{'name','description','author'},
'hullmods/hull_mods.csv':{'name','desc','short','sModDesc'},
'hulls/ship_data.csv':{'name','designation','tech/manufacturer','logistics n/a reason'},
'hulls/wing_data.csv':{'role desc'},
'shipsystems/ship_systems.csv':{'name'},
'strings/descriptions.csv':{'text1','text2','text3','text4','text5'},
'weapons/weapon_data.csv':{'name','primaryRoleStr','speedStr','trackingStr','customPrimary','customPrimaryHL','customAncillary','accuracyStr','tech/manufacturer'},
}
STRUCTURED_SUFFIXES={'.variant','.ship','.skin','.skill','.faction','.json','.java'}
# These are not valid general-purpose JSON; some Starsector data has C-like syntax.
# A lossless raw-token scanner is used to preserve all code/IDs/whitespace.

def quoted_tokens(raw):
    """Return immutable outside-string skeleton and list of (raw quote token, start, end).

    Starsector's data and Java use double-quoted strings for localizable text.
    Single quotes occur inside names and comments, not as delimiters here.
    """
    parts=[];strings=[];i=0;start=0;n=len(raw)
    while i<n:
        if raw[i]!=34:i+=1;continue
        j=i+1;escape=False
        while j<n:
            if escape:escape=False;j+=1;continue
            if raw[j]==92:escape=True;j+=1;continue
            if raw[j]==34:break
            j+=1
        if j>=n:i+=1;continue
        parts.append(raw[start:i]);parts.append(b'"@LOCALIZED_LITERAL@"')
        strings.append((raw[i:j+1],i,j+1))
        i=j+1;start=i
    parts.append(raw[start:])
    return b''.join(parts),strings


def decode_table(data):
    for enc in ('utf-8-sig','cp1252'):
        try:return data.decode(enc),enc
        except UnicodeDecodeError:continue
    raise ValueError('unknown table encoding')


def fail(out,kind,path,detail):
    out.append({'kind':kind,'path':path,'detail':detail})


def audit_csv(path,original,translated,errors,stats):
    a,enc=decode_table(original);b,benc=decode_table(translated)
    old=list(csv.reader(io.StringIO(a,newline='')))
    new=list(csv.reader(io.StringIO(b,newline='')))
    if len(old)!=len(new):fail(errors,'row_count',path,{'old':len(old),'new':len(new)});return
    if not old or not new or old[0]!=new[0]:fail(errors,'header',path,'CSV headers changed');return
    approved=CSV_TEXT_COLUMNS.get(path)
    if approved is None:fail(errors,'unapproved_csv',path,'Missing CSV field policy');return
    changes=collections.Counter()
    for row,(r1,r2) in enumerate(zip(old[1:],new[1:]),start=2):
        if len(r1)!=len(r2):fail(errors,'csv_width',path,{'row':row,'old':len(r1),'new':len(r2)});continue
        for j,(x,y) in enumerate(zip(r1,r2)):
            if x==y:continue
            col=old[0][j] if j<len(old[0]) else f'<EXTRA_{j}>'
            if col not in approved:fail(errors,'protected_column',path,{'row':row,'column':col})
            elif path=='campaign/rules.csv' and col=='script':
                # Preserve the entire multi-command script byte-for-byte except
                # quoted *label arguments* on a SetTextHighlights line.
                a1=x.encode('cp1252',errors='replace'); b1=y.encode('utf8')
                skeleton_old,tokens_old=quoted_tokens(a1)
                skeleton_new,tokens_new=quoted_tokens(b1)
                okay=skeleton_old==skeleton_new and len(tokens_old)==len(tokens_new)
                if okay:
                    for (old_token,old_start,_),(new_token,_,_) in zip(tokens_old,tokens_new):
                        if old_token==new_token:continue
                        line_start=a1.rfind(b'\n',0,old_start)+1
                        prefix=a1[line_start:old_start].strip()
                        if prefix!=b'SetTextHighlights':okay=False
                if not okay:fail(errors,'script_change',path,{'row':row})
            changes[col]+=1
    stats['csv_columns'][path]=dict(changes)
    stats['csv_values_changed']+=sum(changes.values())


def audit_structured(path,original,translated,errors,stats):
    ax,alist=quoted_tokens(original);bx,blist=quoted_tokens(translated)
    if ax!=bx:fail(errors,'non_string_byte_change',path,{'old_literals':len(alist),'new_literals':len(blist)});return
    assert len(alist)==len(blist)
    changes=0
    for (before,bstart,bend),(after,_,_) in zip(alist,blist):
        if before==after:continue
        changes+=1
        if not after[1:-1].isascii():fail(errors,'nonascii_translation',path,{'offset':bstart})
        if path.endswith('.java'):continue
        # A JSON string immediately followed by ':' can be a key/technical ID.
        rest=original[bend:];match=re.match(rb'\s*:',rest)
        if match:fail(errors,'json_key_change',path,{'offset':bstart})
    stats['structured_values_changed']+=changes
    stats['structured_files']+=1
    stats['structured_by_suffix'][Path(path).suffix]+=1


def audit(original_dir,localized_dir):
    stats={'files_checked':0,'files_identical':0,'files_modified':0,'structured_files':0,
           'structured_values_changed':0,'structured_by_suffix':collections.Counter(),
           'csv_values_changed':0,'csv_columns':{},'plain_text_files':[],
           'data_suffix_counts':collections.Counter()}
    errors=[]
    for target in sorted(p for p in localized_dir.rglob('*') if p.is_file()):
        path=target.relative_to(localized_dir).as_posix()
        source=original_dir/path
        stats['files_checked']+=1;stats['data_suffix_counts'][target.suffix]+=1
        if not source.is_file():fail(errors,'missing_original',path,'No corresponding original file');continue
        old=source.read_bytes();new=target.read_bytes()
        if old==new:stats['files_identical']+=1;continue
        stats['files_modified']+=1
        if target.suffix in STRUCTURED_SUFFIXES:audit_structured(path,old,new,errors,stats)
        elif target.suffix=='.csv':audit_csv(path,old,new,errors,stats)
        elif target.suffix=='.txt':stats['plain_text_files'].append(path)
        else:fail(errors,'unsupported_file_type',path,target.suffix)
    stats['structured_by_suffix']=dict(stats['structured_by_suffix'])
    stats['data_suffix_counts']=dict(stats['data_suffix_counts'])
    stats['csv_files']=len(stats['csv_columns'])
    stats['plain_text_count']=len(stats['plain_text_files'])
    return {'status':'PASS' if not errors else 'FAIL','stats':stats,'violations':errors,'limitations':[
        'A changed Java literal may theoretically still be a technical string; requires manual use-site review.',
        'CSV author field is a UI-visible quote attribution; human names need separate preservation audit.',
        '19 prose files are freely translated and not covered by the literal-only rule.',
        'No claim of semantic translation completeness or Windows runtime testing.'
    ]}

def main():
    p=argparse.ArgumentParser();p.add_argument('--original',type=Path,required=True)
    p.add_argument('--translated',type=Path,required=True);p.add_argument('--out',type=Path)
    a=p.parse_args();result=audit(a.original,a.translated)
    if a.out:a.out.write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
    print('SOURCE_AUDIT',result['status'],{k:v for k,v in result['stats'].items() if k not in ('csv_columns','plain_text_files')},'violations',len(result['violations']))
    if result['violations']:print(json.dumps(result['violations'][:40],indent=2))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()