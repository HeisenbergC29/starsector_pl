#!/usr/bin/env python3
"""Version 1.0.41: remove numerically invalid fixed plurals in 77 active API UI texts.

Never edits executable Java instructions or game identifiers. The set is pinned
by an audited hash of ALL affected original rows. A non-JAR source mapping is
intentionally excluded; it has its own already-corrected mod source file.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path

OLD='TLUMACZENIA_JAR_1040.csv'
NEW='TLUMACZENIA_JAR_1041.csv'
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
# One entry for each replacement. Source strings must contain the exact numeric
# placeholder. Abbreviations are Polish ASCII and independent of grammatical number.
REPLACEMENTS=(('%s jednostek','%s jedn.'),('%s punktow','%s pkt'),('%s lat swietlnych','%s l. sw.'))
EXPECTED_GROUPS={'unit':40,'point':25,'light_year':12}
EXPECTED_SHA='8edfe27a4ce166d1dad5be44555ccdd13346b7f48c97013051be4321ea30456f'  # audited complete exact row-level inventory
STATUS_NOTE='NUMERIC_GRAMMAR_CHECKED_1041'  # an audit flag, NOT a full semantic-review status

def once(source,old,new):
    if source.count(old)!=1:raise AssertionError((old,source.count(old)))
    return source.replace(old,new)

def readmap(path):
    with path.open('r',encoding='utf8',newline='') as fh:
        rdr=csv.DictReader(fh)
        if rdr.fieldnames!=FIELDS:raise ValueError(('unexpected columns',rdr.fieldnames))
        return list(rdr)

def plan(rows):
    affected=[]
    for row in rows:
        cl,en,old=row['source_class'],row['english_literal'],row['polish_ascii_draft']
        if cl.startswith('data/'):
            continue  # historical source-only SurveyingEquipment.java row: not in API JAR
        new=old
        for a,b in REPLACEMENTS:new=new.replace(a,b)
        if new==old:continue
        if not old.isascii() or not new.isascii():raise ValueError(('nonascii Polish',cl))
        if en.count('%s')!=old.count('%s') or old.count('%s')!=new.count('%s'):
            raise ValueError(('mismatching placeholders',cl,en))
        if old.count('\n')!=new.count('\n') or old.startswith(' ')!=new.startswith(' ') or old.endswith(' ')!=new.endswith(' '):
            raise ValueError(('format drift',cl,en))
        affected.append((cl,en,old,new,row['status']))
    counts={'unit':sum('%s jednostek' in x[2] for x in affected),
            'point':sum('%s punktow' in x[2] for x in affected),
            'light_year':sum('%s lat swietlnych' in x[2] for x in affected)}
    if len(affected)!=77 or counts!=EXPECTED_GROUPS:raise ValueError(('wrong audited inventory',len(affected),counts))
    key=hashlib.sha256(json.dumps(affected,ensure_ascii=True,separators=(',',':')).encode('ascii')).hexdigest()
    if key!=EXPECTED_SHA:raise ValueError(('changed review inventory',key))
    return affected,counts,key

def apply(root):
    root=Path(root)
    src=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    oldpath=src/OLD;newpath=src/NEW
    if newpath.exists():raise FileExistsError(newpath)
    old=readmap(oldpath)
    if len(old)!=5257:raise ValueError('incorrect source map version')
    affected,counts,digest=plan(old)
    indexed={(cl,en):new for cl,en,was,new,status in affected}
    for row in old:
        target=indexed.get((row['source_class'],row['english_literal']))
        if target is not None:row['polish_ascii_draft']=target
    with newpath.open('w',encoding='utf8',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=FIELDS,lineterminator='\r\n')
        writer.writeheader();writer.writerows(old)
    def amend(path,changes):
        s=path.read_text('utf8')
        for a,b in changes:s=once(s,a,b)
        path.write_text(s,encoding='utf8')
    main=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go'
    amend(main,[('const version = "1040"','const version = "1041"'),
                ('const exeVersion = "1.0.40"','const exeVersion = "1.0.41"'),
                ('"1037", "1038", version}','"1037", "1038", "1040", version}'),
                ('PL ASCII patch up to 1.0.40','PL ASCII patch up to 1.0.41'),
                ('if state == version {\n\t\t\tr.Note = "Version already installed. No files modified."',
                 'if state == version {\n\t\t\t// Compare full JAR bytes, not only uncompressed entries.\n\t\t\t// A ZIP with modified headers or damaged local member metadata\n\t\t\t// must not be silently accepted as an installed release.\n\t\t\tif hash(current) != r.NewSHA256 {\n\t\t\t\treturn errors.New("installed JAR has unexpected ZIP bytes; refusing no-op on damaged or repacked archive")\n\t\t\t}\n\t\t\tr.Note = "Version already installed. No files modified."')])
    amend(root/'buildtools/NARZEDZIA_INSTALATOR/main.go',[( 'const edition = "1.0.40"','const edition = "1.0.41"')])
    m=root/'mod/mod_info.json';v=json.loads(m.read_text('utf8'))
    if v['version']!='1.0.40':raise ValueError('wrong version')
    v['version']='1.0.41';v['description']=once(v['description'],'1.0.40','1.0.41')
    m.write_text(json.dumps(v,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    readme=root/'mod/CZYTAJ.txt'
    amend(readme,[('STARSECTOR PL ASCII 1.0.40','STARSECTOR PL ASCII 1.0.41')])
    with readme.open('a',encoding='utf8') as out:
        out.write('\nPoprawiono odmiane ilosci w 77 tekstach API za pomoca jednoznacznych skrotow: jedn., pkt oraz l. sw. (rok swietlny). Dalsze gettery i testy gry Windows pozostaja otwarte.\n')
    print(json.dumps({'release':'1.0.41','corrected_active_api_rows':len(affected),'groups':counts,'map_rows':len(old),'review_sha256':digest},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('worktree',type=Path)
    apply(parser.parse_args().worktree)
