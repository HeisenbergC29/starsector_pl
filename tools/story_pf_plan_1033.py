"""Candidate class-scoped replacements for 81 Misc.STORY uses.

NOT a release: gated by complete original/translated JAR audits and assembled-output checks.
"""
from collections import defaultdict
P='com.fs.starfarer.'
A=P+'api.'
O=P
API=defaultdict(dict)
OBF=defaultdict(dict)
def reg(mapping,cl,**k):mapping[cl].update(k)
def put(mapping,cl,pairs):
 for en,pl in pairs.items():
  if en in mapping[cl] and mapping[cl][en]!=pl:raise AssertionError((cl,en))
  mapping[cl][en]=pl

# Shared constant: all 81 accesses are reads of this display word.
put(API,A+'util.Misc',{'story':'PF'})
put(API,A+'characters.SkillsChangeOfficerEffect$2',{' point':''})
put(API,A+'impl.campaign.econ.impl.BaseIndustry',{
 ' points required to make an additional improvement.':' potrzebnych do kolejnego ulepszenia.',
 ' points':'',
})
put(API,A+'impl.campaign.rulecmd.SetStoryOption$1',{'point':'','points':'',' ':''})
put(API,A+'impl.campaign.rulecmd.SetStoryOption$BaseOptionStoryPointActionDelegate',{
 ' point':'',' points':'',' points available':'',
 'No ':'Brak dostepnych ',
 'Only %s ':'Dostepne tylko %s ',
 ' available':'',
 'points':'','point':'',
})
put(API,A+'impl.campaign.skills.AptitudeDesc$Level0',{
 ' point\n':'\n',' point':'',
 '    - Choose enough skills in lower tiers to unlock the next tier\n    - It\'s possible to skip a tier by taking more skills in lower tiers instead\n    - Reaching the top tier requires 4 skill points, plus 1 more to take one of the top skills\n    - Taking the second top tier skill requires an additional 2 points spent in lower tier skills\n    - Skills that only affect the piloted ship can be made "elite" at the cost of a ':
 '    - Wybierz wystarczajaco duzo umiejetnosci z nizszych poziomow, aby odblokowac kolejny\n    - Mozesz pominac poziom, wybierajac wiecej umiejetnosci na nizszych poziomach\n    - Osiagniecie najwyzszego poziomu wymaga 4 punktow umiejetnosci, a wybranie jednej z umiejetnosci na nim kolejnego punktu\n    - Wybranie drugiej umiejetnosci na szczycie wymaga dodatkowych 2 punktow w umiejetnosciach nizszego poziomu\n    - Umiejetnosci dotyczace tylko pilotowanego okretu mozna ulepszyc do elitarnego poziomu za ',
})
put(API,A+'impl.campaign.tutorial.TutorialLevelUpDialogPluginImpl',{
 ' points as you gain experience; these can be used to ':' w miare zdobywania doswiadczenia. PF mozna wykorzystac, aby ',
 ' points':'',
 ' point.':'.',
 ' point':'',
})
# OBF: character experience notifications use shared story and special highlight text.
put(OBF,O+'campaign.CharacterStats',{
 'point':'','points':'',
 'Used ':'Wydano ',
 'Gained ':'Zdobyto ',
 ' bonus experience from ':' dodatkowego doswiadczenia za ',
 ' points spent earlier':' jako zwrot za wczesniejsze wydatki',
 ' to spend':'do wydania',
})
put(OBF,O+'coreui.interface',{' point':''})
put(OBF,O+'coreui.k',{
 ' points':'',
 ' point':'',
 ' point and will not grant bonus experience.\n\n':' i nie zapewnia dodatkowego doswiadczenia.\n\n',
 ' point.\n\n':'.\n\n',
 ' point to make elite':', aby podniesc umiejetnosc do poziomu elitarnego',
})
put(OBF,O+'coreui.k$4',{' point.':'.'})
put(OBF,O+'coreui.k$5',{' point instead of a skill point.':' zamiast punktu umiejetnosci.',
 ' point':''})
put(OBF,O+'coreui.k$6',{
 'Using ':'Punkty fabularne (',
 ' points enables you to take actions that are in some way exceptional.':') umozliwiaja wykonywanie wyjatkowych dzialan.',
 ' points':'',
 ' points over the course of each level. ':' na kazdym poziomie. ',
 ' points ':' ',
 ' points grant bonus experience, which doubles your experience gain ':' przynosza dodatkowe doswiadczenie, podwajajace zdobywane PD ',
 'Some uses of ':'Niektore sposoby wykorzystania ',
 ' point", eventually compensating ':'", co z czasem rekompensuje ',
 ' point entirely.':'.',
 'for the use of the ':'wydanie ',
})
put(OBF,O+'coreui.oO0o$1',{
 ' points over the course of each level. ':' na kazdym poziomie. ',
 ' points ':' ',
 ' points':'',
 ' points in certain ways.':' w okreslonych sytuacjach.',
 ' when this bonus XP is used up.':'gdy dodatkowe PD zostana wykorzystane.',
 ' points so far. This is enough to gain ':' do tej pory. To wystarczy, aby zdobyc ',
})
put(OBF,O+'coreui.refit.ModPickerDialogV3',{
 'No ':'Brak dostepnych ',
 ' points available':'',
})
put(OBF,O+'coreui.refit.ModPickerDialogV3$PermaModInfoWidget',{
 ' points remaining':' pozostalo',
})
for clazz in [O+'coreui.refit.ModPickerDialogV3$PermaModInfoWidget$1',
              O+'ui.newui.FleetMemberRecoveryDialog$7']:
 put(OBF,clazz,{
  ' point", eventually compensating ':'", co z czasem rekompensuje ',
  ' point entirely.':'.',
  'for the use of one ':'wydanie jednego ',
  'Bonus experience doubles your experience gain until it\'s used up; %s bonus experience means "enough to earn an extra ':
  'Dodatkowe doswiadczenie podwaja zdobywane PD do wyczerpania; %s dodatkowego doswiadczenia oznacza "dosyc, by zdobyc dodatkowy ',
 })
put(OBF,O+'coreui.refit.ModPickerDialogV3$PermaModInfoWidget$2',{
 ' point':'',
 ' point for each hullmod and ':' za kazda modyfikacje kadluba oraz ',
 ' point for each hullmod.':' za kazda modyfikacje kadluba.',
 'story point':'PF',
})
put(OBF,O+'coreui.refit.ModWidget$1',{
 ' points to build hullmods into the ship, reducing ':' do trwalego montazu modyfikacji kadluba, co obnizy ',
 ' points to enhance certain hull-standard built-in mods, ':' do ulepszania wybranych fabrycznych modyfikacji kadluba, ',
 ' points':'',
 'Use ':'Wykorzystaj ',
 'their ordnance point cost to zero and making them unremovable.':'ich koszt punktow uzbrojenia do zera, a ponadto uniemozliwi ich usuniecie.',
})
put(OBF,O+'ui.d',{' points: ':': '})
put(OBF,O+'ui.d$1',{' points: ':': '})
put(OBF,O+'ui.impl.StandardTooltipV2$1',{
 ' point to recover, grants ':' do odzyskania, zapewnia ',
})
put(OBF,O+'ui.impl.StandardTooltipV2Expandable',{
 ' point':'',' points':'',
 ' points available':'',
 'No ':'Brak dostepnych ',
 'Only %s ':'Dostepne tylko %s ',
 ' available':'',
})
put(OBF,O+'ui.newui.FleetMemberRecoveryDialog',{
 ' points remaining':' pozostalo',
 ' points':'',
 'Not enough story points':'Za malo PF',
})

if __name__=='__main__':
 print('API classes',len(API),'literal keys',sum(map(len,API.values())))
 print('OBF classes',len(OBF),'literal keys',sum(map(len,OBF.values())))
