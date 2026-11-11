#!/usr/bin/env python3
"""Read-only fail-closed audit of currently installed DRAFT/OPTIONAL API map rows.

Boundary checks are diagnostic, not a semantic review. Keep comma-vs-conjunction
cases visible as intentionally different in Polish, not automatically errors.
"""
import argparse,csv,collections,json,re
from pathlib import Path
STATUS={'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
TOKEN=re.compile(r'\$[A-Za-z_]\w*|\{(?:\d+|[A-Za-z_]\w*)\}|(?<![A-Za-z0-9])%(?:\d+\$)?[-+#0,(]*\d*(?:\.\d+)?[a-zA-Z%]')

def audit(path):
 with path.open(encoding='utf8',newline='') as f:r=list(csv.DictReader(f))
 assert len(r)==len({(x['source_class'],x['english_literal']) for x in r})
 old=[x for x in r if x['status'] in STATUS]
 issues=collections.defaultdict(list)
 for x in old:
  a=x['english_literal']; b=x['polish_ascii_draft']
  if not a or not b:issues['empty_value'].append(x)
  if a[:1]==' ' and b[:1]!=' ':issues['leading_space_removed'].append(x)
  if a[-1:]==' ' and b[-1:]!=' ':issues['trailing_space_removed'].append(x)
  if b[:1]==' ' and a[:1]!=' ':issues['leading_space_added'].append(x)
  if b[-1:]==' ' and a[-1:]!=' ':issues['trailing_space_added'].append(x)
  if a.count('\n')!=b.count('\n'):issues['newline_count_changed'].append(x)
  if sorted(TOKEN.findall(a))!=sorted(TOKEN.findall(b)):issues['format_tokens_changed'].append(x)
  if not b.isascii():issues['non_ascii_target'].append(x)
  if re.search(r'\b(?:the|will|when|your|with|ships|enemy|cannot|their|not)\b',b,re.I):issues['english_stop_words'].append(x)
 return {'rows_total':len(r),'examined_installed_draft_optional':len(old),
  'statuses':dict(collections.Counter(x['status'] for x in old)),
  'flags':{k:[{'class':x['source_class'],'english':x['english_literal'],'polish':x['polish_ascii_draft']} for x in v] for k,v in sorted(issues.items())},
  'limitations':'Automated boundary/token audit only. Not an exhaustive semantic or UI runtime review. A comma before English and may intentionally be omitted in Polish.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('api_csv',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 z=audit(a.api_csv);a.out.write_text(json.dumps(z,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'rows_checked':z['examined_installed_draft_optional'],'flags':{k:len(v) for k,v in z['flags'].items()}},indent=2))
if __name__=='__main__':main()