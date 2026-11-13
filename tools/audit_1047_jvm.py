#!/usr/bin/env python3
"""Private read-only JVM proof for 1.0.47: 14 economic texts, 26 battle choices,
and the non-fixable shared 'her' constant. No proprietary strings enter reports."""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from apply_1047 import CHANGES
from audit_1046_jvm import cp_literals, ORIGINAL_API_SHA

FLEET='com.fs.starfarer.api.impl.campaign.FleetInteractionDialogPluginImpl'
BASEBAR='com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson'
BATTLE_OPTIONS=(
 'Disabled ships from your fleet are available for recovery',
 'Consider ship recovery',
 'Disabled ships from your fleet are available for recovery.',
 'Cut the comm link',
 'Order your second-in-command to handle it',
 'Transfer command for this engagement',
 'Take command of the action',
 'Crash-mothball some of your ships to prevent malfunctions',
 'Continue into battle',
 'Join the battle',
 'Accept the comm request',
 'Open a comm link',
 'Join the pursuit',
 'Perform a salvage operation, then leave',
 'Maneuver to force a pitched battle',
 'Outmaneuver the opposing fleet, forcing them to fight you head on.',
 'Harry their retreat',
 'Join the disengage attempt',
 'Join the engagement',
 'Disengage by executing a series of special maneuvers',
 'Allows your fleet to disengage without being pursued.',
 'Perform limited emergency repairs',
 'Brings your flagship and a few officer-controlled ships back up to reasonable combat readiness and repairs some hull damage.',
 'Attempt to disengage',
 'Let them go',
 'Pursue them',
)
assert len(BATTLE_OPTIONS)==len(set(BATTLE_OPTIONS))==26

def javap(jar,cl):
    c=subprocess.run(['javap','-p','-c','-classpath',str(jar),cl],capture_output=True,text=True,timeout=35)
    if c.returncode:raise RuntimeError(('javap failed',cl,c.stderr[-900:]))
    return c.stdout

def method(text,name):
    # Match the precise no-argument method declaration, bounded by next declaration.
    m=re.search(r'(?m)^  protected java\.lang\.String '+name+r'\(\);\n(.*?)(?=^  (?:protected|private|public) |\Z)',text,re.S|re.M)
    if not m:raise ValueError('Getter missing '+name)
    return m.group(1)

def verify_shared_her(jar):
    s=javap(jar,BASEBAR)
    obj=method(s,'getHimOrHer');poss=method(s,'getHisOrHer')
    a=re.findall(r'\bldc\s+#(\d+)\s+// String her$',obj,re.M)
    b=re.findall(r'\bldc\s+#(\d+)\s+// String her$',poss,re.M)
    if a!=['143'] or b!=['143'] or 'String him' not in obj or 'String his' not in poss:
        raise ValueError(('Shared female her collision changed',a,b))
    return {'class':BASEBAR,'object_getter':'getHimOrHer','possessive_getter':'getHisOrHer',
            'shared_original_constant_pool_index':143,'same_ldc_constant':True,
            'plain_her_replacement_safe_for_both_grammatical_roles':False,
            'getter_callsite_fix_status':'open_not_modified'}

def verify_options(jar):
    txt=javap(jar,FLEET).splitlines()
    out=[]
    for english in BATTLE_OPTIONS:
        hits=[i for i,line in enumerate(txt) if '// String '+english in line and line.split('// String ',1)[1]==english]
        if not hits:raise ValueError(('Missing UI option in javap',english))
        # In the unchanged game bytecode, each audited literal is fed to
        # OptionPanelAPI.addOption (including select buttons and tooltips).
        if any(not any('OptionPanelAPI.addOption:' in line for line in txt[i+1:i+15]) for i in hits):
            raise ValueError(('Literal not connected to option panel',english))
        out.append({'english_key_sha256':hashlib.sha256(english.encode()).hexdigest(),
                    'original_jvm_add_option_calls':len(hits),'option_panel_callsite_verified':True})
    return out

def check(original_api):
    jar=Path(original_api)
    digest=hashlib.sha256(jar.read_bytes()).hexdigest()
    if digest!=ORIGINAL_API_SHA:raise ValueError(('Incorrect original game jar',digest))
    hits=[];cache={}
    all_keys=list(CHANGES)+[(FLEET,e) for e in BATTLE_OPTIONS]
    with zipfile.ZipFile(jar) as z:
        if z.testzip() is not None:raise ValueError('Original JAR damaged')
        for cls,en in all_keys:
            if cls not in cache:cache[cls]=cp_literals(z.read(cls.replace('.','/')+'.class'))
            if cache[cls].count(en.encode('utf8'))!=1:raise ValueError(('Missing/ambiguous original JVM String',cls,en))
            hits.append({'class':cls,'english_key_sha256':hashlib.sha256(en.encode('utf8')).hexdigest()})
    choices=verify_options(jar)
    shared=verify_shared_her(jar)
    return {'schema_version':1,'release':'1.0.47','original_api_sha256':digest,
            'corrected_numeric_english_literals_found':14,'original_battle_ui_option_labels_found':len(choices),
            'checked_original_jvm_string_literals':len(hits),
            'classes_with_original_constants':len(cache),'option_panel_callsites_checked':sum(x['original_jvm_add_option_calls'] for x in choices),
            'shared_her':shared,'checks':hits,'battle_option_evidence':choices,
            'source':'private original JVM 0.98a-RC8, no in-game Windows run'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--original-api',type=Path,required=True)
    p.add_argument('--out',type=Path);a=p.parse_args();v=check(a.original_api)
    if a.out:a.out.write_text(json.dumps(v,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in v.items() if k not in ('checks','battle_option_evidence')},indent=2))
