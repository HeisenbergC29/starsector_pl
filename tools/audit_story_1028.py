#!/usr/bin/env python3
"""Precisely scope all Misc.STORY uses to prevent unsafe global translation.

Read-only, with original release SHA checks. The detailed JSON report is private
because nearby snippets may originate from proprietary copyrighted game data.
A successful audit does NOT certify the Polish grammar of assembled strings.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,subprocess,zipfile
from pathlib import Path
HASHES={'OBF':'5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8',
        'API':'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'}
STORY='// Field com/fs/starfarer/api/util/Misc.STORY:Ljava/lang/String;'
LDCS=re.compile(r'\bldc(?:_w)?\s+#\d+\s+// String (.*)$')
METHOD=re.compile(r'^  (?:public|private|protected|static|final|synchronized).*\);$')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--obf',type=Path,required=True);ap.add_argument('--api',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args();jars={'OBF':a.obf,'API':a.api}
 result={'game_version':'0.98a-RC8','original_sha256':HASHES,'refs':[],'classes_disassembled':0}
 for kind,jar in jars.items():
  assert hashlib.sha256(jar.read_bytes()).hexdigest()==HASHES[kind],kind
  with zipfile.ZipFile(jar) as z:
   names=[n[:-6].replace('/','.') for n in z.namelist() if n.endswith('.class') and b'Misc' in z.read(n) and b'STORY' in z.read(n)]
  for cl in names:
   p=subprocess.run(['javap','-classpath',str(jar),'-c','-p',cl],capture_output=True,text=True,check=True)
   lines=p.stdout.splitlines()
   if not any(STORY in line for line in lines):continue
   result['classes_disassembled']+=1
   meth=''
   for i,line in enumerate(lines):
    if METHOD.match(line):meth=line.strip()
    if STORY not in line:continue
    pre=[m.group(1) for j in range(max(0,i-40),i) if (m:=LDCS.search(lines[j]))]
    aft=[m.group(1) for j in range(i+1,min(len(lines),i+26)) if (m:=LDCS.search(lines[j]))]
    offset=re.search(r'^\s*(\d+):',line)
    result['refs'].append({'jar':kind,'class':cl,'method':meth,'offset':int(offset.group(1)) if offset else None,
                           'prior_last_literals':pre[-3:],'subsequent_first_literals':aft[:3],
                           'followed_by_point_suffix':bool(aft and re.search(r'^\s*points?\b',aft[0]))})
 total=len(result['refs']);byjar=collections.Counter(r['jar'] for r in result['refs']);bycl=collections.Counter((r['jar'],r['class']) for r in result['refs'])
 assert total==81,(total,byjar)
 assert byjar=={'OBF':65,'API':16},byjar
 assert len(bycl)==24,(len(bycl),bycl)
 result['stats']={'story_field_loads':total,'OBF':byjar['OBF'],'API':byjar['API'],'classes_using_field':len(bycl),
                  'direct_followup_point_suffix':sum(r['followed_by_point_suffix'] for r in result['refs']),
                  'class_references':[{'jar':k[0],'class':k[1],'loads':n} for k,n in sorted(bycl.items())]}
 # A global source-word replacement would change every site; the same field is
 # used in both singular and plural constructions even in one class.
 assert any(r['class'].endswith('SetStoryOption$1') for r in result['refs'])
 assert sum(r['class']=='com.fs.starfarer.campaign.CharacterStats' for r in result['refs'])==9
 with zipfile.ZipFile(a.api) as z:
  data=z.read('com/fs/starfarer/api/util/Misc.class')
 assert b'story' in data and b'STORY' in data
 result['decision']='DO_NOT_GLOBAL_REPLACE: shared across 81 loads and 24 classes with singular/plural and highlights; needs per-construction grammar audit'
 a.out.write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps(result['stats'],indent=2))
if __name__=='__main__':main()