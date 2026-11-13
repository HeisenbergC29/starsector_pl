# Starsector PL ASCII 1.0.50 — wspolne polskie jednostki czasu w interfejsie

**Data:** 2026-11-13  
**Gra:** Starsector 0.98a-RC8  
**Baza:** 1.0.49, SHA mapy `3ae9e6c3e8675139a9aa3bc91ca88f32fc2b65301f5b7657e8936c85d81c5420`.  
**Nowa mapa:** 5269 pozycji, SHA-256 `d2f6b355c58a8d2f0c9a5674e19bcaf7e24862ac4a3c28ad6ace97ce0024b41e`.

**Wersja 1.1 w opracowaniu; wydanie 1.0.50 to zweryfikowana poprawka offline, NIE pelna polonizacja gry.**

## Osiem nowych przekladow z oryginalnej Java API

W klasie `com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin` na oryginalnym JAR wystepuje osiem wspolnych literalow uzywanych **17 razy przez instrukcje `ldc_w`**. Metody klasy tworza widoczne teksty czasu, a `getDaysString()` zwraca `day` lub `days` rowniez dla innych komunikatow, np. `PromoteOfficerIntel`. Wczesniej te fragmenty pozostawaly angielskie mimo polskich fragmentow okalajacych.

| Angielski literal | Polski ASCII | Wywolan `ldc_w` |
| --- | --- | ---: |
| `day` | `dzien` | 4 |
| `days` | `dni` | 4 |
| `month` | `mies.` | 2 |
| `months` | `mies.` | 2 |
| `cycle` | `cyk.` | 1 |
| `cycles` | `cyk.` | 1 |
| ` and ` | ` i ` | 2 |
| ` ago.` | ` temu.` | 1 |

**Liczby:** `1 dzien`, `2 dni`, `5 dni` sa gramatycznie poprawne. `mies.` oraz `cyk.` to niezalezne od liczby skroty. Dla przykladu po zlozeniu literalow `Dodano wpis do dziennika 2 mies. i 1 dzien temu.`. Komunikat o awansie oficera sklada sie z oryginalnego API `getDaysString()` i uzyskuje `... przez 1 dzien.` lub `... przez 2 dni.` bez podwojnej kropki.

Wszystkie tlumaczenia ograniczono do **jednej oryginalnej klasy**, zachowujac inne znaczenia `day`, `and`, `cycle` w pozostalych klasach i identyfikatorach gry. Nie wprowadzono zmian instrukcji metod JVM. Szczegolowe indeksy oryginalnej puli stalych i liczba wystapien: `docs/API_TIME_COMPONENTS_1050.json` oraz `docs/JVM_AUDIT_1050.json`.

## Recenzja 60 historycznych tekstow API

Sprawdzono i zakotwiczono na oryginalnych `CONSTANT_String` **60 dalszych wpisow DRAFT/OPTIONAL**, wybranych z obszarow zarzadzania kolonia, rajdow i dziennika floty:

- 42 ze wspolnego UI `BaseIndustry` (produkcja, budowa, RDZEN SI, utrzymanie, zaburzenia i komunikaty obiektow);
- 13 z `MarketCMD` (rajdy, obrona kolonii, konsekwencje dzialan);
- 5 z `BaseIntelPlugin` (dziennik floty i rejestrowanie czasu).

Rejestr `docs/API_STATIC_UI_REVIEW_1050.json` zawiera oryginalny tekst, polska wersje, klasę, status, fingerprint SHA i dowod odnalezienia w oryginalnej klasie. Wcześniejszych 252 recenzji nie zmieniono. **Lacznie 312/3658 wpisow historycznych sprawdzono offline, 3346 nadal wymaga recenzji.** Potwierdzenie w puli stalych i przeglad tlumaczenia nie jest rownowazny z testem wizualnym w uruchomionej grze.

## Weryfikacja techniczna

- Oryginalny `starfarer.api.jar` 0.98a-RC8 SHA-256: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- Zweryfikowano wszystkie 8 nowo lokalizowanych literalow i ich 17 oryginalnych `ldc_w` oraz 60 historycznych tekstow w oryginalnej puli stalych JVM.
- W stosunku do 1.0.49 zmienila sie **jedna klasa**: `BaseIntelPlugin`. Porownanie metod wykazuje **zero zmian wykonywalnego kodu Java**.
- **5267 faktycznych podmian API w 938 klasach**; OBF bez zmian.
- Nowe 8 wierszy mapy bez modyfikacji poprzednich 5261, zachowane angielskie klucze, statusy, ASCII i format CSV CRLF.
- Wszystkie 870 plikow `data/` bajtowo bez zmian; kod i format opcji dialogow nietkniete.
- Symulacje: 9 kombinacji liczba/jednostka, 3 daty zlozone, 3 zdania o awansie oficera; 8 celowych mutacji mapy oraz 8 celowo sfalszowanych bramek wydania 1.1 zostaly odrzucone.
- Realne uruchomienie patchera Go na oryginalnych komercyjnych JAR: **fresh = upgrade 1.0.49 -> 1.0.50**, ponowne zastosowanie bez zmian, odmowa uszkodzonego ZIP i przywrocenie oryginalu PASS. Wynik API SHA-256 `35e086aed9380cf481bd6e48bfc29017cb5ee94012e5292953c9d53e44a540df`.
- Narzedzia i raporty przeznaczone do GitHub Actions: `tools/apply_1050.py`, `tools/verify_1050.py`, `tools/test_1050.py`, `tools/verify_review_1050.py`, `tools/check_release_gates_1050.py`, `tools/test_release_gates_1050.py`, `tools/package_1050.py`. Raport prywatnego testu: `docs/PRIVATE_UPGRADE_1050.json`. Oryginalne komercyjne JAR nie sa publikowane.

## Reprodukcja

Z repo odtworz snapshot 1.0.12 i kolejno overlaye `tools/apply_1013.py` ... `tools/apply_1049.py`, a nastepnie:

```bash
python3 tools/apply_1050.py worktree
python3 tools/verify_1050.py worktree
python3 tools/test_1050.py worktree
python3 tools/verify_review_1050.py worktree --previous docs/API_SEMANTIC_REVIEW_1049.json --ledger docs/API_SEMANTIC_REVIEW_1050.json
python3 tools/check_release_gates_1050.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1049.json --ledger docs/API_SEMANTIC_REVIEW_1050.json
python3 tools/test_release_gates_1050.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1049.json --ledger docs/API_SEMANTIC_REVIEW_1050.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1050.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.50_MINIMALNY.zip
```

## Nierozwiazane warunki docelowej wersji 1.1

**3346** historycznych wpisow API bez recenzji semantycznej, **186** nierozpatrzonych getter-callsite Java i wspolna stala `her` w `BaseBarEventWithPerson`, co najmniej 2275 potencjalnie problematycznych wystapien dynamicznych zaimkow w 1139 rekordach `rules.csv` (nie wszystkie sa potwierdzonymi bledami). Osobno wymagana jest weryfikacja `FactionPersonalityPickerPluginImpl`, gdzie identyfikatory techniczne cech oficerow moga pojawiac sie w opisach UI. Brakuje pelnego audytu wszystkich tekstow i **natywnej rozgrywki Windows**.

**Nie oznaczac 1.0.50 jako 1.1.**
