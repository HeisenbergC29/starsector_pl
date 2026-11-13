#!/usr/bin/env python3
"""Exact regression proof for 1.0.42. Uses game-owned JARs only when explicitly provided locally."""
from __future__ import annotations
import argparse,hashlib,json,re,sys,zipfile
from pathlib import Path
from apply_1042 import FIELDS,readmap,plan

ORIGINAL_SHA='a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'
EXPECTED_API_1041_SHA='be752bc07ca3965435ad34bab2e12febd80a7883818a430d8c007999b562e5c9'
EXPECTED_API_1042_SHA='ae2cfb7bda28b58e20bd31976e1f399174c9eab564f5b98c192f2464ecf3bcf4'
OBF_SHA='03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a'
BAD_DOT=re.compile(r'(?<!\.)\.\.(?!\.)')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify_delta(before,after):
  planrows,groups,h=plan(before)
  assert len(before)==len(after)==5257
  wanted={(x[0],x[1]):x for x in planrows}
  count=0
  for i,(a,b) in enumerate(zip(before,after)):
    key=a['source_class'],a['english_literal']
    assert key==(b['source_class'],b['english_literal']),(i,'class/English changed')
    assert a['status']==b['status'],(i,'status changed')
    if key in wanted:
      old=wanted[key];assert (a['polish_ascii_draft'],b['polish_ascii_draft'])==(old[2],old[3]),(i,'unapproved punctuation')
      count+=1
    else:assert a==b,('unapproved data change',i,key)
    assert b['polish_ascii_draft'].isascii()
    assert not BAD_DOT.search(b['polish_ascii_draft']),('double period persisted',i,key)
  assert count==15
  assert len({(r['source_class'],r['english_literal']) for r in after})==5257
  return {'corrected_rows':count,'groups':groups,'review_hash':h,'map_rows':len(after),'double_periods_remaining':0}

def verify(root,original=None,patched=None,previous_zip=None):
  root=Path(root);td=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
  before=readmap(td/'TLUMACZENIA_JAR_1041.csv');after=readmap(td/'TLUMACZENIA_JAR_1042.csv')
  out=verify_delta(before,after)
  code=(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go').read_text('utf8')
  assert 'const version = "1042"' in code and 'const exeVersion = "1.0.42"' in code
  assert '"1038", "1040", "1041", version}' in code
  assert 'if hash(current) != r.NewSHA256 {' in code
  assert 'installed JAR has unexpected ZIP bytes; refusing no-op on damaged or repacked archive' in code
  assert 'const edition = "1.0.42"' in (root/'buildtools/NARZEDZIA_INSTALATOR/main.go').read_text('utf8')
  meta=json.loads((root/'mod/mod_info.json').read_text('utf8'))
  assert meta['version']=='1.0.42' and meta['gameVersion']=='0.98a-RC8' and len(meta['replace'])==41
  data={p.relative_to(root/'mod').as_posix():p.read_bytes() for p in (root/'mod/data').rglob('*') if p.is_file()}
  assert len(data)==870 and all(x.isascii() for x in data.values())
  if previous_zip:
    with zipfile.ZipFile(previous_zip) as z:
      prev={k.removeprefix('Starsector_PL_ASCII/'):z.read(k) for k in z.namelist() if k.startswith('Starsector_PL_ASCII/data/')}
    assert data==prev
    out['unchanged_data_files_vs_1041']=870
  if original or patched:
    assert original and patched
    assert sha(original)==ORIGINAL_SHA
    if EXPECTED_API_1042_SHA is not None:assert sha(patched)==EXPECTED_API_1042_SHA
    from verify_story_1033 import proof_class_files,class_entries,texts
    mapping={(r['source_class'],r['english_literal']):r['polish_ascii_draft'] for r in after}
    proof=proof_class_files(Path(original),Path(patched),mapping)
    assert proof['modified_classes']==938 and proof['mapped_string_constants']==5255 and proof['executables_untouched']
    with zipfile.ZipFile(original) as a,zipfile.ZipFile(patched) as b:
      for cls,en,old,new,status in plan(before)[0]:
        entry=cls.replace('.','/')+'.class'
        aa=texts(class_entries(a.read(entry))[0]);bb=texts(class_entries(b.read(entry))[0])
        assert en in aa and new in bb and old not in bb,(cls,en,'unfixed double period')
    out['original_jar_sha256']=sha(original)
    out['patched_jar_sha256']=sha(patched)
    out['jar_proof']=proof
  return out

if __name__=='__main__':
  p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--original-api',type=Path);p.add_argument('--patched-api',type=Path);p.add_argument('--previous-zip',type=Path)
  a=p.parse_args();print(json.dumps(verify(a.worktree,a.original_api,a.patched_api,a.previous_zip),indent=2))
