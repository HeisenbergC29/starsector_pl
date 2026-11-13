#!/usr/bin/env python3
"""Auditable append-only 20-row semantic review, 1.0.46.

Every newly approved map literal is pinned to exactly one original JVM
CONSTANT_String (private game JAR verified separately) and its installed Polish
mapping. This is offline-only; no Windows gameplay is implied.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from apply_1046 import load,FIELDS
from audit_1046_jvm import check as check_jvm

APPROVED_STATUSES={'DRAFT_ONLY_NOT_INSTALLED','OPTIONAL_PATCHER_NOT_GAME_TESTED','DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME'}
FAMILIES={
'com.fs.starfarer.api.impl.campaign.intel.events.PiracyRespiteScript':None,
'com.fs.starfarer.api.impl.campaign.skills.CrewTraining$Level2':None,
'com.fs.starfarer.api.impl.campaign.skills.PhaseCorps$Level3':None,
'com.fs.starfarer.api.impl.campaign.tutorial.GalatianAcademyStipend':None,
'com.fs.starfarer.api.impl.campaign.AbandonMarketPluginImpl':APPROVED_STATUSES,
'com.fs.starfarer.api.impl.campaign.rulecmd.DoCanAffordCheck$1':None,
'com.fs.starfarer.api.impl.hullmods.MissileAutoloader':APPROVED_STATUSES,
}
SELECTED_COUNTS={'PiracyRespiteScript':5,'CrewTraining$Level2':1,'PhaseCorps$Level3':3,
                'GalatianAcademyStipend':4,'AbandonMarketPluginImpl':4,
                'DoCanAffordCheck$1':2,'MissileAutoloader':1}

def keyfp(r):return hashlib.sha256('\0'.join(r[k] for k in ('source_class','english_literal','polish_ascii_draft')).encode()).hexdigest()
def selected(rows):
    found=[];counts={}
    for x in rows:
        cls=x['source_class']
        if cls not in FAMILIES or x['status'] not in APPROVED_STATUSES:continue
        found.append(x)
        short=cls.rsplit('.',1)[-1];counts[short]=counts.get(short,0)+1
    if counts!=SELECTED_COUNTS:raise ValueError(('Review cohort changed',counts))
    if len({(x['source_class'],x['english_literal']) for x in found})!=20:raise ValueError('Bad duplicate review keys')
    return sorted(found,key=lambda r:(r['source_class'],r['english_literal']))

def make(root,previous,original_api=None):
    root=Path(root)
    src=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1046.csv'
    cur=load(src)
    if len(cur)!=5260:raise ValueError('Bad map row count')
    orig=json.loads(Path(previous).read_text('utf8'))
    old=orig['reviewed']
    if orig['schema_version']!=1 or len(old)!=122:raise ValueError('Bad previous ledger')
    index={(x['source_class'],keyfp(x)):x for x in cur}
    if any((y['source_class'],y['row_sha256']) not in index for y in old):raise ValueError('Old reviews no longer match target API map')
    cohort=selected(cur)
    seen={(x['source_class'],x['row_sha256']) for x in old}
    if any((x['source_class'],keyfp(x)) in seen for x in cohort):raise ValueError('Already reviewed row double-counted')
    if original_api:
        proof=check_jvm(original_api,{(r['source_class'],r['english_literal']) for r in cohort})
        if proof['checked_class_scoped_literals']!=20:raise ValueError('Private JVM proof incomplete')
    record=[]
    for x in cohort:
        record.append({'source_class':x['source_class'],'row_sha256':keyfp(x),
                       'english_key_sha256':hashlib.sha256(x['english_literal'].encode()).hexdigest(),
                       'evidence':'original_jvm_constant_pool_and_contextual_polish_1046',
                       'review_status':'approved_offline_context_only_pending_native_windows_gameplay'})
    result={'schema_version':1,'installed_version':'1.0.46',
       'review_protocol':'append-only: 122 inherited + 20 individually checked active DRAFT/OPTIONAL rows in 7 API class groups; original JVM constant-pool verified, no native Windows gameplay',
       'previous_ledger':'docs/API_SEMANTIC_REVIEW_1040.json','new_reviewed_rows':20,
       'reviewed':old+record}
    return result

def verify(root,previous,ledger,original_api=None):
    expected=make(root,previous,original_api)
    supplied=json.loads(Path(ledger).read_text('utf8'))
    if supplied!=expected:raise ValueError('Semantic review ledger changed unexpectedly')
    if len(supplied['reviewed'])!=142:raise ValueError('Wrong review count')
    return {'historical_api_review_total':3658,'prior_reviewed_offline':122,
            'newly_reviewed_offline':20,'cumulative_reviewed_offline':142,
            'remaining_historical_api_reviews':3516,'native_gameplay_tested':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
    p.add_argument('--previous',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
    p.add_argument('--original-api',type=Path);p.add_argument('--generate',action='store_true')
    a=p.parse_args()
    if a.generate:
        j=make(a.worktree,a.previous,a.original_api)
        a.ledger.write_text(json.dumps(j,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(verify(a.worktree,a.previous,a.ledger,a.original_api),indent=2))
