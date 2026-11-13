#!/usr/bin/env python3
"""1.0.48: 29 original-JVM-verified numerical Polish API declension repairs.

Only class-scoped translated text changes in the API CSV; not identifiers or JVM code.
The explicit source inventory is locked to a 1.0.47 baseline hash and row keys.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path

OLD='TLUMACZENIA_JAR_1047.csv'
NEW='TLUMACZENIA_JAR_1048.csv'
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
OLD_SHA='9a36861c53e6508f8082a1a2b845e36e6c5d76f44dd1918b3b8e151ae06eaebd'
# Pre-audited exact inventory: 29 class-scoped API entries, NOT source-only data/.
BAD=re.compile(r'%s (?:dni(?:ach)?|kredytow|punkt(?:ami|ow)?|osob|okretow|jednostek|sekund)\b')
EXPECTED=29
EXPECTED_CLASSES=19

def sha(data):return hashlib.sha256(data).hexdigest()
def readmap(path):
    with Path(path).open(encoding='utf8',newline='') as f:
        it=csv.DictReader(f)
        if it.fieldnames!=FIELDS:raise ValueError('Wrong API map columns')
        return list(it)
def once(v,a,b):
    if v.count(a)!=1:raise ValueError(('Expected exactly one change',a,v.count(a)))
    return v.replace(a,b)

def grammar(text):
    if 'Mozna stabilizowac tylko kolonie z co najmniej %s punktami niedawnych niepokojow.' in text:
        text=once(text,'Mozna stabilizowac tylko kolonie z co najmniej %s punktami niedawnych niepokojow.',
                'Stabilizacja wymaga co najmniej %s pkt niedawnych niepokojow na kolonii.')
    # Neutral abbreviations avoid singular/plural mismatch for 1, 2 and 5.
    # Preserve a sentence-ending full stop instead of creating doubled periods.
    for word,abbrev in [('kredytow','kred.'),('osob','os.'),('punkt','pkt'),('punktow','pkt'),('okretow','okr.')]:
        text=text.replace('%s '+word+'.','%s '+abbrev+('' if abbrev.endswith('.') else '.'))
        text=text.replace('%s '+word,'%s '+abbrev)
    text=text.replace('%s dniach','%s dn.')
    text=text.replace('%s dni.','%s dn.')
    text=text.replace('%s dni','%s dn.')
    text=text.replace('%s sekund','%s s')
    if 'pktami' in text or 'dn..' in text or 'kred..' in text or 'os..' in text or 'okr..' in text:
        raise ValueError('Bad grammar punctuation')
    return text

def plan(rows):
    if len(rows)!=5260:raise ValueError('Expected 5260 API rows')
    affected={};inventory=[]
    for row in rows:
        cl,en,old=row['source_class'],row['english_literal'],row['polish_ascii_draft']
        if cl.startswith('data/') or not BAD.search(old):continue
        key=cl,en
        if key in affected:raise ValueError(('Duplicate source key',key))
        new=grammar(old)
        if new==old or BAD.search(new):raise ValueError(('Incomplete change',key))
        if not new.isascii() or not old.isascii():raise ValueError(('Non ASCII',key))
        for token in ('%s','%d','%f','%%','\n','\t'):
            if old.count(token)!=new.count(token) or en.count(token)!=new.count(token):
                raise ValueError(('Placeholder count changed',key,token))
        if old[:1].isspace()!=new[:1].isspace() or old[-1:].isspace()!=new[-1:].isspace():
            raise ValueError(('Boundary whitespace changed',key))
        affected[key]=(old,new)
        inventory.append((cl,en,old,new,row['status']))
    if len(inventory)!=EXPECTED or len({x[0] for x in inventory})!=EXPECTED_CLASSES:
        raise ValueError(('Wrong audited inventory',len(inventory),len({x[0] for x in inventory})))
    digest=sha(json.dumps(inventory,ensure_ascii=True,separators=(',',':')).encode('ascii'))
    return affected,inventory,digest

def apply(root):
    root=Path(root);folder=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
    old=folder/OLD;new=folder/NEW
    if new.exists():raise FileExistsError(new)
    if sha(old.read_bytes())!=OLD_SHA:raise ValueError('Wrong source map')
    rows=readmap(old);edits,inventory,digest=plan(rows)
    for r in rows:
        k=(r['source_class'],r['english_literal'])
        if k in edits:r['polish_ascii_draft']=edits[k][1]
    with new.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
    def rewrite(path,replacements):
        p=root/path;s=p.read_text('utf8')
        for a,b in replacements:s=once(s,a,b)
        p.write_text(s,encoding='utf8')
    rewrite('buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go',[
        ('const version = "1047"','const version = "1048"'),
        ('const exeVersion = "1.0.47"','const exeVersion = "1.0.48"'),
        ('"1040", "1041", "1042", "1046", version}', '"1040", "1041", "1042", "1046", "1047", version}'),
        ('PL ASCII patch up to 1.0.47','PL ASCII patch up to 1.0.48')])
    rewrite('buildtools/NARZEDZIA_INSTALATOR/main.go', [('const edition = "1.0.47"','const edition = "1.0.48"')])
    m=root/'mod/mod_info.json';metadata=json.loads(m.read_text('utf8'))
    if metadata['version']!='1.0.47':raise ValueError('Wrong baseline mod version')
    metadata['version']='1.0.48';metadata['description']=once(metadata['description'],'1.0.47','1.0.48')
    m.write_text(json.dumps(metadata,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    rewrite('mod/CZYTAJ.txt',[('STARSECTOR PL ASCII 1.0.47','STARSECTOR PL ASCII 1.0.48')])
    with (root/'mod/CZYTAJ.txt').open('a',encoding='utf8') as f:
        f.write('\nPoprawiono 29 wyswietlanych liczb w wynagrodzeniach, zleceniach, statusie kolonii oraz opisach okretow; bez zmiany dzialania gry.\n')
    return {'version':'1.0.48','rows_corrected':len(edits),'classes':EXPECTED_CLASSES,
        'review_inventory_sha256':digest,'old_map_sha256':OLD_SHA,'new_map_sha256':sha(new.read_bytes()),
        'status_unchanged':True,'new_entries':0,'data_changes':0,
        'review': [{'source_class':cl,'english_literal_sha256':sha(en.encode()),'old_polish_sha256':sha(old.encode()),'new_polish_sha256':sha(new.encode()),'source_status':status} for cl,en,old,new,status in inventory]}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--report',type=Path)
    a=p.parse_args();ret=apply(a.worktree)
    if a.report:a.report.write_text(json.dumps(ret,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in ret.items() if k!='review'},indent=2))
