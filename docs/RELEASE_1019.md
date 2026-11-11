# Starsector PL 1.0.19 — wydanie robocze (2026-11-11)

**Starsector 0.98a-RC8. Cel 1.1 jeszcze nieukończony.**

## Naprawiono błędne składanie zdań w API

Klasa `com.fs.starfarer.api.impl.campaign.abilities.ToggleAbilityWithCost` składała angielskie czasowniki z pojedynczej litery i dalszego fragmentu: `C` + `onsumes`, `R` + `educes`. Poprzednia mapa tłumaczeń przekładała wyłącznie drugi fragment, w efekcie powstawały niepoprawne `Czuzywa` i `Rzmniejsza`.

Wersja 1.0.19 poprawia **8** istniejących tłumaczeń i dodaje **6** brakujących źródłowych literałów (`C`, ` c`, `R`, ` r`, `year's`, `years'`). Wszystkie zmiany są w klasie wyświetlającej dymki kosztu zdolności. Test Go scala dosłownie całe zdania i sprawdza osobno warianty dotyczące paliwa, gotowości bojowej oraz pojedynczego/wielu lat świetlnych. Nie zmieniono żadnego pola technicznego ani metody Java.

Mapa API: **5106 wierszy; 5104 rzeczywiste podmiany w 936 klasach.** Mapy i patcher OBF **bez zmian** względem 1.0.18 (3142 podmiany, 533 klasy). 870 plików danych bajtowo identycznych z 1.0.18.

## Testy na oryginalnych bibliotekach (Linux)

| Kontrola | Wynik |
|---|---|
| Obie oryginalne sumy SHA-256 dla 0.98a-RC8 | PASS |
| API 5104 podmiany, 936 zmienionych klas | PASS |
| OBF 3142 podmiany, 533 zmienione klasy (bez zmian względem 1.0.18) | PASS |
| Audyt pul stałych i bajtkodu: zmienione tylko zatwierdzone `CONSTANT_String` | PASS |
| OBF: 533 sum manifestu odpowiada 533 zmienionym klasom | PASS |
| Składanie sześciu wariantów tooltipu z aktualnych CSV — test Go | PASS |
| API świeża instalacja, ponowna instalacja (idempotencja) | PASS |
| API aktualizacja 1.0.18 → 1.0.19 równa świeżej instalacji (identyczny SHA) | PASS |
| Przywrócenie obydwu oryginalnych bibliotek bez zmian | PASS |
| Go test/vet: OBF/API/instalator i 3 Windows x64 PE32+ cross-build | PASS |
| 870 plików `data/` identycznych z 1.0.18 | PASS |
| `rules.csv` 7371/7371 poprawnych opcji | PASS |
| ZIP (873 elementy), CRC, brak oryginalnych JAR | PASS |
| Natywny test Windows i gry | NIE PRZEPROWADZONO |
| Kompletność 1.1 | NIE POTWIERDZONO |

Hash API po poprawkach: `997da797948e711886cddaa0759d46c9e9b01f58638f5ddcbc0dc0c2799ad52f`.
Hash OBF po poprawkach (bez zmian): `c95b45715e4d7c1b982d154acdc6776a3cf60756e83eefb00ea526a96c5a6c92`.

ZIP `Starsector_PL_ASCII_0.98a_RC8_1.0.19_MINIMALNY.zip`: **11 817 829 bajtów**; SHA-256 `5527ae27781f488341a340ee6a106c620f46b778e82c6c229b5e7690d39739fa`. Paczka i `Starsector_PL_1.0.19_TESTY.json` w prywatnej Bibliotece projektu.

## Dodatkowy audyt dynamicznych pól przed 1.1

Skrypt `tools/audit_dynamic_calls_1019.py` odczytał oryginalne JAR (sumy SHA zweryfikowane) i przeanalizował **94 klasy**. Wykrył **81** odwołań do `Misc.STORY` w **24 klasach** oraz **219** wywołań metod zaimkowych w **42 klasach** (79 `getHeOrShe`, 66 `getHisOrHer`, 41 `getManOrWoman`, 32 `getHimOrHer`, 1 `getHimOrHerself`). W odróżnieniu od starszego audytu uwzględnia `InterfaceMethod` i `Method`. Liczby dotyczą wywołań znalezionych w bajtkodzie, nie dowodzą że każde jest użyte w danej rozgrywce.

Raport ze szczegółowymi kontekstami `STORY_PRONOUN_CONTEXT_1019.json` znajduje się prywatnie w Bibliotece; kod audytu jest publiczny, lecz oryginalne JAR nie są i nie mogą zostać wrzucone na GitHub. Pozostałe zaimki i `Misc.STORY` nadal wymagają prawidłowej odmiany, a mapy `DRAFT` / `OPTIONAL` audytu semantycznego.

## Reprodukcja

```bash
python3 tools/restore_snapshot.py
python3 tools/apply_1013.py worktree
python3 tools/apply_1014.py worktree
python3 tools/apply_1015.py worktree
python3 tools/apply_1016.py worktree
python3 tools/apply_1017.py worktree
python3 tools/apply_1018.py worktree
python3 tools/apply_1019.py worktree
python3 tools/verify_1019_tooltip.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1019.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.19_MINIMALNY.zip
```

Ten stan nie jest pełnym wydaniem 1.1 ani testem uruchomionej gry.
