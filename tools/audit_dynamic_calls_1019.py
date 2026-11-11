#!/usr/bin/env python3
"""Read-only Starsector UI dynamic text context audit.  Only works on user's originals."""
from __future__ import annotations
import argparse, collections, concurrent.futures, csv, hashlib, json, re, subprocess, zipfile
from pathlib import Path
SHA={'OBF':'5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8','API':'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a'}
STORY=re.compile(r'// Field com/fs/starfarer/api/util/Misc\.STORY:Ljava/lang/String;')
PRONOUN=re.compile(r'// (?:Method|InterfaceMethod) (?:\S+\.)?(get(?:ManOrWoman|HeOrShe|HimOrHer|HimOrHerself|HisOrHer)):')
STR=re.compile(r'// String (.*)$')
METHOD=re.compile(r'^  (?:(?:public|private|protected|static|final|synchronized|abstract|native|strictfp)\s+)+[^\n]*\([^\n]*\);$')

def strings_after(lines,start):
  found=[]
  for n in range(max(0,start-35),min(len(lines),start+36)):
    m=STR.search(lines[n])
    if m:found.append((n-start,m.group(1)))
  return [t for _,t in found if _<0][-5:], [t for _,t in found if _>0][:5]

def inspect(jar, name):
  res=subprocess.run(['javap','-classpath',str(jar),'-c','-p',name],check=True,capture_output=True,text=True)
  lines=res.stdout.splitlines();method='';out=[]
  for i,line in enumerate(lines):
    if METHOD.match(line):method=line.strip()
    ty='story' if STORY.search(line) else ('pronoun' if PRONOUN.search(line) else None)
    if not ty:continue
    before,after=strings_after(lines,i)
    target=PRONOUN.search(line).group(1) if ty=='pronoun' else 'Misc.STORY'
    offset=re.search(r'^\s*(\d+):',line)
    out.append({'class':name,'method':method,'offset':int(offset.group(1)) if offset else None,'kind':ty,'reference':target,'previous_literals':before,'next_literals':after})
  return out

def main():
  a=argparse.ArgumentParser();a.add_argument('--obf',type=Path,required=True);a.add_argument('--api',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
  for kind in SHA:
    if hashlib.sha256(getattr(args,kind.lower()).read_bytes()).hexdigest()!=SHA[kind]:raise ValueError('invalid '+kind+' JAR checksum')
  tasks=[]
  for kind in SHA:
    jar=getattr(args,kind.lower())
    with zipfile.ZipFile(jar) as z:
      for item in z.infolist():
        if not item.filename.endswith('.class'):continue
        data=z.read(item)
        if b'STORY' in data or b'getHisOrHer' in data or b'getHimOrHer' in data or b'getManOrWoman' in data or b'getHimOrHerself' in data:
          tasks.append((kind,jar,item.filename[:-6].replace('/','.')))
  result=[]
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    futs={ex.submit(inspect,jar,name):kind for kind,jar,name in tasks}
    for f in concurrent.futures.as_completed(futs):
      kind=futs[f];result.extend([dict(jar=kind,**r) for r in f.result()])
  result.sort(key=lambda x:(x['jar'],x['class'],x['method'],x['offset'] or 0))
  stats={k:len([r for r in result if r['kind']==k]) for k in ('story','pronoun')}
  group=dict(collections.Counter(x['jar'] for x in result if x['kind']=='story'))
  counts=collections.Counter(x['reference'] for x in result)
  report={'verified_orig_sha':SHA,'classes_disassembled':len(tasks),'stats':stats,'story_by_jar':group,'reference_counts':dict(counts),'references':result}
  args.out.write_text(json.dumps(report,ensure_ascii=True,indent=2)+'\n')
  print(json.dumps({'classes_disassembled':len(tasks),'stats':stats,'story_by_jar':group,'reference_counts':dict(counts)},indent=2))

if __name__=='__main__':main()