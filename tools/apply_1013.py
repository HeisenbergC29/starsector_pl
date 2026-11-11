#!/usr/bin/env python3
"""Apply verified API UI copy for 1.0.13 atop 1.0.12 worktree.

Keeps TLUMACZENIA_JAR_1010.csv for identification and upgrade of legacy patched jars.
No original game resources are bundled or modified by this script.
"""
from pathlib import Path
import argparse, csv, io, json, re

# Source text is selected by exact class and an unambiguous full-string prefix
# from original JAR CONSTANT_String, verified against prior raw-unmapped audit.
FIXES = [
('com.fs.starfarer.api.impl.campaign.abilities.DistressCallAbility', 'May be used by a stranded fleet',
'Flota, ktorej zabraklo paliwa lub zaopatrzenia, moze nadac przez nadprzestrzen sygnal alarmowy i poprosic pobliskie floty o pomoc. Na pomoc trzeba czasem czekac wiele dni, o ile w ogole nadejdzie. Korzystanie z niej bedzie skutkowalo coraz wiekszym pogorszeniem stosunkow z flotami, ktore odpowiedzialy na wezwanie.'),
('com.fs.starfarer.api.impl.campaign.abilities.GraviticScanAbility', 'Reliably detects the presence of slipstreams',
'Niezawodnie wykrywa strumienie nadprzestrzenne w promieniu %s lat swietlnych. Poza Otchlania poziom szumu tla uniemozliwia wykrycie innych zrodel neutrin. Gdy flota podrozuje strumieniem, detektor ulega przeciazeniu i wylacza sie.'),
('com.fs.starfarer.api.impl.campaign.intel.bases.PirateBaseIntel', 'You have an %s with the base commander',
'Masz %s z dowodca bazy. Jej floty z reguly nie atakuja twoich kolonii ani szlakow handlowych. Oplata za ochrone wynosi %s przychodu brutto wszystkich objetych nia kolonii, czyli obecnie %s miesiecznie.'),
('com.fs.starfarer.api.impl.campaign.intel.events.LuddicChurchHostileActivityFactor$1', 'A large community of the faithful',
'Duza wspolnota wiernych, pozostajaca poza bezposrednia kontrola Kosciola i mogaca wyrosnac na wazny osrodek kulturowy, budzi coraz wiekszy niepokoj jego wladz. W twoich ukladach mozna spotkac floty Rycerzy Ludda zwane "obroncami", ktore rzekomo strzega interesow miejscowych wiernych.'),
('com.fs.starfarer.api.impl.campaign.intel.events.LuddicChurchStandardActivityCause$1', 'Negotiating with the Luddic Church',
'Negocjacje z Kosciolem Ludda w sprawie kontroli naplywu wiernych do twoich kolonii prawdopodobnie zakoncza te szykany. Jesli konflikt o niewielkiej intensywnosci pozostanie nierozwiazany, z czasem dojdzie do jego zaostrzenia i rozstrzygniecia w jedna lub druga strone.'),
('com.fs.starfarer.api.impl.campaign.intel.events.TriTachyonHostileActivityFactor', "You've dealt with the mercenary attack", 
'Udalo ci sie odeprzec atak najemnikow, co znacznie ostudzilo zapal przeciwnikow do dalszej agresji. Napady na handel trwaja, lecz postep tego wydarzenia jest zmniejszony o %s, a kolejne ataki na duza skale sa malo prawdopodobne.'),
('com.fs.starfarer.api.impl.campaign.intel.events.ht.HTNonASBScanFactor$1', 'A scan of the right entity or location',
'Skanowanie odpowiedniego obiektu lub miejsca moze ujawnic szczegoly topografii okolicznej nadprzestrzeni. Cel zwykle musi byc na tyle masywny, by wytwarzac znaczna studnie grawitacyjna, emitowac wysokoenergetyczne promieniowanie albo wyrozniac sie w inny, niezwykly sposob.'),
('com.fs.starfarer.api.impl.campaign.intel.events.ht.HTScanFactor$1', 'An %s of the right entity or location',
'Wykorzystanie %s do zbadania odpowiedniego obiektu lub miejsca moze ujawnic topografie okolicznej nadprzestrzeni. Cel zwykle musi byc na tyle masywny, by wytwarzac znaczna studnie grawitacyjna, emitowac wysokoenergetyczne promieniowanie albo wyrozniac sie w inny, niezwykly sposob.'),
('com.fs.starfarer.api.impl.campaign.intel.events.ht.HyperspaceTopographyEventIntel', 'Detailed sensor readings greatly aid',
'Dokladne odczyty czujnikow znacznie ulatwiaja nawigacje w nadprzestrzeni. Dane mozna pozyskac na wiele sposobow: korzystajac z sieci czujnikow w ukladach, uruchamiajac Aktywny impuls czujnikow w poblizu interesujacych zjawisk, podrozujac przez nadprzestrzen z bardzo duza predkoscia lub kupujac informacje od zbieraczy zlomu.'),
('com.fs.starfarer.api.impl.campaign.intel.events.ttcr.TriTachyonCommerceRaiding', 'The %s needs to be convinced',
'Trzeba przekonac %s, ze dalsze inwestowanie w dzialania przeciwko twoim interesom nie oplaca sie w dluzszej perspektywie. Jesli uda ci sie przekazac ten sygnal bez otwartej wrogosci albo pozniej zalagodzic urazy, moga uznac, ze rozumiesz realia biznesu i warto z toba wspolpracowac.'),
('com.fs.starfarer.api.impl.hullmods.ConvertedHangar', 'Increases fighter refit time by',
'Czas przygotowania mysliwcow wydluza sie o %s, a wskaznik uzupelniania eskadr spada i odnawia sie o %s wolniej. Ponadto bombowce powracajace po uzbrojenie (lub mysliwce do naprawy) potrzebuja %s swojego podstawowego czasu przygotowania, aby ponownie wystartowac, choc normalnie trwa to krocej niz sekunde. '),
('com.fs.starfarer.api.impl.hullmods.ConvertedHangar', 'Increases the minimum crew by',
'Minimalna wymagana zaloga wzrasta o %s ze wzgledu na pilotow i obsluge pokladowa. Punkty wystawienia okretu i koszt zaopatrzenia potrzebnego do odzyskania gotowosci po walce rosna o %s na kazde %s punktow uzbrojenia przeznaczonych na mysliwce, ale nie mniej niz o %s punkt. Proporcjonalnie rosnie tez utrata gotowosci bojowej przy kazdym wystawieniu.'),
('com.fs.starfarer.api.impl.hullmods.HighResSensors', 'A ship with high resolution sensors',
'Okret z czujnikami wysokiej rozdzielczosci zwieksza zasieg czujnikow floty o %s/%s/%s/%s, zaleznie od wielkosci kadluba. Kazdy kolejny taki okret daje coraz mniejszy przyrost. Im wiekszy jest najwyzszy pojedynczy bonus do zasiegu czujnikow we flocie, tym pozniej zaczyna sie spadek korzysci.'),
('com.fs.starfarer.api.impl.hullmods.NeuralInterface', 'After the transfer is complete',
'Po zakonczeniu przeniesienia czas odnowienia systemu docelowego okretu (jesli wystepuje) zostaje wyzerowany. Jesli system korzysta z ladunkow, zyska jeszcze jeden ladunek. Efekt ten ma czas odnowienia rowny %s zaoszczedzonego czasu odnowienia systemu lub regeneracji ladunku.'),
('com.fs.starfarer.api.impl.hullmods.PhaseField', "In addition, the fleet's detected-at range is reduced", 
'Ponadto zasieg, z ktorego mozna wykryc flote, jest zmniejszany przez mnoznik wyliczany na podstawie lacznej sygnatury czujnikowej %s okretow o najwyzszej sygnaturze we flocie oraz lacznej sily czujnikow %s okretow fazowych o najwyzszej sile czujnikow. Efekt dziala tylko przy wylaczonym transponderze.'),
]

ENGLISH = [
"May be used by a stranded fleet to punch a distress signal through to hyperspace, asking nearby fleets to bring aid in the form of fuel and supplies. Help may take many days to arrive, if it arrives at all, and taking advantage of it will result in a progressively higher reduction in standing with the responders.",
"Reliably detects the presence of slipstreams out to a range of %s light-years. Except for abyssal areas, the background noise levels are such that it is unable to detect any other neutrino sources. When the fleet is traversing a slipstream, the detector is overwhelmed and shuts down.",
"You have an %s with the base commander, and fleets from this base do not, as a rule, harass your colonies or shipping. The protection payment is %s of the gross income of all of your affected colonies, which amounts to %s per month at their current level of income.",
'A large community of the faithful - not under their direct control, and with potential to emerge as a major cultural center - is a growing source of concern to the Church. "Protector" fleets operated by the Knights of Ludd can be found in your systems, ostensibly there to protect the interests of the local Luddic population.',
'Negotiating with the Luddic Church about controlling the immigration of the faithful to your colonies is likely to get this harassment to stop. If left unchecked, this low-grade conflict will eventually come to a head and is likely to be resolved one way or another.',
"You've dealt with the mercenary attack sent against you, and this has considerably cooled the enthusiasm for continued aggression. Commerce-raiding continues, but the event progress value is reduced by %s, and no further large-scale attacks are likely to be mounted.",
'A scan of the right entity or location can provide insight into the topography of surrounding hyperspace. The target usually needs to be massive enough to produce a significant gravity well, produce a high energy discharge, or be exotic or unusual in some other way.',
'An %s of the right entity or location can provide insight into the topography of surrounding hyperspace. The target usually needs to be massive enough to produce a significant gravity well, produce a high energy discharge, or be exotic or unusual in some other way.',
'Detailed sensor readings greatly aid hyperspace navigation. There are many ways of acquiring this data, including using in-system sensor arrays, using an Active Sensor Burst near interesting phenomena, traveling through hyperspace at a very high burn level, or simply buying the data from scavengers.',
'The %s needs to be convinced that continued investment in acting against your interests is unprofitable in the long term. If you are able to send this message without becoming openly hostile - or smooth any ruffled feathers afterwards - this may even mark you as someone whose understanding of business realities makes them worth working with.',
'Increases fighter refit time by %s, and the fighter replacement rate both decays and recovers %s more slowly. In addition, bombers returning to rearm (or fighters returning for repairs) take %s of their base refit time to relaunch, where normally it takes under a second. ',
"Increases the minimum crew by %s to account for pilots and flight crews. Increases the ship's deployment points and supply cost to recover from deployment by %s for every %s ordnance points spent on fighters, or by at least %s point. This comes with a proportional increase in combat readiness lost per deployment.",
"A ship with high resolution sensors increases the fleet's sensor range by %s/%s/%s/%s, depending on hull size. Each additional ship with high resolution sensors provides diminishing returns. The higher the highest sensor range increase from a single ship in the fleet, the later diminishing returns kick in.",
"After the transfer is complete, the target ship's system cooldown (if any) will be reset, and if the ship system uses charges, it will gain an additonal charge. This effect operates on a cooldown equal to %s the cooldown/charge regeneration time saved by it.",
"In addition, the fleet's detected-at range is reduced by a multiplier based on the total sensor profile of the %s highest-profile ships in the fleet, and the total sensor strength of the %s phase ships with the highest sensor strength values. This effect only applies when the fleet's transponder is turned off."
]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('worktree', type=Path)
    args=parser.parse_args()
    root=args.worktree
    source=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1010.csv'
    out=source.with_name('TLUMACZENIA_JAR_1013.csv')
    text=source.read_text('utf-8')
    with io.StringIO(text, newline='') as f:
        existing=list(csv.DictReader(f))
    assert len(existing)==5042, len(existing)
    seen={(r['source_class'],r['english_literal']) for r in existing}
    assert len(FIXES)==len(ENGLISH)==15
    placeholders=re.compile(r'%(?:(?:\d+\$)?[-+#0,(]*\d*(?:\.\d+)?[sdifxXoegGaAcCbBhHn%])|\$[a-zA-Z_][A-Za-z_0-9]*|\{[0-9]+\}')
    new=[]
    for (cls,prefix,pl),en in zip(FIXES,ENGLISH):
        assert en.startswith(prefix), (cls,prefix)
        assert en.isascii() and pl.isascii()
        assert (cls,en) not in seen, (cls,prefix)
        assert sorted(placeholders.findall(en))==sorted(placeholders.findall(pl)), (cls,prefix)
        new.append(dict(source_class=cls,english_literal=en,polish_ascii_draft=pl,status='VERIFIED_TOOLTIP_CALLSITE_1013'))
    with out.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['source_class','english_literal','polish_ascii_draft','status'],lineterminator='\r\n')
        writer.writeheader();writer.writerows(existing+new)
    go=root/'buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/main.go'
    data=go.read_text()
    for old,n in [('const version = "1010"','const version = "1013"'),('const exeVersion = "1.0.10"','const exeVersion = "1.0.13"'),('"1009", version}','"1009", "1010", version}')]:
        assert data.count(old)==1, old
        data=data.replace(old,n)
    go.write_text(data)
    ig=root/'buildtools/NARZEDZIA_INSTALATOR/main.go'
    data=ig.read_text();assert data.count('const edition = "1.0.12"')==1
    ig.write_text(data.replace('const edition = "1.0.12"','const edition = "1.0.13"'))
    mod=root/'mod/mod_info.json';info=json.loads(mod.read_text())
    assert info['version']=='1.0.12';info['version']='1.0.13'
    info['description']=info['description'].replace('1.0.12','1.0.13')
    mod.write_text(json.dumps(info,ensure_ascii=True,indent=2)+'\n')
    readme=root/'mod/CZYTAJ.txt';data=readme.read_text()
    assert data.count('1.0.12')==1
    data=data.replace('1.0.12','1.0.13').replace('Mapy patcherow JAR sa takie jak w 1.0.10.','Dodano 15 tekstow tooltipow Java API. Mapa OBF bez zmian; API rozpoznaje poprzednie wydania.')
    readme.write_text(data)
    print('Applied 1.0.13, 15 API translations, map rows',len(existing+new))

if __name__=='__main__': main()