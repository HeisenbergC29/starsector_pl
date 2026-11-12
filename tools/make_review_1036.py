#!/usr/bin/env python3
"""Generate 20 manually selected and context-reviewed API map fingerprints.

The selection is an explicit authored editorial decision, NOT automatic approval
of all class strings. Rerun after apply_1036.py; unchanged previous reviews.
"""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
EVENT='com.fs.starfarer.api.impl.campaign.intel.bar.events.PlanetaryShieldBarEvent'
# Exact source literals selected following comparison of the original and Polish
# fragments and the surrounding optionSelected() / other display callsites.
# Avoid pieces requiring unresolved getHisOrHer()/getHimOrHer().
SELECT={
 ' did not live the experience in such ':'neutral statement about the pilot, independent of name gender',
 'stride as ':'comparative clause before gendered on/ona; both variants tested',
 ', and has taken to drinking themselves senseless ':'comma and continuing clause, with a space before semi-retirement',
 'I wouldn\'t wish my fate on you or anyone. Besides, I have no idea." A pause, then, ':'speaker-independent direct speech, no masculine conditional',
 '"Some folks, I don\'t think they react well ':'continuation toward the cryopod description',
 'to the emergency cryo-pods. Like a bit o\' their brain is still froze up and not coming back."':'continuation of the cryopod description; unchanged quote',
 'The old spacer tells you that ':'speaker/target framing for the corrected sentence',
 'The old space-hand opens up as one drink turns to two or three. ':'bar-event narrative after ordering drinks',
 '\n\nThen the officers found something new in a data-cache. ':'narrative break, two newlines and trailing space preserved',
 'There they found a planet all shining and red. "It weren\'t anything natural. It was all... shapes, angles, glowing like plasma. That\'s truth," ':'planet discovery with quoted speech, ellipsis preserved',
 'For a minute there, you were caught by the story, but you now see that following up on it would be a fool\'s errand.':'story denotes a tale here, NOT the Misc.STORY point currency',
 'The loot was good, and any brigand they couldn\'t fight, they could flee.':'past-tense salvage fleet description',
 'They fared two hyperspace storms before arriving at a distant star system.':'travel narrative, original two storms retained',
 'a salvage fleet trawling decivilized systems outside the Core Worlds. ':'salvage fleet, Core Worlds term, trailing delimiter',
 'Rumours flew among the crew, who were told nothing, as the fleet suddenly left a rich ':'crew rumors leading into target world description',
 'asteroid belt to make for the outer system jump-point. ':'asteroid belt and outer jump point, not a new system',
 'escape pod which was only "mostly" malfunctioning. "The miracle wasn\'t that I ':'partially faulty escape pod, first-person quotation retained',
 'never seen anything Domain-made glow like that across a whole planet\'s face. ':'Domain technology referenced without changing faction name',
 '"Where was this system with the red planet?"':'player option asking the location of the red planet',
 'You consider a trip to ':'option narrative introducing target destination',
}

def fp(row):
 return hashlib.sha256('\0'.join(row[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode('utf8')).hexdigest()

def generate(root,prior,output):
 old=json.loads(prior.read_text('utf8'))
 assert old['schema_version']==1 and old['installed_version']=='1.0.33' and len(old['reviewed'])==58
 mapping=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1036.csv'
 with mapping.open(encoding='utf8',newline='') as f:rows=list(csv.DictReader(f))
 if len(SELECT)!=20:raise AssertionError(len(SELECT))
 events={r['english_literal']:r for r in rows if r['source_class']==EVENT}
 assert set(SELECT)<=set(events)
 verified=[]
 for en,why in SELECT.items():
  row=events[en]
  assert row['status'] in {'DRAFT_ONLY_NOT_INSTALLED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME','OPTIONAL_PATCHER_NOT_GAME_TESTED'}
  assert row['polish_ascii_draft']!=en and row['polish_ascii_draft'].isascii()
  verified.append({'source_class':EVENT,'row_sha256':fp(row),
       'evidence':'planetary_shield_contextual_original_and_patched_jvm',
       'note':why,'english_key_sha256':hashlib.sha256(en.encode('utf8')).hexdigest()})
 oldseen={(x['source_class'],x['row_sha256']) for x in old['reviewed']}
 assert not any((x['source_class'],x['row_sha256']) in oldseen for x in verified)
 out={'schema_version':1,'installed_version':'1.0.36',
      'review_protocol':'58 prior immutable offline reviews plus 20 manually selected PlanetaryShieldBarEvent phrases, checked against original and patched constant pools and adjacent callsites. Does not constitute native Windows gameplay proof.',
      'reviewed':old['reviewed']+verified}
 assert len(out['reviewed'])==78
 output.write_text(json.dumps(out,ensure_ascii=True,indent=2)+'\n','utf8')
 print(json.dumps({'previous':58,'new_contextual_reviews':20,'total_offline_reviews':78,'historical_pending_offline':3658-78}))
 return out
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('worktree',type=Path);a.add_argument('--prior-ledger',required=True,type=Path);a.add_argument('--out',required=True,type=Path)
 x=a.parse_args();generate(x.worktree,x.prior_ledger,x.out)
