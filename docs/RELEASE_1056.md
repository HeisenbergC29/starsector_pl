# Starsector PL ASCII 1.0.56 — neutralizacja 110 tekstow dialogowych

**Gra:** Starsector 0.98a-RC8. **Status:** instalator Windows x64 z GitHub Actions, testy JVM i CSV offline. **1.1 NIE GOTOWA.**

## Co zmieniono

Poprawiono **110 dokladnie zidentyfikowanych rekordow `data/campaign/rules.csv`** z oryginalnych 11 107. W kazdym usunieto jedno niepotrzebne wywolanie zmiennej plciowej; zmieniono **wylacznie pole `text`**. Nazwy i identyfikatory rekordow, `trigger`, `conditions`, `script`, `options` i `notes` oraz wszystkie 869 innych plikow danych zostaly bajtowo nienaruszone.

- **71** krotkich wtracen narracyjnych `mowi $heOrShe` / `odpowiada $heOrShe`: naturalny polski czasownik trzecioosobowy bez zbednego zaimka podmiotu. Przyklad: `"Nie", mowi $heOrShe.` -> `"Nie", mowi.`
- **39** zatwierdzonych neutralizacji formy dzierzawczej `$hisOrHer`, m.in. `znad $hisOrHer konsoli` -> `znad konsoli`, `Pirat przybiera $hisOrHer najlepszy usmiech` -> `Pirat przybiera swoj najlepszy usmiech`, `na $hisOrHer czole drzy pot` -> `na czole drzy kropla potu`.

Pelny wykaz zawiera **110 identyfikatorow, oryginalne i poprawione cale pola tekstowe, zarejestrowane podmiany oraz SHA-256 kazdego pola**: `docs/RULES_NEUTRAL_REVIEW_1056.json`. Dwa poczatkowo wytypowane rekordy wystepowaly juz w historycznych recenzjach; wykluczono je z tej partii. Nowa lista nie pokrywa sie z **253 wczesniej recenzowanymi rekordami**.

## Pelny licznik problematycznych znacznikow

| Stan | 1.0.55 | 1.0.56 | Zmiana |
| --- | ---: | ---: | ---: |
| Dialogi zawierajace surowe zmienne plciowe | 1139 | 1029 | -110 |
| Wystapienia takich zmiennych | 2275 | 2165 | -110 |
| Rekordy tekstowe poddane recenzji offline | 253 | 363 | +110 |
| Historyczne literalne API recenzowane offline | 391/3658 | 391/3658 | 0 |
| Nierozpatrzone gettery Java | 186 | 186 | 0 |

Zaznaczamy, ze pozostale surowe znaczniki **nie sa dowodem kazdorazowego blednego tekstu w grze**. Ich znaczenie i ewentualna polska forma musi byc sprawdzona kontekstowo. Nie oznaczono ich automatycznie jako nieprzetlumaczonych.

## Ochrona formatu i kodu

Oryginalny `rules.csv` zawiera zroznicowane kodowanie cytowanych pol oraz ostatni rekord bez finalnego LF. Patcher przepisuje **jedynie pola tekstowe na poziomie oryginalnych bajtow rekordu CSV**. Nie serializuje ponownie calej tabeli. Walidator odwraca w 110 rekordach dokladnie zatwierdzone zmiany i odtwarza pierwotny plik **bajtowo**, o SHA-256 `e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a`. Nowy SHA-256 `a08330e67de037fc0df66447c039ec7ac6792340405d2983c04e31f2bfef4810`. Plik nadal ma 11 107 rekordow. Dodatkowo porownano SHA-256 wszystkich **869 niezmienionych plikow `data/`**.

Mapy i bajtkod Java API/OBF **bez zmian**: API 5298 wierszy (5296 rzeczywistych podmian w 938 klasach), OBF 3537 podmian w 539 klasach. Zaktualizowano numer binarnego patchera API do 1.0.56, kopiujac mape 1.0.55 **bez zadnej zmiany**, tak aby system rozpoznawal poprzednia instalacje. W mapach nie tlumaczono technicznych identyfikatorow.

### Test oryginalnych JAR-ow (prywatnie)

Oba oryginalne JAR-y 0.98a-RC8 zostaly sprawdzone przez rzeczywiste binarne patchery Go. Swieza instalacja = aktualizacja 1.0.55 -> 1.0.56; powtorne zastosowanie jest idempotentne; modyfikowany/uszkodzony JAR zostal odrzucony bez nadpisania; restore odtworzyl dokladnie oryginalne SHA. Patcher API produkuje identyczny JAR jak w 1.0.55 (SHA-256 `57004e66715ce8ccaec236a85d73961290cb4ebbbdc0282abd12a31c9b0c6be8`); OBF pozostaje o SHA `85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1`. Oryginalnych komercyjnych JAR-ow **nie ma** w repozytorium ani paczce dystrybucyjnej. Raport: `docs/PRIVATE_UPGRADE_1056.json`.

Testy zapisu CSV: 10 negatywnych mutacji planu/oryginalu. Testy kontraktu instalatora: 4 negatywne przypadki. Bramki 1.1 odrzucaja 10 sztucznych statusow ukonczenia.

## Reprodukcja

W repozytorium odtworzyc bazowy snapshot 1.0.12 i zastosowac kolejno overlaye 1013–1055, a nastepnie:

```bash
python3 tools/apply_1056.py worktree
python3 tools/verify_1056.py worktree
python3 tools/test_1056.py worktree
python3 tools/test_package_contract_1056.py worktree
python3 tools/check_release_gates_1056.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1055.json
python3 tools/test_release_gates_1056.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1055.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1056.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.56_MINIMALNY.zip
```

## Co pozostaje otwarte

Przede wszystkim **1029 dialogow z 2165 surowymi potencjalnie problematycznymi zmiennymi plciowymi**, **3267 historycznych wpisow API** do recenzji, **186 nierozpatrzonych getterow Java** i **brak testow w faktycznie uruchomionej grze na Windows**. Wydanie 1.0.56 jest etapem technicznym, **nie stanowi ukonczonej wersji 1.1**.
