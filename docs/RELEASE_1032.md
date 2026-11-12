# Starsector PL 1.0.32 — kolejny etap polonizacji 0.98a-RC8

**Nie jest to kompletna wersja 1.1.** Wydanie naprawia składanie angielsko-polskich podpowiedzi o zużyciu paliwa oraz błędy odmiany po zmiennych liczbowych. Nie zawiera oryginalnych komercyjnych bibliotek gry.

## Zmiany językowe

- **API: 6 nowych literałów i 25 korekt wcześniejszych tłumaczeń** w mapie `TLUMACZENIA_JAR_1032.csv`, bez zmian w danych gry i mapie OBF.
- Trzy klasy: `DurationAbilityWithCost2`, `EmergencyBurnAbility`, `FractureJumpAbility` składały podpowiedź z `Consumes %s light ` / `Jumping into hyperspace consumes %s light `, `year's` albo `years'` oraz ` worth of fuel...`. W wersji 1.0.31 pierwsza część była po polsku, dwie pozostałe mogły zawierać angielski i prowadzić do dwukrotnego podania jednostki.
- Obecna konstrukcja: `Zuzywa paliwo potrzebne do pokonania 1 roku swietlnego ...` oraz `Zuzywa paliwo potrzebne do pokonania 2 lat swietlnych ...` (odpowiednio ze zdaniem o obniżeniu gotowości bojowej lub bez niego). Dla skoku nadprzestrzennego stosowane jest `Skok w nadprzestrzen zuzywa...`.
- Pozostałe korekty: m.in. napisy kosztu bombardowania, awaryjnego dopalacza, zaopatrzenia i przewożonego ładunku. W kontekstach przyjmujących wartość 1 zapis `jednostek` zastąpiono neutralnym liczbowo `jedn.`. Poprawiono też wcześniej urwaną informację `Masz %s.` na `Masz %s jedn. paliwa.`.
- **Nie zmieniano** `Misc.STORY`, współdzielonych zaimków, identyfikatorów technicznych, nazw metod, instrukcji bajtkodu, zdarzeń i zasad gry.

## Mapa i testy na dostarczonych oryginałach

| Miara | Wynik |
|---|---:|
| OBF (bez zmian względem 1.0.31) | 3510 podmian / 538 klas |
| API mapa | 5225 wierszy (w tym 2 stare bez dopasowania) |
| API rzeczywiście zmodyfikowane literały | **5223** |
| Klasy API ze zmianami tekstu | **938** |
| Nowe literały API | **6** |
| Poprawione istniejące wpisy API | **25** |
| Odtworzone warianty podpowiedzi | **8** |
| Całe pliki `data/` względem 1.0.31 | **870/870 identyczne** |
| Testy negatywne map i bramek | **17 PASS** |
| Testy Go / go vet, trzy Windows x64 PE32+ | **PASS** |
| Aktualizacja spatchowanego 1.0.30 do 1.0.32 | **bajtowo identyczna ze świeżą instalacją** |
| Ponowna instalacja, przywracanie oryginału, odrzucenie uszkodzonego JAR | **PASS** |
| Gra uruchomiona na Windows | **NIE TESTOWANO** |

Weryfikator `tools/verify_1032.py` porównuje **wszystkie** klasy `starfarer.api.jar` w oryginale i wyniku instalacji. W 938 zmienionych klasach nie wykrył żadnej zmiany bajtów za pulą stałych ani żadnej zmiany istniejących wpisów puli innych niż `CONSTANT_String` (plus dołączenie nowych `CONSTANT_Utf8`). To dowód niezmienności wykonywalnych instrukcji, nie dowód jakości rozgrywki.

SHA oryginału API: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`. SHA API po patchu 1.0.32: `ae26c46473bd2557c7cccf4473e6bedc0e72ade05198c9465bf848ca84dac449`.

Minimalna paczka `Starsector_PL_ASCII_0.98a_RC8_1.0.32_MINIMALNY.zip`: **14 848 336 bajtów**, 873 wpisy (870 plików danych + `mod_info.json`, `CZYTAJ.txt`, instalator Windows x64), SHA-256 `22bb22b2775529fae4337c5518640d197df6e11a745a0d2587fdf35adc7c182e`, integralność ZIP potwierdzona. Bez oryginalnych JAR.

## Kontrola do 1.1

Historyczna grupa `DRAFT/OPTIONAL` to nadal **3658** pozycji. Oprócz 30 uprzednio zrecenzowanych offline zapisano **25** nowych recenzji korekt z odciskami SHA w `docs/API_SEMANTIC_REVIEW_1032.json`, zatem **55** pozycji ma dowody offline, a **3603** nadal nie mają takiej recenzji. Nie mylić tego z testem w grze: **3658** historycznych oraz **6** nowo dodanych literałów (**3664 łącznie w śledzonych grupach**) nie ma potwierdzonego testu wizualnego Windows.

Wciąż otwarte są: **81** wywołań `Misc.STORY`, **219** odnotowanych wywołań metod zaimków, pełna kontrola kompletności polonizacji i natywny test działania gry. Bramki w `docs/RELEASE_GATES_11.json` pozostają zablokowane. Nie nazywać tego wydania 1.1.

## Odtworzenie i testy

Po standardowych overlayach 1013..1031:

```bash
python3 tools/apply_1032.py worktree
python3 tools/verify_1032.py worktree
python3 tools/verify_review_1032.py --map worktree/buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1032.csv --old-ledger docs/API_SEMANTIC_REVIEW_1031.json --ledger docs/API_SEMANTIC_REVIEW_1032.json
python3 tools/check_release_gates_1032.py worktree --gates docs/RELEASE_GATES_11.json --prior-ledger docs/API_SEMANTIC_REVIEW_1031.json --ledger docs/API_SEMANTIC_REVIEW_1032.json
python3 tools/test_1032.py worktree
python3 tools/test_release_gates_1032.py worktree
(cd worktree && sh build_windows.sh)
python3 tools/package_1032.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.32_MINIMALNY.zip
```

**Dodatkowy prywatny dowód na oryginalnych JAR**, których nie wolno umieszczać w GitHubie: `python3 tools/verify_1032.py worktree --original /PRIVATE/starfarer.api.jar --patched /PRIVATE/patched_1032/starfarer.api.jar`.
