#!/usr/bin/env python3
"""Fail-closed 1.1 semantic review ledger with exact map-row fingerprints.

Approval is *offline semantic/context review only*. A real Windows game test
remains required. No author is allowed to change translation text after review
without invalidating its SHA-256 fingerprint.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
from audit_api_effective_1031 import class_literals,rows_from_csv,DRAFT_STATUSES
import zipfile

ALLOW_EVIDENCE={'enum_constructor_label','tooltip_addPara','monthly_report_label'}

def fingerprint(r):
    text='\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft'))
    return hashlib.sha256(text.encode('utf8')).hexdigest()

def fmt_markers(s):
    return re.findall(r'%(?:\d+\$)?[-+#0,]*(?:\d+|\*)?(?:\.\d+)?[sdfc]|\$[a-zA-Z_][\w]*|\{\d+\}',s)

def verify(rows,ledger,original=None,patched=None):
    if ledger.get('schema_version')!=1 or ledger.get('installed_version')!='1.0.30':
        raise AssertionError('unsupported review ledger')
    active={(r['source_class'],fingerprint(r)):r for r in rows}
    seen=set();summary={'reviewed_offline_not_gameplay':0,'evidence':{},'still_need_review':0}
    if len(ledger['reviewed'])!=30:raise AssertionError('expected exactly 30 reviewed rows')
    targets=[]
    for x in ledger['reviewed']:
        cl=x['source_class'];sha=x['row_sha256'];kind=x['evidence']
        if kind not in ALLOW_EVIDENCE or (cl,sha) not in active or (cl,sha) in seen:
            raise AssertionError('review evidence invalid or stale')
        seen.add((cl,sha));r=active[(cl,sha)]
        if r['status'] not in DRAFT_STATUSES:raise AssertionError('row was not pending review')
        if fmt_markers(r['english_literal'])!=fmt_markers(r['polish_ascii_draft']):
            raise AssertionError('changed format placeholders')
        if r['english_literal'].startswith(' ')!=r['polish_ascii_draft'].startswith(' '):
            raise AssertionError('leading separator changed')
        if r['english_literal'].endswith(' ')!=r['polish_ascii_draft'].endswith(' '):
            raise AssertionError('trailing separator changed')
        if not r['polish_ascii_draft'].isascii():raise AssertionError('not ascii')
        targets.append(r)
        summary['evidence'][kind]=summary['evidence'].get(kind,0)+1
    assert summary['evidence']=={'enum_constructor_label':10,'tooltip_addPara':17,'monthly_report_label':3},summary
    pending=[r for r in rows if r['status'] in DRAFT_STATUSES]
    if len(pending)!=3658:raise AssertionError('unexpected draft pool')
    summary['reviewed_offline_not_gameplay']=len(seen)
    summary['still_need_review']=len(pending)-len(seen)
    summary['remaining_windows_gameplay_reviews']=len(pending)
    if (original is None) != (patched is None):raise ValueError('supply both original and patched API JAR')
    if original:
        from audit_api_effective_1031 import ORIGINAL_SHA,PATCHED_1030_SHA
        for jar,expect in ((original,ORIGINAL_SHA),(patched,PATCHED_1030_SHA)):
            if hashlib.sha256(jar.read_bytes()).hexdigest()!=expect:
                raise AssertionError('wrong private JAR SHA256')
        with zipfile.ZipFile(original) as old,zipfile.ZipFile(patched) as new:
            for r in targets:
                cls=r['source_class'].replace('.','/')+'.class'
                if r['english_literal'] not in class_literals(old.read(cls)):
                    raise AssertionError('source literal not found in original JVM pool')
                strings=class_literals(new.read(cls))
                if r['polish_ascii_draft'] not in strings or r['english_literal'] in strings:
                    raise AssertionError('patched JVM text differs from approved offline review')
        summary['confirmed_private_jar_sites']=len(targets)
    else:
        summary['confirmed_private_jar_sites']='not_tested_in_public_CI'
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--map',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
    p.add_argument('--original',type=Path);p.add_argument('--patched',type=Path);p.add_argument('--out',type=Path)
    a=p.parse_args();summary=verify(rows_from_csv(a.map),json.loads(a.ledger.read_text('utf8')),a.original,a.patched)
    if a.out:a.out.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
