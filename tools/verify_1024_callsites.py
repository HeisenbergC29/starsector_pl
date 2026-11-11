#!/usr/bin/env python3
"""Read-only original-JAR proof: 44 selected literals go into UI construction.

Requires javap and private original Starsector 0.98a-RC8 game JARs. Does not
redistribute original classes or extracts. Never rely solely on this scan for
completeness; callsites are targeted by known UI bytecode patterns.
"""
import argparse,hashlib,re,subprocess,zipfile
from pathlib import Path
from apply_1024 import OBF,API
from audit_1015_jars import parse_class

SHA={
 'OBF':'5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8',
 'API':'a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a',
}
PATTERNS={
 'com.fs.starfarer.title.C':('com/fs/starfarer/ui/Q.o00000',14),
 'com.fs.starfarer.coreui.refit.WeaponPickerDialog':('com/fs/starfarer/coreui/refit/public.addItem',8),
 'com.fs.starfarer.coreui.refit.FighterPickerDialog':('com/fs/starfarer/coreui/refit/public.addItem',8),
 'com.fs.starfarer.coreui.refit.wgd2.WeaponGroupDialogV2':('com/fs/starfarer/',25),
 'com.fs.starfarer.launcher.opengl.GLLauncher':('com/fs/starfarer/ui/',17),
 'com.fs.starfarer.launcher.opengl.ooOO':('com/fs/starfarer/ui/',17),
 'com.fs.starfarer.api.impl.PlanetSearchData$1':('TooltipMakerAPI.addTitle',3),
 'com.fs.starfarer.api.impl.PlanetSearchData$2':('TooltipMakerAPI.addTitle',3),
 'com.fs.starfarer.api.campaign.econ.MonthlyReport':('MonthlyReport$FDNode.name',4),
 'com.fs.starfarer.api.campaign.impl.items.BaseSpecialItemPlugin':('StringBuilder',10),
 'com.fs.starfarer.api.campaign.FleetAssignment':('Method "<init>"',5),
}

def examine(jar,tag,mapping):
    assert hashlib.sha256(jar.read_bytes()).hexdigest()==SHA[tag],tag
    n=0;countclasses=0
    with zipfile.ZipFile(jar) as z:
      for cl,vals in mapping.items():
        cp,_=parse_class(z.read(cl.replace('.','/')+'.class'))
        literals={cp[e[3]][2].decode('utf8') for e in cp if e and e[0]==8 and cp[e[3]] and cp[e[3]][0]==1}
        assert all(en in literals for en in vals),(cl,'missing original literal')
        proc=subprocess.run(['javap','-c','-p','-classpath',str(jar),cl],capture_output=True,text=True,check=True)
        lines=proc.stdout.splitlines()
        target,span=PATTERNS[cl]
        for en in vals:
          matches=[i for i,line in enumerate(lines) if re.search(r'// String '+re.escape(en.rstrip(' '))+r'\s*$',line)]
          assert matches,(cl,en,'javap missing')
          # UI link rather than just a text-like constant in class.
          if cl.endswith('FleetAssignment'):
            assert any(target in '\n'.join(lines[i:i+span+1]) for i in matches),(cl,en,'not enum user-facing description')
          elif cl.endswith('BaseSpecialItemPlugin'):
            assert any('java/lang/StringBuilder' in '\n'.join(lines[max(0,i-3):i+span+1]) for i in matches),(cl,en,'not concatenated visible value')
          else:
            assert any(target in '\n'.join(lines[i:i+span+1]) for i in matches),(cl,en,'not UI constructor')
          n+=1
        countclasses+=1
    print(f'{tag}: {n} exact user-facing constants checked in {countclasses} original classes')
    return n

def main():
 p=argparse.ArgumentParser();p.add_argument('--obf',required=True,type=Path);p.add_argument('--api',required=True,type=Path);a=p.parse_args()
 assert examine(a.obf,'OBF',OBF)==28
 assert examine(a.api,'API',API)==16
 print('CALLSITE REVIEW PASS: all 44 original literals in UI/enum description paths')
if __name__=='__main__':main()