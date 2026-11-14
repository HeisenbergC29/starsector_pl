# Starsector PL ASCII 1.0.66 — symulator walki, przemysl kolonii i samouczek

**Gra:** Starsector 0.98a-RC8. **System instalatora:** Windows x64. **Docelowe 1.1: NIEUKONCZONE.**

## Zmiany widoczne dla gracza

Na podstawie oryginalnego `starfarer.api.jar` zrecenzowano trzy duze klasy interfejsu, a nie tylko ciagi z arkusza tlumaczen:

| Klasa Java API | Historyczne wpisy robocze sprawdzone | Wczesniej zliczone | Nowe historyczne recenzje | Dodatkowe brakujace tlumaczenia |
| --- | ---: | ---: | ---: | ---: |
| `com.fs.starfarer.api.impl.SimulatorPluginImpl` | 58 | 0 | **58** | 2 |
| `com.fs.starfarer.api.impl.campaign.econ.impl.BaseIndustry` | 56 | 46 | **10** | 7 |
| `com.fs.starfarer.api.impl.campaign.tutorial.TutorialMissionIntel` | 47 | 1 | **46** | 4 |
| **Suma** | **161** | **47** | **114** | **13** |

Dodatkowo poprawiono **9** istniejacych polskich fragmentow, z czego siedem dotyczy produkcji i budowy przemyslu kolonii, a dwa komend wyroznianych w samouczku. Wszystkie nowe podmiany ograniczono do konkretnej klasy, bez globalnej zmiany slow takich jak `day`, `units`, `Story` lub `default`.

### Symulator: 2 nowe naglowki

- `Aggression / behavior` → `Agresja i zachowanie`.
- `DevMode stuff` → `Opcje deweloperskie` (sekcja widoczna w trybie deweloperskim).

Utrzymano dotychczasowe nazwy techniczne opcji konfiguracyjnych: `behavior_aggressive`, `officers_none`, `quality_high`, `cat_default`, itp.; nie sa to teksty dla gracza.

### Panel przemyslu: brakujace jednostki i skladanie zdan

Przywrócono kompletne polskie opisy z oryginalnych, faktycznie wykonywanych instrukcji `ldc`:

- `day`/`days` → `dzien`/`dni` (odpowiednio dla 1 i wielu dni; numery 1, 2, 5, 12, 21).
- `unit`/`units` → `jedn` w kluczowych skladanych opisach produkcji, z koncowa kropka dostarczana przez oryginalny kod (wynik `5 jedn.`, nie `5 jedn..`).
- ` left` → pusty fragment; naprawiono prefixy czasu (`Budowa, pozostalo: 5 dni`, `Ulepszanie, pozostalo: 1 dzien`, `Zaklocenia, pozostalo: 2 dni`).
- `%s and %s ` → `Koszt: %s; czas: %s `, a dwa zakonczenia `to build`/`to upgrade` na `. Dostepne srodki: %s.`. Otrzymujemy `Koszt: 5000; czas: 5 dni. Dostepne srodki: 2500.`
- `Requires %s more ` + dni + ` to finish building.` → `Pozostaly czas: 5 dni.`
- ` at ` → ` - kolonia: ` w powiadomieniach o budowie, np. `Rafineria - kolonia: Jangala`, zamiast wymuszania odmiany nazwy kolonii.

Zachowano cyfrowe znaczniki `%s`, `%d` i nazwy technicznych towarow/identyfikatorow. Nie zmieniano wartosci rozgrywki.

### Samouczek Galatii: instrukcje i wyroznienia

- `Completed` → `Ukonczono` w raporcie misji.
- `Go Dark` → `trybu skrytego`, `Emergency Burn` → `awaryjnego dopalacza`, by skladane zdanie zawieralo poprawna odmiane: `Uzyj trybu skrytego, aby uniknac wykrycia, a awaryjnego dopalacza, aby uciec, jesli zostaniesz zauwazony.`
- `Active Sensor Burst` → `aktywnego impulsu czujnikow` po konstrukcji `uzyj`.
- Wyroznienia `"Storage"` → `"Magazyn"` i `"autofit"` → `"automatyczne dopasowanie"`; pierwszy termin pasuje teraz do przetlumaczonej tresci akapitu.
- Klucz `Story` jest dodawany przez `Set.add()` do kategorii informacji i **pozostaje technicznie niezmieniony**, podobnie jak identyfikatory questow, lokacji i skryptow.

**Uwaga:** instalator i teksty Java pozostaja w ASCII do czasu ustalenia zgodnosci polskich znakow z silnikiem.

## Oryginalny JVM, bez naruszania kodu gry

Oryginalny `starfarer.api.jar` ma SHA-256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.

- W trzech klasach potwierdzono **669 wykonywanych odczytow `ldc/ldc_w`** (272 symulator, 188 przemysl, 209 samouczek).
- Liczba unikatowych oryginalnych tekstow w tych klasach: 204 + 118 + 147 = **469**, z czego po tej partii mapa obsluguje **205** (76 + 77 + 52). Nie kazdy pozostaly oryginalny tekst jest przeznaczony do wyswietlenia; wiele to ID i znaczniki techniczne.
- Mapa API: **5314 → 5327** wierszy; 13 nowych mapowan i 9 poprawek wartosci. Mapa OBF **bez zmian**. Wszystkie **870** plikow danych gry (w tym `rules.csv`) pozostaja bajtowo identyczne.
- Prywatne oryginalne JAR: **fresh 1.0.66 == upgrade 1.0.65 → 1.0.66**, dokladnie trzy zmienione pliki `.class`, wszystkie offsety i opcode JVM niezmienione, ponowna instalacja no-op, restore do oryginalnych JAR, odmowa instalacji na naruszonym JAR — **PASS**. Nie publikuje sie oryginalnych komercyjnych JAR.
- Zweryfikowano 60 dynamicznie skladanych tekstow, 16 odrzuconych zlych mutacji mapy oraz 7 odrzuconych falszywych stanow dystrybucji. `go test`, `go vet`, kompilacja trzech EXE Windows x64, 7371 opcji dialogowych (0 bledow), CRC ZIP 873 wpisy — **PASS**.

## Historyczne recenzje — brak podwojnego liczenia

Stan w 1.0.65: **617/3658**. W `BaseIndustry` 46 wpisow nadal mialo status `DRAFT/OPTIONAL`, ale zostaly juz ujete we wczesniejszych audytach (`docs/API_SEMANTIC_REVIEW_1065.json`). Dodatkowo 1 stary wpis `TutorialMissionIntel` (`Recover at least %s ships at Tetra`) nadal mial status DRAFT, mimo ze juz figurowal w rejestrze. Doliczono tylko 58 + 10 + 46 = **114** unikatowych historycznych recenzji. Nowy stan: **731/3658**, pozostaje **2927**.

Rejestr jest append-only: wszystkie 617 poprzednich odciskow zachowuje w tej samej kolejnosci; nowe 114 ma wlasne `source_class`, `english_key_sha256` i `row_sha256`. **13 dopisanych brakujacych literalow nie zwieksza licznika historii** (nie nalezaly do 3658 oryginalnych wpisow roboczych).

## Cel 1.1 i testy

Zgodnie z decyzja uzytkownika z 14.11.2026 **testowanie uruchomionej gry i przeglad wizualny odbeda sie dopiero po wydaniu 1.1**. Nie sa przedwydaniowym warunkiem 1.1, a ich status nie moze byc oznaczany jako wykonany. Automatyczny audyt tresci, integralnosci kodu, paczki i instalatora pozostaje obowiazkowy przed wydaniem. Do pelnej 1.1 pozostaja m.in. 2927 historycznych wpisow API, 186 kontekstow getterow, 1953 dynamicznych znacznikow plci w 1006 dialogach oraz ocena wszystkich widocznych tekstow i skrotow.

## Odtwarzanie z GitHuba

Po odtworzeniu snapshotu 1.0.12 i nakladek do 1.0.65:

```sh
python3 tools/apply_1066.py worktree
python3 tools/verify_1066.py worktree
python3 tools/test_1066.py worktree
python3 tools/test_package_contract_1066.py worktree
python3 tools/build_review_1066.py worktree --record docs/SIM_INDUSTRY_TUTORIAL_REVIEW_1066.json --previous docs/API_SEMANTIC_REVIEW_1065.json --ledger docs/API_SEMANTIC_REVIEW_1066.json
python3 tools/check_release_gates_1066.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1065.json --prior-semantic docs/API_SEMANTIC_REVIEW_1065.json --semantic docs/API_SEMANTIC_REVIEW_1066.json
sh worktree/build_windows.sh
python3 tools/package_1066.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.66_MINIMALNY.zip
```

Zewnetrznie, tylko lokalnie z oryginalnymi JAR-ami: `python3 tools/audit_original_jvm_1066.py --jar PRIVATE/starfarer.api.jar --worktree worktree`; `python3 tools/private_upgrade_1066.py --jars PRIVATE/starsector-core --worktree worktree`.
