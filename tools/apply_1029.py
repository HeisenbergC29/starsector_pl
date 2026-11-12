#!/usr/bin/env python3
"""Reproduce Starsector PL 1.0.29: class-scoped, bytecode-verified UI literals.

Run after overlays 1013..1028. Does not alter original game JARs or logic.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

PREV_OBF_SHA='282a465e022c5bf292b08cde9cad59db11f0a92cac067dd237fca1475c694fa6'
NEW_OBF_SHA='fe13bdd519414be15e290ab1fcf84724524ea5e2f133b1bae6ce4e12ad90e71a'
STATUS='VERIFIED_UI_LDC_TO_WIDGET_1029'
OBF={
 'com.fs.starfarer.campaign.ui.intel.PlanetListV2':{'Pop.':'Ludn.'},
 'com.fs.starfarer.campaign.ui.marketinfo.o0O0':{'Manage...':'Zarzadzaj...'},
 'com.fs.starfarer.campaign.ui.marketinfo.o0OO':{'Credits/month':'Kredyty/mies.'},
 'com.fs.starfarer.campaign.ui.oOOO.F':{'In-system':'W ukladzie'},
 'com.fs.starfarer.campaign.ui.trade.new':{'Flux/damage':'Strumien/obrazenia'},
 'com.fs.starfarer.coreui.A.O0Oo':{'In-system':'W ukladzie'},
 'com.fs.starfarer.coreui.A.Z$1':{'Light-years':'Lata swietlne'},
 'com.fs.starfarer.coreui.A.oOOo':{'Light-years':'Lata swietlne'},
 'com.fs.starfarer.coreui.class$o':{'Range:':'Zasieg:','Usage:':'Zuzycie:'},
 'com.fs.starfarer.coreui.k':{'Level ':'Poziom '},
 'com.fs.starfarer.coreui.null':{'Level ':'Poziom '},
 'com.fs.starfarer.coreui.oO0o':{'Level ':'Poziom '},
 'com.fs.starfarer.coreui.refit.L':{'Built-in':'Wbudowane'},
 'com.fs.starfarer.coreui.refit.WeaponGroupDialog':{'Shield:':'Oslona:'},
 'com.fs.starfarer.coreui.refit.WeaponGroupDialog$oo':{'Group ':'Grupa '},
 'com.fs.starfarer.coreui.refit.oOOO':{'Bought ':'Kupiono ','Refunded ':'Zwrocono '},
 'com.fs.starfarer.ui.impl.L$1':{'Level ':'Poziom '},
 'com.fs.starfarer.ui.impl.Oooo$2':{'Price/unit':'Cena/jedn.'},
 'com.fs.starfarer.ui.impl.StandardTooltipV2$3':{'Level ':'Poziom '},
 'com.fs.starfarer.ui.impl.ooOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO':{'Reinforce...':'Wzmocnij...'},
 'com.fs.starfarer.ui.newui.L':{'Crew/Cargo':'Zaloga/Ladunek'},
}
API={
 'com.fs.starfarer.api.impl.campaign.FleetInteractionDialogPluginImpl':{'Go back':'Wroc'},
 'com.fs.starfarer.api.impl.campaign.intel.misc.LuddicShrineIntel':{'Go back':'Wroc'},
 'com.fs.starfarer.api.impl.campaign.procgen.PlayerFleetGenPluginImpl':{'Go back':'Wroc'},
 'com.fs.starfarer.api.impl.campaign.rulecmd.salvage.MarketCMD':{'Go back':'Wroc'},
 'com.fs.starfarer.api.impl.campaign.events.FoodShortageEvent':{'Food shortage - ':'Niedobor zywnosci - ','Possible food shortage - ':'Mozliwy niedobor zywnosci - '},
 'com.fs.starfarer.api.impl.campaign.procgen.EventTestPluginImpl':{'Fight!':'Walcz!'},
}

def one(s,old,new):
 assert s.count(old)==1,('expected exactly one',repr(old),s.count(old))
 return s.replace(old,new)

def read_csv(path):
 with path.open('r',encoding='utf-8',newline='') as f:
  c=csv.DictReader(f)
  assert c.fieldnames==['source_class','english_literal','polish_ascii_draft','status']
  return list(c)

def append_map(parent,oldname,newname,extra):
 src=parent/oldname;dst=parent/newname
 original=read_csv(src)
 assert not dst.exists(),dst
 known={(r['source_class'],r['english_literal']) for r in original}
 fresh=[]
 for cl,terms in extra.items():
  for en,pl in terms.items():
   assert en!=pl and en.isascii() and pl.isascii()
   assert (cl,en) not in known,(cl,en)
   assert en.startswith(' ')==pl.startswith(' ') and en.endswith(' ')==pl.endswith(' '),(cl,en,pl)
   assert en.count('\n')==pl.count('\n')
   fresh.append({'source_class':cl,'english_literal':en,'polish_ascii_draft':pl,'status':STATUS})
 with dst.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
  w.writeheader();w.writerows(original+fresh)
 return len(original),len(fresh)

def main(root):
 obf=root/'buildtools/NARZEDZIA_OBF'
 api=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO'
 a,b=append_map(obf,'TLUMACZENIA_OBF_10128.csv','TLUMACZENIA_OBF_10129.csv',OBF)
 c,d=append_map(api/'translations','TLUMACZENIA_JAR_1028.csv','TLUMACZENIA_JAR_1029.csv',API)
 assert a==3485 and c==5208 and b==23 and d==7,(a,b,c,d)
 p=obf/'main.go';s=p.read_text('utf-8')
 s=one(s,'TLUMACZENIA_OBF_10127.csv TLUMACZENIA_OBF_10128.csv','TLUMACZENIA_OBF_10127.csv TLUMACZENIA_OBF_10128.csv TLUMACZENIA_OBF_10129.csv')
 s=one(s,'const currentPatchState = "patched 10128"','const currentPatchState = "patched 10129"')
 s=one(s,'var knownPreviousOBFHashes = map[string]string{','var knownPreviousOBFHashes = map[string]string{\n\t"'+PREV_OBF_SHA+'": "10128",')
 s=one(s,'loadTranslations("TLUMACZENIA_OBF_10128.csv")','loadTranslations("TLUMACZENIA_OBF_10129.csv")')
 s=one(s,'state == currentPatchState || state == "patched 10127"','state == currentPatchState || state == "patched 10128" || state == "patched 10127"')
 s=one(s,'OBF 1.0.28 | stan:','OBF 1.0.29 | stan:')
 s=one(s,'1.0.28: Lokalizacja tekstow OBF','1.0.29: Lokalizacja tekstow OBF')
 s=one(s,'0.9.99-1.0.28; odmowa modyfikacji','0.9.99-1.0.29; odmowa modyfikacji')
 p.write_text(s,'utf-8')
 p=obf/'main_test.go';p.write_text(one(p.read_text('utf-8'),'alreadyThisRelease("patched 10128")','alreadyThisRelease("patched 10129")'),'utf-8')
 p=obf/'mapping_10128_test.go';p.write_text(one(p.read_text('utf-8'),'!alreadyThisRelease("patched 10128") || alreadyThisRelease("patched 10127")','alreadyThisRelease("patched 10128") || alreadyThisRelease("patched 10127")'),'utf-8')
 p=api/'main.go';s=p.read_text('utf-8')
 s=one(s,'const version = "1028"','const version = "1029"')
 s=one(s,'const exeVersion = "1.0.28"','const exeVersion = "1.0.29"')
 s=one(s,'"1026", "1027", version}','"1026", "1027", "1028", version}')
 s=one(s,'PL ASCII patch up to 1.0.28','PL ASCII patch up to 1.0.29')
 s=one(s,'const expectedOBFPatched10128 = "'+PREV_OBF_SHA+'"','const expectedOBFPatched10128 = "'+PREV_OBF_SHA+'"\nconst expectedOBFPatched10129 = "'+NEW_OBF_SHA+'"')
 s=one(s,'hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10128','hash(obf) != expectedOBF && hash(obf) != expectedOBFPatched10129 && hash(obf) != expectedOBFPatched10128')
 p.write_text(s,'utf-8')
 p=root/'buildtools/NARZEDZIA_INSTALATOR/main.go';p.write_text(one(p.read_text('utf-8'),'const edition = "1.0.28"','const edition = "1.0.29"'),'utf-8')
 p=root/'mod/mod_info.json';meta=json.loads(p.read_text('utf-8'))
 assert meta['version']=='1.0.28'
 meta['version']='1.0.29';meta['description']=one(meta['description'],'1.0.28','1.0.29')
 p.write_text(json.dumps(meta,ensure_ascii=True,indent=2)+'\n','utf-8')
 p=root/'mod/CZYTAJ.txt';s=p.read_text('utf-8')
 s=one(s,'STARSECTOR PL ASCII 1.0.28','STARSECTOR PL ASCII 1.0.29')
 s+='\nKolejne etykiety interfejsu: poziomy, mapa, handel, refit, glod i opcje dialogowe.\n'
 p.write_text(s,'utf-8')
 print('1.0.29, OBF',a,'+',b,'API',c,'+',d)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('worktree',type=Path)
 main(p.parse_args().worktree)
