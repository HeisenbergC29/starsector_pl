# Audyt 1.1: skladane zdania Java (stan 1.0.29, 12.11.2026)

**To jest zrealizowany audyt, a nie wydanie 1.0.30 ani gotowa 1.1.** Nie modyfikowano JAR, map tlumaczen, logiki gry ani plikow gracza.

## Dowody z oryginalnej gry i zainstalowanej 1.0.29

- Sprawdzono SHA-256 oryginalnych `starfarer_obf.jar` i `starfarer.api.jar` gry 0.98a-RC8; dodatkowo SHA-256 bibliotek po rzeczywistej instalacji 1.0.29.
- W obu oryginalnych JAR ponownie i niezaleznie stwierdzono **81 instrukcji `getstatic Misc.STORY` w 24 klasach** (65 OBF + 16 API). W 69 miejscach pierwszym nastepnym literalem jest czlon `point` / `points` (wyszukiwanie nie przechodzi przez granice metody). Wersja 1.0.29 nie lokalizuje `Misc.STORY`, ma nadal wartosc `story`.
- Stwierdzono wiec rzeczywisty problem skladania czesciowo polskich komunikatow: tlumaczone koncowki sa dolaczane do angielskiego `story` w czasie dzialania gry.
- W `com.fs.starfarer.api.impl.campaign.intel.bar.events.BaseBarEventWithPerson` metody `getHimOrHer()` i `getHisOrHer()` uzywaja **tej samej stalej `her` o indeksie JVM #143**, chociaz po polsku wymagaja roznych form zaleznosci od kontekstu. Rozroznienia nie zapewnia dzisiejszy patcher klasowo-literałowy.
- Poprzedni audyt `STORY_PRONOUN_CONTEXT_1019.json` zawiera **219 wywolan metod zaimkowych**, nieobjetych ponownym pelnym przegladem znaczenia w tym etapie. Dotychczasowe 6 podmian `he/she` w 1.0.18 nie rozwiazuje pozostalych przypadkow.

## Grupy 81 kontekstow i kolejne dzialania

| Grupa / ekran | Klasy | Zadanie przed 1.1 |
|---|---|---|
| Postac, awans, umiejetnosci | `CharacterStats`, `coreui.k` i klasy zagniezdzone, `oO0o$1` | sprawdzic liczby, przypadki, kolejnosc czlonow, rozdzielic punkty umiejetnosci od fabularnych |
| Trwale modyfikacje i odzyskiwanie okretow | `ModPickerDialogV3`, `ModWidget`, `FleetMemberRecoveryDialog` | sprawdzic koszt 1/wielu punktow i wszystkie odmiany przy roznych rozmiarach kadluba |
| Etykiety, podpowiedzi, statystyki | `coreui.interface`, `ui.d`, `StandardTooltipV2` i `StandardTooltipV2Expandable` | kontekstowe zlozenie i wyroznienie calych polskich fragmentow |
| Zdarzenia, dialogi, samouczek | `SetStoryOption`, `TutorialLevelUpDialogPluginImpl`, `AptitudeDesc`, `BaseIndustry`, `SkillsChangeOfficerEffect` | wyeliminowac mieszane angielsko-polskie komunikaty, zachowac formaty i callbacki |

**Nie nalezy:** automatycznie zamieniac `story` -> `PF`, `her` na dowolny pojedynczy zaimek ani globalnie usuwac `point(s)`. Nawet jesli skrot PF jest nieodmienny, wsrod 81 kontekstow sa frazy jednostkowe/mnogie, opisy kosztow, teksty eksponowane jako podswietlenia oraz literały dzielone miedzy metodami. Dopiero przeglad kazdego calego zdania rozstrzygnie, czy lokalizacja jest wykonalna samymi podmianami stalej i sasiadujacych tekstow. **Dotychczasowa zasada zakazuje zmieniania wykonywalnego kodu metod.** Mozliwa potrzeba osobnej techniki nie jest zgoda na zmiane bajtkodu.

## Odtwarzalna kontrola

```bash
python3 tools/audit_dynamic_1030.py \
  --obf /PRIVATE/starfarer_obf.jar --api /PRIVATE/starfarer.api.jar \
  --patched-obf /PRIVATE/installed/starfarer_obf.jar \
  --patched-api /PRIVATE/installed/starfarer.api.jar \
  --prior /PRIVATE/STORY_PRONOUN_CONTEXT_1019.json \
  --out /PRIVATE/DYNAMIC_1030_PRIVATE.json \
  --summary /PRIVATE/DYNAMIC_1030_SUMMARY.json
python3 tools/test_dynamic_1030.py
```

Szczegolowy raport 81 wywolan zawiera fragmenty oryginalnych tekstow komercyjnej gry i **pozostaje prywatny**. Publiczny jest wyłącznie `docs/DYNAMIC_AUDIT_1030_SUMMARY.json` z licznikami i technicznym dowodem kolizji. Narzedzie jest tylko do odczytu.

## Kryterium zamkniecia problemu

1. Kazdy z 81 przypadkow ma zatwierdzone wynikowe zdanie na polski, w tym liczba pojedyncza i mnoga, highlight i kombinacje ze znacznikami.
2. Kazde wywolanie metod zaimkowych jest sprawdzone w *docelowej* wypowiedzi. Kolizja `her` jest rozwiazana bez zmiany technicznego identyfikatora i bez naruszenia logiki.
3. Testy instalacji/aktualizacji/przywracania oraz struktury kazdej zmienionej klasy potwierdzaja brak nieautoryzowanych modyfikacji.
4. Rzeczywisty test wizualny w dzialajacej grze Windows potwierdza, ze dynamiczne zdania nie zawieraja mieszanki EN/PL i nie traca formatowania.

Status: **OTWARTY**, issue #4. Zmiany w tym etapie: narzedzia/raporty i blokada przedwczesnego oznaczenia 1.1, bez patchowania gry.
