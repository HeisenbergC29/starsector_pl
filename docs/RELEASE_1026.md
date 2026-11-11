# Starsector PL 1.0.26 — kolejne 86 etykiet i przyciskow (2026-11-12)

**Gra:** Starsector 0.98a-RC8. **Cel 1.1 nadal NIE jest ukończony.** Wszelkie nowe napisy w plikach gry są kodowane w ASCII.

## Zmiany względem 1.0.25

Z oryginalnych `CONSTANT_String` przetłumaczono **86 brakujących etykiet w 20 klasach OBF**. Wprowadzono tylko nowe wiersze w mapie OBF (3294 → **3380**), a mapa API pozostaje identyczna z 1.0.25 (5150 wierszy mapy / **5148** realnych podmian). **870 plików danych pozostaje identycznych bajtowo**.

| Ekran lub funkcja | Klasy | Nowych etykiet | Przykłady |
|---|---:|---:|---|
| Refit, modyfikacje kadłuba i grupy uzbrojenia | 3 | 11 | `Autofit...` → `Autodopasuj...`, `Undo` → `Cofnij`, `Linked` → `Polaczone` |
| Badanie planet oraz lista planet | 2 | 8 | `Continue` → `Kontynuuj`, `Hazard` → `Zagrozenie`, `Dist` → `Odlegl.` |
| Wybór celów najazdu i przemysł | 3 | 18 | `Objective` → `Cel`, `Upkeep` → `Utrzymanie`, `Downgrade` → `Obniz poziom` |
| Przegląd rynków i gospodarki | 3 | 10 | `Accessibility` → `Dostepnosc`, `Incoming` → `Przychodzace` |
| Oficerowie i przydziały | 2 | 9 | `Admins` → `Administratorzy`, `Reassign` → `Zmien przydzial` |
| Odzysk okrętów i wyposażenie | 2 | 8 | `Recover` → `Odzyskaj`, `Mounts:` → `Mocowania:` |
| Przyciski nawigacji i zakładki zarządzania | 2 | 13 | `Fleet` → `Flota`, `Intel` → `Informacje`, `Refit` → `Modyfikacje` |
| Ładunek i handel | 1 | 4 | `Cargo` → `Ladunek`, `Jettison` → `Wyrzuc` |
| Dziennik zdarzeń i dane towarów | 2 | 5 | `Date` → `Data`, `Demand` → `Popyt` |
| **Razem** | **20** | **86** | |

*Dwa ekrany zakładek korzystają z odrębnych klas i mają różne zestawy przycisków, stąd powtórzenie części etykiet w dwóch lokalizacjach bajtkodu. Liczba 86 oznacza podmiany w parach klasa–literał, nie 86 unikalnych słów.*

Zgodność znaczenia i odmiany ustalano według kontekstu klasy i dalszych operacji bajtkodu. Nie wprowadzono pustych podmian `en == pl`. `System:` pozostawiono bez zmiany, bo w polskim wygląda identycznie. Nie zmieniono technicznych enum ID (np. `FOLLOW`, `HOLD`) ani klas gry, metod i zmiennych.

## Audyt oryginalnych JAR i wyniki testów lokalnych (Linux)

| Kontrola | Wynik |
|---|---|
| Oryginalne OBF/API: SHA-256 zgodne z wydaniem 0.98a-RC8 | PASS |
| OBF `CONSTANT_String`: **3380** zatwierdzonych referencji, **533** zmienione klasy | PASS |
| API `CONSTANT_String`: **5148** zatwierdzonych referencji, **936** klas | PASS |
| Porównanie całego bajtkodu metod względem oryginału | **0 zmian niedozwolonych** |
| OBF — **533** prawidłowo zmodyfikowane sekcje sum manifestu | PASS |
| Niezmienione wpisy w JAR: OBF **2394**, API **2604** | PASS |
| W oryginalnym bajtkodzie 86 etykiet w **106** odwołaniach `ldc`, 20 klasach; 11 wymaga sprawdzenia pośredniej ścieżki UI | PASS (kontrola statyczna) |
| Instalacja obu patcherów na czystych JAR | PASS |
| Aktualizacja obu rzeczywiście spatchowanych bibliotek 1.0.25 → 1.0.26, identyczna ze świeżą instalacją | PASS |
| Ponowna instalacja (idempotencja) | PASS |
| Przywrócenie oryginalnych JAR bajt w bajt | PASS |
| Celowo uszkodzony OBF i osobno API odrzucone bez nadpisania | PASS |
| 5 testów negatywnych map: zmiana starego/nowszego tekstu, klasy, ID i mapy API | PASS |
| **1021** odtworzonych plików źródłowych zgodnych bajtowo (pomijając wygenerowane binaria) | PASS |
| **870/870** plików `data/` zgodnych z paczką 1.0.25 | PASS |
| `rules.csv`: **7371/7371** poprawnych opcji | PASS |
| Go test/vet: OBF, API, instalator; 3 pliki EXE Windows x64 (PE32+) | PASS |
| ZIP **873 wpisy**, CRC poprawne, oryginalnych JAR brak | PASS |
| Natywny instalator Windows i uruchomiona rozgrywka | **NIE PRZEPROWADZONO** |
| Potwierdzona pełna lokalizacja 1.1 | **NIE** |

Wynikowy **OBF SHA-256**: `a475ef535590b79da74d425f9e3f7566c85bed163e4a3795e88a593b7f69f42a`.

Wynikowy **API SHA-256** (identyczny z 1.0.25): `3d584fb28a334adc62894795bb197e3618eee718d1830de129eec22accd5b843`.

**Paczka:** `Starsector_PL_ASCII_0.98a_RC8_1.0.26_MINIMALNY.zip` — **13 281 340 bajtów**; SHA-256 `b96962ea6353544a5d6a0db4dfabe0286a674d34b004b3182675811a844733e7`.

ZIP, raport testów oraz dokładny audyt `ST_1026_CALLSITES.json` zapisano w Bibliotece projektu. Publiczne repozytorium nie zawiera oryginalnych JAR, plików binarnych z gry ani pełnych zrzutów literałów komercyjnych klas.

**GitHub Actions: PASS** — [przebieg 43122029677](https://github.com/HeisenbergC29/starsector_pl/actions/runs/43122029677), commit `337def2b`. Zaliczone: odtworzenie źródeł z migawek i wszystkich nakładek 1013–1026, rygorystyczny audyt map OBF/API oraz 3659 starszych podmian DRAFT/OPTIONAL, walidacja `rules.csv`, Go test/vet i kompilacja trzech instalacyjnych plików PE32+ Windows x64. Nie jest to test uruchomionej gry na Windows.

## Odtworzenie z GitHuba

```bash
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1026_ui.py worktree
python3 tools/test_1026_delta.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1026.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.26_MINIMALNY.zip
```

Weryfikacja rzeczywistych oryginalnych literałów wymaga prywatnego `starfarer_obf.jar` i narzędzia `javap`:

```bash
python3 tools/verify_1026_callsites.py \
  --obf /prywatna/sciezka/starfarer_obf.jar \
  --out /tmp/ST_1026_CALLSITES.json
```

## Otwarte prace do wersji 1.1

1. Dalszy audyt krótkich etykiet i tekstów wyświetlanych przez OBF/API oraz wszystkich nazw i skrótów.
2. **81** miejsc użycia `Misc.STORY` i pozostałe zaimki w dynamicznie składanych zdaniach.
3. Audyt **znaczenia** instalowanych tłumaczeń oznaczonych `DRAFT/OPTIONAL`. Kontrola 3659 wierszy w 1.0.25 wykluczyła naruszenia podstawowych znaczników, ale nie zastępuje recenzji całych dialogów.
4. Test uruchomionej gry i instalatora na Windows.

**1.0.26 jest kolejną przetestowaną wersją roboczą, a nie ostatecznym 1.1.**
