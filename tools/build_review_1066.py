#!/usr/bin/env python3
"""Cross-check 161 draft rows and count only historically new fingerprints.

46 BaseIndustry DRAFT and 1 TutorialMissionIntel DRAFT rows were already counted,
although their map status was not updated. Never add them again.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1054 import readmap
from apply_1066 import SIM,IND,TUT,OLD,NEW,DRAFT,ADDITIONS,CORRECTIONS,sha,fp,build
BASE_REVIEW_KEYS_12={
 'f23706f9b3db','725d20ad7e7a','43cf43303acd','84de816f5f12','60b3186b3453',
 'c7d3d7dba412','66fca11ab8b5','8a443c2e31c7','ce64552cc93e','3eb8bbb4203a',
 '859de6c5aa6f','6846b36354c2','4f06d4606b01','e58b3b425dd0','793dee860a8e',
 '06f92c1b6372','c693d9b731f5','76adb3e64d7a','4d1cfe5234a0','b85c16f4d3ee',
 '982b5e63b069','cd9a8922a25b','ee48e0882730','5a57ec1b2735','99b8d9a10257',
 '265590c28c82','e5fc6430d299','356a4d0dda28','a82b42610558','6eada24ff447',
 '19cdd964c1c4','924f5baa6543','2f24c917fe2c','8eea090e9cfd','c37885ce9f98',
 '95b351f53895','7e4195581db4','f82b783b9654','2d2baf5cf852','47e9aa496b9e',
 '3915dbf8f624','7324f89d7d14','2e3d6a0d46c9','da918db586f9','a67869eb9f5a',
}
BASE_REVIEW_UNKEYED_FP='2bbbe22d0bf1056c4a70d3f7d04072cadbd9893855d832267bf034d9cc66dd82'
TUTORIAL_REVIEW_ENGLISH_SHA='be538709197f8b2064568ca286f2dc0b4ad65557917136f26790e74c6f3602ff'
assert len(BASE_REVIEW_KEYS_12)==45
PREVIOUS=617;NEW_REVIEWED=114;HISTORIC_TOTAL=3658

def inventory(root:Path)->dict:
 root=Path(root);tr=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 before=readmap(tr/OLD);after=readmap(tr/NEW);expected,stats=build(before)
 if after!=expected:raise ValueError('v1.0.66 reviewed content changed')
 old={(r['source_class'],r['english_literal']):r for r in before}
 prior=[];new=[]
 for r in stats['reviewed_status_rows']:
  oldrow=old[(r['source_class'],r['english_literal'])]
  former=(r['source_class']==IND and (
   r['english_key_sha256'][:12] in BASE_REVIEW_KEYS_12 or fp(oldrow)==BASE_REVIEW_UNKEYED_FP)) or (
   r['source_class']==TUT and r['english_key_sha256']==TUTORIAL_REVIEW_ENGLISH_SHA)
  item={**r,'previously_reviewed_in_historic_ledger':former}
  (prior if former else new).append(item)
 if len(prior)!=47 or len(new)!=NEW_REVIEWED or len(stats['reviewed_status_rows'])!=161:
  raise ValueError(('Wrong draft-history overlap',len(prior),len(new)))
 if len({x['english_key_sha256'] for x in prior})!=47 or sum(x['source_class']==IND for x in prior)!=46 or sum(x['source_class']==TUT for x in prior)!=1:
  raise ValueError('Prior history 46 BaseIndustry items not uniquely identified')
 if (sum(x['source_class']==SIM for x in new),sum(x['source_class']==IND for x in new),
     sum(x['source_class']==TUT for x in new))!=(58,10,46):
  raise ValueError('Wrong per-class new historical review counts')
 return {'schema_version':1,'release':'1.0.66','game_version':'0.98a-RC8',
  'previous_map_sha256':sha((tr/OLD).read_bytes()),'new_map_sha256':sha((tr/NEW).read_bytes()),
  'previous_historical_reviews':PREVIOUS,'draft_status_rows_reviewed':161,
  'historical_rows_previously_counted':47,'new_historical_reviews':NEW_REVIEWED,
  'cumulative_historical_reviews':PREVIOUS+NEW_REVIEWED,
  'historical_unreviewed':HISTORIC_TOTAL-PREVIOUS-NEW_REVIEWED,
  'by_source_class':{SIM:{'drafts':58,'new':58,'already':0},
                     IND:{'drafts':56,'new':10,'already':46},
                     TUT:{'drafts':47,'new':46,'already':1}},
  'corrected_fragments':stats['repaired'],
  'new_mapped_literals':[{'class':cl,'english_literal':en,'polish_ascii_draft':value}
    for (cl,en),value in ADDITIONS.items()],
  'rechecked_earlier_history':prior,'reviewed_historical_rows':new,
  'native_game_test_policy':'after_1_1_release'}

def cumulative(prior:dict,record:dict)->dict:
 if prior.get('installed_version')!='1.0.65' or len(prior.get('reviewed',[]))!=PREVIOUS:
  raise ValueError('Wrong immutable historical API ledger baseline')
 old=prior['reviewed'];ident={(x['source_class'],x['row_sha256']) for x in old}
 if len(ident)!=PREVIOUS:raise ValueError('Duplicate earlier history fingerprints')
 industry=[x for x in old if x['source_class']==IND];sim=[x for x in old if x['source_class']==SIM]
 tutorial=[x for x in old if x['source_class']==TUT]
 if (len(industry),len(sim),len(tutorial))!=(46,0,1):
  raise ValueError('Unexpected prior history for selected classes')
 prior_en={(x['source_class'],x.get('english_key_sha256')) for x in old if x.get('english_key_sha256')}
 old_fp={x['row_sha256'] for x in industry+tutorial}
 for row in record['rechecked_earlier_history']:
  if (row['source_class'],row['english_key_sha256']) not in prior_en and row['old_row_sha256'] not in old_fp:
   raise ValueError(('Unanchored previously reviewed row',row['english_literal']))
 additions=[{k:row[k] for k in ('source_class','row_sha256','english_key_sha256','evidence','review_status')}
   for row in record['reviewed_historical_rows']]
 if len(additions)!=NEW_REVIEWED or any((x['source_class'],x['row_sha256']) in ident
    or (x['source_class'],x['english_key_sha256']) in prior_en for x in additions):
  raise ValueError('Duplicate or falsely new historical review')
 return {'schema_version':1,'installed_version':'1.0.66',
  'previous_ledger':'docs/API_SEMANTIC_REVIEW_1065.json',
  'review_protocol':'All 617 historical API rows preserved exactly. 161 DRAFT-status texts in SimulatorPluginImpl, BaseIndustry, TutorialMissionIntel reviewed in original JVM; 46 BaseIndustry and 1 TutorialMissionIntel already historical, so only 114 new. Also 13 new original-JVM-visible literals and 9 corrections, not additionally counted. Native game tests after 1.1.',
  'new_historical_reviews':NEW_REVIEWED,'reviewed':old+additions}

def check(root:Path,record:Path,prior:Path|None=None,ledger:Path|None=None)->dict:
 expected=inventory(root)
 if json.loads(Path(record).read_text('utf8'))!=expected:raise ValueError('v1066 original-JVM review record altered')
 if prior and ledger:
  actual=json.loads(Path(ledger).read_text('utf8'))
  computed=cumulative(json.loads(Path(prior).read_text('utf8')),expected)
  if actual!=computed:raise ValueError('Cumulative history is not append-only or counts prior reviews twice')
 return {'release':'1.0.66','reviewed_status_rows':161,'already_previously_reviewed':47,
  'new_historical_reviews':114,'cumulative':731,'remaining':2927,
  'append_only_ledger_checked':bool(prior and ledger)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--record',type=Path,required=True);p.add_argument('--previous',type=Path)
 p.add_argument('--ledger',type=Path);p.add_argument('--generate',action='store_true');a=p.parse_args()
 if a.generate:
  data=inventory(a.worktree);a.record.write_text(json.dumps(data,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
  if a.previous and a.ledger:
   a.ledger.write_text(json.dumps(cumulative(json.loads(a.previous.read_text('utf8')),data),ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps(check(a.worktree,a.record,a.previous,a.ledger),indent=2))
