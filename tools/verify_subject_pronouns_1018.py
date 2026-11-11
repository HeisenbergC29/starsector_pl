#!/usr/bin/env python3
"""Check minimal, safe 1018 map delta without access to proprietary original JARs."""
import csv,sys,json,re
from pathlib import Path
root=Path(sys.argv[1])
o=root/'buildtools/NARZEDZIA_OBF'
a=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
expected={
 'OBF':('TLUMACZENIA_OBF_10117.csv','TLUMACZENIA_OBF_10118.csv',
        {'com.fs.starfarer.rpg.Person'},3140),
 'API':('TLUMACZENIA_JAR_1017.csv','TLUMACZENIA_JAR_1018.csv',
        {'com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson',
         'com.fs.starfarer.api.impl.campaign.intel.bar.events.historian.HistorianData'},5096),
}
report={}
for label,(prev,cur,classes,old_count) in expected.items():
 d=o if label=='OBF' else a/'translations'
 def read(p):
  with (d/p).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
 before=read(prev);after=read(cur)
 assert len(before)==old_count and after[:old_count]==before,(label,'historical map modified')
 appended=after[old_count:]
 exact={(cl,eng,pl,'VERIFIED_SUBJECT_PRONOUN_1018') for cl in classes for eng,pl in [('he','on'),('she','ona')]}
 actual={(r['source_class'],r['english_literal'],r['polish_ascii_draft'],r['status']) for r in appended}
 assert actual==exact and len(appended)==len(exact),(label,'unexpected map delta',appended)
 assert not any(r['english_literal'] in {'him','her','his','himself','herself','story'} for r in appended)
 report[label]={'previous_rows':len(before),'current_rows':len(after),'new_rows':len(appended),'classes':sorted(classes)}
assert 'const version = "1018"' in (a/'main.go').read_text()
assert 'const currentPatchState = "patched 10118"' in (o/'main.go').read_text()
assert 'c95b45715e4d7c1b982d154acdc6776a3cf60756e83eefb00ea526a96c5a6c92' in (a/'main.go').read_text()
assert json.loads((root/'mod/mod_info.json').read_text())['version']=='1.0.18'
print(json.dumps(report,indent=2))