#!/usr/bin/env python3
"""Reproducible local-only original JVM evidence for 19 historical reviews."""
import argparse,json,subprocess,sys,zipfile,re
from pathlib import Path
from apply_1054 import OLD,NEW,readmap,sha
from verify_review_1054 import make,fp
from private_jvm_1051 import parse_class,getstr

def run(root,previous,original):
 root=Path(root);n=readmap(root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'/NEW)
 selected={(x['source_class'],x['row_sha256']) for x in make(root,previous)['reviewed'][-19:]}
 rows=[x for x in n if (x['source_class'],fp(x)) in selected]
 if len(rows)!=19:raise ValueError('Wrong selected class subset')
 records=[]
 with zipfile.ZipFile(original) as z:
  for cl in sorted(set(x['source_class'] for x in rows)):
   b=z.read(cl.replace('.','/')+'.class');cp,_,_=parse_class(b)
   cv={i:getstr(b,cp,i) for i,c in enumerate(cp) if c and c[0]==8}
   dis=subprocess.check_output(['javap','-classpath',str(original),'-p','-c',cl],text=True,timeout=45)
   for row in (x for x in rows if x['source_class']==cl):
    ids=[i for i,s in cv.items() if s==row['english_literal']]
    if len(ids)!=1:raise ValueError(('Original constant not unique',cl,row['english_literal'],ids))
    idx=ids[0]
    uses=len(re.findall(r'^\s*\d+:\s+ldc(?:_w)?\s+#'+str(idx)+r'\s+// String',dis,re.M))
    if uses<1:raise ValueError(('Original literal not referenced by JVM',cl,idx))
    records.append({'source_class':cl,'class_original_sha256':sha(b),'english':row['english_literal'],
      'polish_ascii':row['polish_ascii_draft'],'jvm_constant_string_index':idx,'original_ldc_uses':uses,
      'source_status':row['status']})
 return {'reviewed_count':len(records),'source_original_api_sha256':sha(Path(original).read_bytes()),'data':records}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path);p.add_argument('--previous',type=Path,required=True);p.add_argument('--original',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
 d=run(a.worktree,a.previous,a.original);a.report.write_text(json.dumps(d,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print({'reviewed':d['reviewed_count'],'used_callsites':sum(x['original_ldc_uses'] for x in d['data'])})
