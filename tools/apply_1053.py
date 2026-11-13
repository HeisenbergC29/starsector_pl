#!/usr/bin/env python3
"""1.0.53: fix three ship-count fragments in the real OBF recovery dialog.

Preserves all JVM executable instructions, identifiers, the existing API map,
and 870 packaged game data files. OBF table is class-scoped and byte-pinned.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path

OLD_OBF='TLUMACZENIA_OBF_10133.csv'
NEW_OBF='TLUMACZENIA_OBF_10153.csv'
OLD_API='TLUMACZENIA_JAR_1052.csv'
NEW_API='TLUMACZENIA_JAR_1053.csv'
OBF_SHA='f2ffdb534d870a49fce81dea47b4ebbac8fdccc218b79d5bed0f3752485cd484'
API_SHA='ddcec94935d80bcee715514352f79ffbea113ec299953c422746a94241ee179c'
GO_OBF_SHA='f53023d97c88615b353d4fbe78f7e7a41cd085c3e082fc2a00586592be8da9bc'
GO_API_SHA='8437d02711fcfec5ec093b73c5fd1e6cbc89e1a5853c50ec6bf852fa1c03c569'
OBF_PRIOR_PATCH_SHA='03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a'
OBF_CURRENT_PATCH_SHA='85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1'
RECOVERY='com.fs.starfarer.ui.newui.FleetMemberRecoveryDialog'
CHANGES={
 (RECOVERY,'ship'):'okr.',
 (RECOVERY,'ships'):'okr.',
 (RECOVERY,' ships'):' okr.',
}
FIELDS=['source_class','english_literal','polish_ascii_draft','status']
STATUS='VERIFIED_RECOVERY_COUNT_UI_1053_ORIGINAL_JVM'

def sha(b):return hashlib.sha256(b).hexdigest()
def once(t,a,b):
 if t.count(a)!=1:raise ValueError(('Nonunique source anchor',a,t.count(a)))
 return t.replace(a,b)
def read_csv(path):
 with Path(path).open(encoding='utf-8',newline='') as f:
  r=csv.DictReader(f)
  if r.fieldnames!=FIELDS:raise ValueError('Unexpected translation columns')
  return list(r)
def serialize(rows):
 f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\r\n');w.writeheader();w.writerows(rows)
 return f.getvalue().encode('utf8')
def make_obf(rows):
 if len(rows)!=3534 or len({(r['source_class'],r['english_literal']) for r in rows})!=len(rows):
  raise ValueError('Incorrect source OBF mapping')
 if set(CHANGES) & {(r['source_class'],r['english_literal']) for r in rows}:
  raise ValueError('Already mapped, refuse duplicate source literal')
 return rows + [dict(source_class=cl,english_literal=en,polish_ascii_draft=pl,status=STATUS)
                  for (cl,en),pl in CHANGES.items()]

# These precisely pinned replacements are used by both install and independent verifier.
OBF_MAIN_EDITS=(
 ('TLUMACZENIA_OBF_10130.csv TLUMACZENIA_OBF_10133.csv',
  'TLUMACZENIA_OBF_10130.csv TLUMACZENIA_OBF_10133.csv TLUMACZENIA_OBF_10153.csv'),
 ('const currentPatchState = "patched 10133"','const currentPatchState = "patched 10153"'),
 ('var knownPreviousOBFHashes = map[string]string{',
  'var knownPreviousOBFHashes = map[string]string{\n\t"'+OBF_PRIOR_PATCH_SHA+'": "10133",'),
 ('loadTranslations("TLUMACZENIA_OBF_10133.csv")','loadTranslations("TLUMACZENIA_OBF_10153.csv")'),
 ('state == currentPatchState || state == "patched 10130"',
  'state == currentPatchState || state == "patched 10133" || state == "patched 10130"'),
 ('Starsector 0.98a-RC8 | OBF 1.0.33 | stan:',
  'Starsector 0.98a-RC8 | OBF 1.0.53 | stan:'),
 ('0.9.99-1.0.33; odmowa modyfikacji','0.9.99-1.0.53; odmowa modyfikacji')
)
OBF_TEST_EDITS=(
 ('alreadyThisRelease("patched 10133")','alreadyThisRelease("patched 10153")'),
 ('[]string{"original", "patched 10121",','[]string{"original", "patched 10133", "patched 10121",'),
)
API_MAIN_EDITS=(
 ('const version = "1052"','const version = "1053"'),
 ('const exeVersion = "1.0.52"','const exeVersion = "1.0.53"'),
 ('"1049", "1050", "1051", version}', '"1049", "1050", "1051", "1052", version}'),
 ('const expectedOBFPatched10133 = "'+OBF_PRIOR_PATCH_SHA+'"',
  'const expectedOBFPatched10133 = "'+OBF_PRIOR_PATCH_SHA+'"\nconst expectedOBFPatched10153 = "'+OBF_CURRENT_PATCH_SHA+'"'),
 ('hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10133',
  'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10153 && hash(obf) != expectedOBFPatched10133'),
 ('PL ASCII patch up to 1.0.52','PL ASCII patch up to 1.0.53'),
)

def transform(s,pairs):
 for old,new in pairs:s=once(s,old,new)
 return s

def apply(root):
 root=Path(root)
 obf=root/'buildtools/NARZEDZIA_OBF'
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 tab=api/'translations'
 if any(p.exists() for p in (obf/NEW_OBF,tab/NEW_API)):
  raise FileExistsError('Overlay 1.0.53 already applied')
 if sha((obf/OLD_OBF).read_bytes())!=OBF_SHA or sha((tab/OLD_API).read_bytes())!=API_SHA:
  raise ValueError('Wrong source translation map revision')
 if sha((obf/'main.go').read_bytes())!=GO_OBF_SHA or sha((api/'main.go').read_bytes())!=GO_API_SHA:
  raise ValueError('Wrong patcher source baseline')
 obf_rows=read_csv(obf/OLD_OBF)
 if serialize(obf_rows)!=(obf/OLD_OBF).read_bytes():raise ValueError('Source OBF mapping not byte-exact CRLF roundtrip')
 out=serialize(make_obf(obf_rows))
 (obf/NEW_OBF).write_bytes(out)
 (tab/NEW_API).write_bytes((tab/OLD_API).read_bytes())
 for p,edits in [(obf/'main.go',OBF_MAIN_EDITS),(obf/'main_test.go',OBF_TEST_EDITS),
                 (api/'main.go',API_MAIN_EDITS)]:
  p.write_text(transform(p.read_text('utf8'),edits),encoding='utf8')
 installer=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
 installer.write_text(once(installer.read_text('utf8'),'const edition = "1.0.52"',
                           'const edition = "1.0.53"'),encoding='utf8')
 meta=root/'mod/mod_info.json';info=json.loads(meta.read_text('utf8'))
 if info['version']!='1.0.52' or info['gameVersion']!='0.98a-RC8':raise ValueError('Incorrect mod version')
 info['version']='1.0.53';info['description']=once(info['description'],'1.0.52','1.0.53')
 meta.write_text(json.dumps(info,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
 manual=root/'mod/CZYTAJ.txt'
 manual.write_text(once(manual.read_text('utf8'),'STARSECTOR PL ASCII 1.0.52','STARSECTOR PL ASCII 1.0.53')+
    '\nW oknie odzyskiwania okretow przetlumaczono trzy brakujace fragmenty ship/ships na skrot okr. Zmiana dotyczy patchera OBF, nie kodu mechaniki.\n',encoding='utf8')
 return {'version':'1.0.53','new_obf_rows':3,'obf_total_rows':3537,'obf_map_sha256':sha(out),
  'api_total_rows':5283,'api_map_unchanged_sha256':sha((tab/NEW_API).read_bytes()),
  'obf_original_patched_sha256':OBF_PRIOR_PATCH_SHA,
  'obf_target_patched_sha256':OBF_CURRENT_PATCH_SHA,
  'changed_original_obf_classes_expected':1,'api_literal_count_unchanged':5281,
  'java_executable_code_changed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 print(json.dumps(apply(p.parse_args().worktree),indent=2))
