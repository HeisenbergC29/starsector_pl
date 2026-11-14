#!/usr/bin/env python3
"""Append exactly 87 new API reviews; 17 of 104 candidates were already counted."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apply_1054 import readmap
from apply_1065 import CLASS,OLD,NEW,REPAIRS,DRAFT,sha,fp,build
PREVIOUS=530;TOTAL=3658
# The 1.0.64 historical ledger already contains 17 MarketCMD entries (some
# still have DRAFT in the versioned source map). Their historic review must not
# be counted again; two receive an updated translation in 1.0.65.
PREVIOUSLY_REVIEWED={
 'The colony has no orbital station or nearby fleets to defend it.',
 'There are no nearby fleets to defend the colony.',
 'The presence of enemy fleets that are willing to offer battle makes a raid impossible.',
 'Your forces will be able to organize another raid within a day or so.',
 'Are you sure you want to engage in open hostilities?',
 'The attackers are in disarray and not currently attempting to engage the station.',
 "You're unable to join this battle.",
 'The defenders are refusing to give battle to defend the colony.',
 'Marines on board',
 'Fleet capability for ground support',
 'will only result in a minor penalty to your standing.',
 'You do not have the forces to carry out an effective raid.',
 'The ground defenses are too strong for your forces to be able to cause long-term disruption.',
 'A bombardment requires %s fuel. You have %s fuel.',
 'A tactical bombardment will destabilize the colony, and will also disrupt the following military targets for approximately %s days:',
 'The bombardment requires %s fuel. You have %s fuel.',
 ' operations for at least %s days.',
}
assert len(PREVIOUSLY_REVIEWED)==17

def inventory(root:Path)->dict:
 root=Path(root);trans=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations'
 old=readmap(trans/OLD);now=readmap(trans/NEW)
 approved,stats=build(old)
 if now!=approved:raise ValueError('Review source and final map differ')
 former={(x['source_class'],x['english_literal']):x for x in old}
 picked=[]
 for r in now:
  if r['source_class']!=CLASS:continue
  p=former[(CLASS,r['english_literal'])]
  if p['status'] not in DRAFT or r['english_literal'] in PREVIOUSLY_REVIEWED:continue
  picked.append({'source_class':CLASS,'english_literal':r['english_literal'],
   'english_key_sha256':sha(r['english_literal'].encode()),
   'old_status':p['status'],'old_draft':p['polish_ascii_draft'],
   'new_draft':r['polish_ascii_draft'],'old_row_sha256':fp(p),'row_sha256':fp(r),
   'evidence':'original_JVM_MarketCMD_1065',
   'review_status':'reviewed_original_JVM_offline_game_tests_after_1_1'})
 if len(picked)!=87 or len({x['row_sha256'] for x in picked})!=87:
  raise ValueError('Expected 87 newly reviewed candidates, excluding 17 prior reviewed')
 historical_prior=[{'english_literal':key,'old_row_sha256':fp(former[(CLASS,key)])}
   for key in sorted(PREVIOUSLY_REVIEWED)]
 return {'schema_version':1,'release':'1.0.65','game_version':'0.98a-RC8',
  'source_class':CLASS,'previous_map_sha256':sha((trans/OLD).read_bytes()),
  'new_map_sha256':sha((trans/NEW).read_bytes()),
  'previous_historical_reviews':PREVIOUS,'revisited_previously_reviewed_historical_rows':17,
  'new_historical_reviews':87,'historical_reviewed_total':PREVIOUS+87,
  'historical_remaining':TOTAL-PREVIOUS-87,
  'corrections':[{'english_literal':k,'polish_ascii_draft':v} for k,v in REPAIRS.items()],
  'corrected_existing_previously_verified_texts':1,
  'historical_previously_reviewed_english_keys_sha256':sorted(sha(x.encode()) for x in PREVIOUSLY_REVIEWED),
  'previously_reviewed_historical_rows':historical_prior,
  'reviewed_historical_rows':picked,'gameplay_test_policy':'after_1_1_release'}

def cumulative(prev:dict,r:dict)->dict:
 items=prev.get('reviewed',[])
 if prev.get('installed_version')!='1.0.64' or len(items)!=PREVIOUS:
  raise ValueError('Wrong historic ledger 1.0.64')
 previous={(x['source_class'],x['row_sha256']) for x in items}
 if len(previous)!=PREVIOUS:
  raise ValueError('Historical reviewed fingerprints contain duplicates')
 additions=[{k:item[k] for k in ('source_class','row_sha256','english_key_sha256','evidence','review_status')}
            for item in r['reviewed_historical_rows']]
 if len(additions)!=87 or any((x['source_class'],x['row_sha256']) in previous for x in additions):
  raise ValueError('Duplicate selected API row fingerprint')
 historical=[x for x in items if x['source_class']==CLASS]
 if len(historical)!=17:raise ValueError(('Expected 17 previously reviewed MarketCMD texts',len(historical)))
 prior_keys={sha(k.encode()) for k in PREVIOUSLY_REVIEWED}
 # Two ancient historical records lacked english_key_sha256. Verify those via
 # their original-row fingerprints, not just status flag in the current map.
 prior_reviewed_fps={x['old_row_sha256'] for x in r['previously_reviewed_historical_rows']}
 for old_item in historical:
  if old_item.get('english_key_sha256'):
   if old_item['english_key_sha256'] not in prior_keys:
    raise ValueError('Historical MarketCMD English key does not match guarded prior entries')
  elif old_item['row_sha256'] not in prior_reviewed_fps:
   raise ValueError('Cannot identify the old MarketCMD historical row without English SHA')
 known_keys={(x['source_class'],x.get('english_key_sha256')) for x in items if x.get('english_key_sha256')}
 if any((x['source_class'],x['english_key_sha256']) in known_keys for x in additions):
  raise ValueError('New MarketCMD English literal overlaps prior historical review')
 return {'schema_version':1,'installed_version':'1.0.65',
  'previous_ledger':'docs/API_SEMANTIC_REVIEW_1064.json',
  'review_protocol':'530 historical review fingerprints preserved; 104 MarketCMD DRAFT rows audited, but 17 already covered by past history and only 87 newly counted. 17 grammar repairs include two historical-reviewed original rows and a previously verified short UI label. Gameplay tests only after 1.1.',
  'new_historical_reviews':87,'reviewed':items+additions}

def check(root:Path,record:Path,previous:Path|None=None,ledger:Path|None=None)->dict:
 expected=inventory(root)
 if json.loads(Path(record).read_text('utf8'))!=expected:
  raise ValueError('MarketCMD source review registry altered')
 if previous and ledger:
  before=json.loads(Path(previous).read_text('utf8'))
  if json.loads(Path(ledger).read_text('utf8'))!=cumulative(before,expected):
   raise ValueError('Append-only MarketCMD historical API ledger mismatch')
 return {'release':'1.0.65','new_historical_reviews':87,'history_total':617,
  'history_remaining':3041,'prior_530_preserved':bool(previous and ledger)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 p.add_argument('--record',type=Path,required=True);p.add_argument('--previous',type=Path)
 p.add_argument('--ledger',type=Path);p.add_argument('--generate',action='store_true')
 a=p.parse_args()
 if a.generate:
  obj=inventory(a.worktree);a.record.write_text(json.dumps(obj,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
  if a.previous and a.ledger:
   a.ledger.write_text(json.dumps(cumulative(json.loads(a.previous.read_text('utf8')),obj),ensure_ascii=True,indent=2)+'\n',encoding='utf8')
 print(json.dumps(check(a.worktree,a.record,a.previous,a.ledger),indent=2))
