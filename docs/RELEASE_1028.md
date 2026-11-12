# Starsector PL 1.0.28 — etykiety mapy, symulatora i wydarzen (2026-11-12)

**Gra:** Starsector **0.98a-RC8**. Docelowa kompletna lokalizacja **1.1 NIE jest jeszcze ukonczona**. Wszystkie teksty dodane do zasobow gry sa w **polskim ASCII**, bez polskich znakow.

## 92 poprawki widocznego interfejsu

Nowe tlumaczenia dodane do map `CONSTANT_String` klas Java: **64 OBF** (18 klas), **28 API** (9 klas). Kazdy oryginalny literal potwierdzono w odpowiednim JAR, a wszystkie **122** uzycia `ldc` (75 OBF, 47 API) skontrolowano z uwzglednieniem metod i miejsc wyswietlania. Pominieto identyfikatory techniczne, tagi i klucze sortowania. Zawartosc wszystkich **870 plikow `data/`** jest identyczna z 1.0.27.

| Zakres | JAR | Przyklady zatwierdzonych podmian |
|---|---|---|
| Mapa sektora i nawigacja | OBF | `Constellations` → `Konstelacje`, `Hyperspace` → `Nadprzestrzen`, `Waypoint` → `Punkt trasy` |
| Handel, magazynowanie i przemysl | OBF | `Buy` → `Kup`, `Sell` → `Sprzedaj`, `Queued` → `W kolejce`, `Industry/structure` → `Przemysl/struktura` |
| Zarzadzanie wariantami statkow | OBF | `Delete` → `Usun`, `Rename` → `Zmien nazwe`, `Load` → `Wczytaj` |
| Widoczne statusy i relacje | OBF | `Hostile` → `Wrogi`, `Friendly` → `Przyjazny`, `Unknown` → `Nieznany` |
| Osobowosci oficerow | API | `Aggressive` → `Agresywny`, `Cautious` → `Ostrozny`, `Reckless` → `Brawurowy`, `Steady` → `Opanowany` |
| Wydarzenia, zlecenia i dialogi | API | `Continue` → `Kontynuuj`, `Leave` → `Odejdz`, `Confirm` → `Potwierdz`, `Abandon` → `Porzuc` |

Zrodla `aggressive`, `cautious`, `steady`, `reckless` pisane mala litera sa **techniczne** i pozostaly nietkniete. Analogicznie nie zmieniono nazw klas, stalych enum, pol metod, skryptow ani identyfikatorow gry. Niezmienne pozostaja wszystkie wczesniejsze podmiany.

## Wyniki testow na rzeczywistych oryginalnych JAR (Linux)

| Test | Wynik |
|---|---|
| OBF: **3485** zatwierdzonych trafien w **536** klasach; **2391** pozostalych wpisow JAR niezmienionych | PASS |
| API: **5206** trafien w **937** klasach; mapa ma **5208** wierszy, dwa historyczne wiersze bez klas w API | PASS |
| API: **2603** pozostale wpisy JAR niezmienione | PASS |
| Klasa po klasie: zmiany ograniczone do dopuszczonych `CONSTANT_String` | PASS |
| Wykonywalny bajtkod metod i inne struktury klasy | **0 niedozwolonych zmian** |
| OBF: **536** sekcji sum kontrolnych manifestu zgodnych z **536** zmienionymi klasami | PASS |
| Oryginalne SHA-256 OBF i API zgodne z 0.98a-RC8 | PASS |
| Swieza instalacja obu patcherow na oryginalnych JAR | PASS |
| **Rzeczywista aktualizacja 1.0.27 → 1.0.28** na wczesniej spatchowanych obu bibliotekach | PASS |
| Wynik obu JAR po aktualizacji identyczny bajtowo ze swieza instalacja | PASS |
| Ponowna instalacja (idempotencja) | PASS |
| Przywrocenie bajtowo oryginalnych JAR | PASS |
| Dwa celowo uszkodzone JAR odrzucone bez zapisywania zmian | PASS |
| **14** testow negatywnych map: wykrywanie nieautoryzowanych podmian | PASS |
| **1027** niegenerowanych plikow zrodel odtworzonych bajtowo, **5** wygenerowanych plikow binarnych weryfikowanych osobno | PASS |
| **870/870** plikow data bez zmian wobec 1.0.27 | PASS |
| `rules.csv` — **7371/7371** poprawnych opcji dialogowych | PASS |
| Go test/vet: OBF, API i instalator; kompilacja 3 PE32+ Windows x64 | PASS |
| ZIP: **873 wpisy**, test CRC, brak oryginalnych JAR | PASS |
| Natywny test instalatora na Windows i uruchomienie gry | **NIE WYKONANO** |
| Potwierdzona pelna polonizacja 1.1 | **NIE** |

**Oryginalne SHA-256:**
- OBF `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`
- API `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`

**SHA-256 po instalacji 1.0.28:**
- OBF `282a465e022c5bf292b08cde9cad59db11f0a92cac067dd237fca1475c694fa6`
- API `4b60a515c0c28d8896d5f6883471cd2122676021663f176f35a66255d6112c14`

**Pakiet:** `Starsector_PL_ASCII_0.98a_RC8_1.0.28_MINIMALNY.zip`, **13 959 854 B**, SHA-256 `cf9010a7fc4cf54795df6fa1561805384c7dee5c000c6bca9fc0dff27dadfdd1`. Paczka i JSON `Starsector_PL_1.0.28_TESTY.json` w prywatnej Bibliotece projektu. W ZIP znajduja sie 870 plikow danych, `mod_info.json`, `CZYTAJ.txt` i EXE instalatora; brak oryginalnych JAR.

## Audyt blokera `Misc.STORY`: brak ryzykownej podmiany

Oryginalna stala `com.fs.starfarer.api.util.Misc.STORY` ma wartosc `story`. Potwierdzono **81 uzyc przez `getstatic` w 24 klasach** (65 OBF i 16 API). W **69** miejscach nastepny fragment budowanego komunikatu zaczyna sie od `point` lub `points`. Ta sama stala wystepuje z roznymi liczbami, odmianami i sposobami wyroznienia.

**Nie zmieniono `Misc.STORY` i nie zastosowano globalnego `story` → `PF`**. Taka podmiana nie naprawilaby polskiej odmiany. Przykladowo `story point`, `story points`, `one story point` oraz frazy z polskimi fragmentami wymagaja roznych konstrukcji. Konieczny jest przeglad calego lancucha, nie sama zamiana jednego slowa. Szczegolowy prywatny `ST_1028_STORY_AUDIT.json` i publiczny odczytowy `tools/audit_story_1028.py` sa zapisane do dalszej pracy. Publiczne repozytorium nie zawiera komercyjnych oryginalnych JAR ani ich calych zrzutow literałów.

## Odtworzenie stanu z GitHub

```sh
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1028_ui.py worktree
python3 tools/test_1028_delta.py
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1028.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.28_MINIMALNY.zip
```

Z **prywatnymi** oryginalnymi JAR i `javap` mozna dodatkowo zweryfikowac nowe miejsca uzycia oraz skan `Misc.STORY`:

```sh
python3 tools/verify_1028_callsites.py --obf /private/starfarer_obf.jar --api /private/starfarer.api.jar --out /tmp/ST_1028_CALLSITES.json
python3 tools/audit_story_1028.py --obf /private/starfarer_obf.jar --api /private/starfarer.api.jar --out /tmp/ST_1028_STORY_AUDIT.json
```

## Nieukonczone prace przed 1.1

1. Przebudowa zwrotow z `Misc.STORY` i poprawna deklinacja polskich punktow fabularnych dla wszystkich 81 miejsc uzycia.
2. Poprawna odmiana pozostalych dynamicznych zaimkow (wczesniejszy audyt: 219 wywolan).
3. Dalsze brakujace krotkie etykiety w OBF i API, zwlaszcza wspoldzielone literały, ktore moga pelnic role kluczy.
4. Pelna recenzja znaczeniowa **3659** instalowanych wpisow API `DRAFT/OPTIONAL` (ich znaczniki i spacje byly sprawdzone automatycznie; znaczenie nie).
5. Rzeczywisty test instalatora i rozgrywki na Windows. CI na Linuxie nie potwierdza, czy wszystkie panele wygladaja poprawnie w grze.

**Wersja 1.0.28 jest robocza i nie jest finalna 1.1.**