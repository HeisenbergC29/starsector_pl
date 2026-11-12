# Starsector PL 1.0.27 — polskie etykiety spotkań flot i handlu (2026-11-12)

**Gra:** Starsector 0.98a-RC8. **Docelowa pełna lokalizacja 1.1 wciąż nieukończona.**

## 71 rzeczywistych nowych tłumaczeń w Java

Dopisałem **41 par klasa–literał do OBF** i **30 do API**. Wcześniejsze tłumaczenia, pola techniczne, nazwy zmiennych, identyfikatory i wszystkie pliki `data/` pozostają niezmienione. Nowe napisy w plikach gry to polski ASCII.

| Zakres | JAR | Nowe literały |
|---|---|---:|
| Określenia wielkości jednostek i właściwości na panelu floty, m.in. `Cruiser` → `Krazownik`, `Frigate` → `Fregata` | OBF | 10 |
| Wskaźniki gospodarki `Deficit` → `Niedobor`, `Excess` → `Nadwyzka` | OBF | 5 |
| Opis agresji i dowodzenia | OBF | 2 |
| Ekran walki: `Allies` → `Sojusznicy`, `Opponents` → `Przeciwnicy`, `Deploy` → `Rozmiesc` | OBF | 6 |
| Etykiety umiejętności w tooltipie | OBF | 2 |
| Menu kolonii: `Cargo`, `Resources`, `Salvage`, `Trade`, `Uninhabited` | OBF | 5 |
| Nazwy rozkazów w rejestrze sterowania `Assault`, `Avoid`, `Defend`, `Retreat` itd. | OBF | 11 |
| Najazdy w MarketCMD: `Continue`, `Select`, `Spoils`, `Yes` | API | 4 |
| Spotkanie flot: `Disengage` → `Zerwij kontakt`, `Proceed` → `Kontynuuj`, `Salvaged` → `Odzyskano` itd. | API | 8 |
| Dialog osłony planetarnej | API | 1 |
| Statusy członkostwa w Lidze Perseańskiej i raport kolonii | API | 6 |
| Przerwanie ekspedycji karnej i przycisk zamknięcia misji zaopatrzenia | API | 2 |
| Dialogi punktów skoku, odzyskiwania, planet i misji barkowych | API | 9 |
| **Łącznie** | **OBF 41 + API 30** | **71** |

Każdy nowy angielski literał znaleziono w dokładnej puli stałych oryginalnej klasy i co najmniej jednym wywołaniu `ldc` w `javap`. W sumie było **140 takich odwołań** (57 OBF i 83 API) w **19 klasach** (7 OBF i 12 API).

Świadomie **odrzucono** angielskie napisy używane jako klucze sortowania, np. `Raid` w `getSortString` oraz `Procurement`, oraz identyfikatory/tagi `Military`, `Exploration`, `Missions`, `SHIP_ACCELERATE`, `CMENU_ASSAULT`. Nie dodano również podmian identycznych z oryginałem, np. `Status` → `Status`.

## Audyt i testy na oryginalnych JAR (Linux)

| Kontrola | Rezultat |
|---|---|
| OBF: **3421** dopasowanych podmian / **533** zmienione klasy | PASS |
| API: **5178** dopasowanych podmian / **936** zmienionych klas, 5180 wierszy mapy | PASS |
| Ścisłe porównanie `CONSTANT_String` wszystkich zmienionych klas, żadnych obcych zmian bajtkodu | PASS |
| OBF: poprawione manifesty dokładnie **533** zmienionych klas | PASS |
| Niezmienione wpisy bibliotek: **2394** OBF / **2604** API | PASS |
| Świeża instalacja obu patcherów na oryginalnych bibliotekach | PASS |
| Rzeczywista aktualizacja obu bibliotek spatchowanych **1.0.26 → 1.0.27** | PASS |
| Oba JAR po aktualizacji bajtowo identyczne ze świeżą instalacją | PASS |
| Ponowna instalacja bez nadpisywania (idempotencja) | PASS |
| Przywrócenie dokładnych oryginalnych JAR | PASS |
| Celowo zmodyfikowane oba oryginalne JAR: odmowa bez modyfikacji | PASS |
| **14/14** prób nieautoryzowanej zmiany map odrzucone przez testy | PASS |
| **1024** pliki źródłowe odtworzone bajtowo; 5 wygenerowanych binariów weryfikowanych osobno | PASS |
| **870/870** plików `data/` identycznych z 1.0.26 | PASS |
| `rules.csv`: **7371/7371** poprawnych opcji | PASS |
| Testy i `go vet` OBF/API/instalatora oraz kompilacja trzech Windows x64 PE32+ | PASS |
| ZIP: 873 elementy, 870 danych, test CRC, brak komercyjnych JAR | PASS |
| Natywne uruchomienie Windows i rozgrywka | **NIE WYKONANO** |
| Pełne ukończenie tłumaczenia 1.1 | **NIE POTWIERDZONO** |

**Oryginalne sumy SHA-256** OBF `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`; API `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.

**Wynikowe SHA-256** OBF `8d009ff086bc592b66fbb54b0e23ce11f3c2c85fb2a9ebb6c514c58515f1262d`; API `3b6a4cfb3911aa9564ea89c84e30b38931455f2d5c5e73f9a6e58eeb43e7d57d`.

**Pakiet:** `Starsector_PL_ASCII_0.98a_RC8_1.0.27_MINIMALNY.zip`, 13 619 202 bajtów, SHA-256 `a6fff38039ca06b8c7cd7461549787b1d91e38bbf9e1d9279636be9ec26730b3`. Archiwum i raport testów w prywatnej Bibliotece projektu; komercyjne JAR pozostają prywatne.

## Odtworzenie

```sh
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1027_ui.py worktree
python3 tools/test_1027_delta.py
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1027.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.27_MINIMALNY.zip
```

Z prywatnymi oryginalnymi bibliotekami i `javap`:

```sh
python3 tools/verify_1027_callsites.py --obf /private/starfarer_obf.jar --api /private/starfarer.api.jar --out /tmp/ST_1027_CALLSITES.json
```

## Nierozwiązane przed 1.1

- Kolejne krótkie etykiety wymagają sprawdzenia kontekstu bajtkodu i rzeczywistej widoczności.
- **81** odwołań do `Misc.STORY` w 24 klasach (65 OBF, 16 API) wymaga zmian składanych zdań zamiast jednej globalnej podmiany `story`.
- Pozostałe konteksty zaimków; starszy audyt znalazł **219** wywołań metod zaimkowych w 42 klasach.
- **3659** instalowanych wierszy `DRAFT/OPTIONAL` przeszło kontrolę znaczników, lecz nie pełną recenzję semantyczną.
- Należy wykonać test instalatora i uruchomionej gry na Windows. Zaliczenie CI i kontrola struktury JAR nie zastępują testu gameplay.

**Nie nazywać 1.0.27 kompletną 1.1.**