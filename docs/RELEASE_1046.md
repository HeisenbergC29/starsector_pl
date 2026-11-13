# Starsector PL ASCII 1.0.46 — dynamiczne teksty Java API i recenzja 20 tlumaczen

**Data:** 13.11.2026  
**Gra:** Starsector 0.98a-RC8  
**Baza:** 1.0.45, ostatnie Java API 1.0.42  
**Stan:** robocze wydanie tlumaczenia, NIE pelna wersja 1.1.

## Faktyczne zmiany

Nowy overlay `tools/apply_1046.py` poprawia **13** istniejacych spolszczen i dodaje **3** wczesniej nieobjete mapa literały z 8 klas Java API. OBF, wszystkie 870 plikow `data/`, reguly dialogow i techniczne identyfikatory pozostaja niezmienione. Nie edytowano wykonywalnych instrukcji metod Java.

- `PiracyRespiteScript`: usunieto bledne znaczenie *Lasts for* -> *Pozostalo*; nowa etykieta **Czas trwania (dni): %s**. Premia kolonii dostaje etykiete **Premia do dostepnosci kolonii: %s**, odporna na wartosci liczbowe.
- `InterdictionPulseAbility`, `MissileAutoloader`, `CrewTraining$Level2` i `PhaseCorps$Level3`: niepoprawne stale odmiany *%s sekund* oraz *%s sekunde* zastapione spojnymi jednostkami **%s s** w pelnych zdaniach i opisach. Zachowana liczba oraz kolejnosc wszystkich placeholderow.
- `GalatianAcademyStipend`: dynamiczna liczba miesiecy ma postac **%s mies.** zamiast stalej liczby mnogiej.
- `AbandonMarketPluginImpl`: zmieniono komunikaty o porzucaniu kolonii i saldzie na gramatycznie niezalezne od liczby; poprawiono takze budowany dynamicznie bilans zysku/kosztu.
- `DoCanAffordCheck$1`: etykiety dostepnych kredytow sa poprawne takze dla wartosci 1.
- `MissileAutoloader`: **POZOSTALY ZAPAS** zamiast nieprecyzyjnego **POZOSTALA POJEMNOSC** w informacji o limitowanych przeladowaniach.

### Istotny blad skladania bilansu kolonii

`AbandonMarketPluginImpl.createConfirmationPrompt` buduje zdanie z trzech fragmentow i rozgalezienia:

1. Dlugie zdanie podsumowujace koszty ewakuacji i przychod z zakladow.
2. Literal `cost` albo `payout`, zależnie od wyniku finansowego.
3. Sufiks ` of %s.`.

W 1.0.45 spolszczono wylacznie pierwszy fragment, pozostawiajac w wyniku angielskie `cost/payout` i `of`. W 1.0.46 trzy nowe mapowania o **dokladnie tym jednym zakresie klasowym** to `cost` -> `koszt`, `payout` -> `zysk`, ` of %s.` -> ` %s.`. Otrzymujemy dwa warianty: `Bilans: koszt 1.` / `Bilans: zysk 1.` i analogicznie przy pozostalych wartosciach. W oryginalnym `javap -c -p` wszystkie trzy `ldc` sa uzywane w tym samym `StringBuilder` w `createConfirmationPrompt`, nie w warunkach, ID ani logice gry. Skladanie obu wariantow jest testowane syntetycznie.

### Mapa i weryfikacja statyczna

- `TLUMACZENIA_JAR_1042.csv` — SHA-256 `abaa3521fb8906e9686603ea38252cde5e4b00745761ccb11a7588a410bbb9e9`, 5257 rekordow.
- `TLUMACZENIA_JAR_1046.csv` — SHA-256 `8c09fa12c41199e92008551cf89e86a30e59329531ad6ba40731c9d697a73a93`, 5260 rekordow (13 poprawek i 3 nowe).
- Prywatny oryginal `starfarer.api.jar` 0.98a-RC8 — SHA-256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- `tools/audit_1046_jvm.py` w niezaleznym od patchera odczycie `CONSTANT_String` potwierdzil **16/16** oryginalnych literałów w **8** klasach. Nie wykorzystuje tekstowych escape'ow `javap`; pelne biblioteki gry nie sa publikowane.
- `tools/verify_1046.py` potwierdzil tylko uzgodnione zmiany polskich pol mapy: **angielskie klucze, klasy, statusy i wszystkie 5257 starszych wpisow zachowano**. W odrębnym pliku mapy nowe trzy literały maja jawną etykiete `VERIFIED_COMPOSED_ABANDON_TOOLTIP_1046`.
- Test `tools/test_1046.py`: odtworzono 1.0.42 mape bajt w bajt; sprawdzono **39** sztucznych przypadkow liczb (1, 2 i 5) i **8** celowo nieautoryzowanych mutacji, wszystkie odrzucone. Dwa warianty dynamicznego bilansu zweryfikowane jako pelne skladane zdania.
- Sumy 1.0.45 danych bez zmian: `rules.csv` `e9a6ad60da0caca6fa89af21370eddfa461de39324486368458aca2575e3b64a`; 869 innych plikow w drzewie `5bfda6c69b2f83e3913fa4e1475c6288e1f3a0d82914fd007abba381e8da0fc1`. Porownanie z paczka 1.0.45 bajt po bajcie: PASS offline.

### Rejestr recenzji starszych DRAFT/OPTIONAL

`docs/API_SEMANTIC_REVIEW_1046.json` zachowuje **122** wczesniejsze zatwierdzone pozycje, a do nich dopisuje **20** nowych, recenzowanych na poziomie oryginalnego tekstu, kontekstu klasy i nowego polskiego zdania (przede wszystkim `PiracyRespiteScript`, `AbandonMarketPluginImpl`, `GalatianAcademyStipend`, umiejetnosci i etykiety zapasow rakietowych). Wszystkie 20 ma potwierdzone oryginalne literały JVM; zaden z 122 starych wpisow nie zostal policzony ponownie. **142/3658** recenzowanych offline, **3516** do przegladu; statusy DRAFT w samym CSV sa nadal historyczne i nie steruja instalacja patchera. To nie jest audyt calosci ani runtime Windows.

### Odtworzenie z repozytorium

Po `python3 tools/restore_snapshot.py` i nakladkach `tools/apply_1013.py`–`tools/apply_1045.py` w kolejnosci:

```bash
python3 tools/apply_1046.py worktree
python3 tools/verify_1046.py worktree
python3 tools/test_1046.py worktree
python3 tools/verify_review_1046.py worktree --previous docs/API_SEMANTIC_REVIEW_1040.json --ledger docs/API_SEMANTIC_REVIEW_1046.json
python3 tools/check_release_gates_1046.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1040.json --ledger docs/API_SEMANTIC_REVIEW_1046.json
python3 tools/test_release_gates_1046.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/API_SEMANTIC_REVIEW_1040.json --ledger docs/API_SEMANTIC_REVIEW_1046.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1046.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.46_MINIMALNY.zip
```

Z prywatnymi oryginalnymi JAR na komputerze wlasciciela:

```bash
python3 tools/audit_1046_jvm.py --original-api /private/starfarer.api.jar
python3 tools/verify_1046.py worktree --original-api /private/starfarer.api.jar
```

Build na GitHubie nie zawiera oryginalnych komercyjnych JAR. Sam cross-build Windows nie jest testem uruchomionej gry.

### Nadal otwarte do 1.1

- 186 nierozpatrzonych kontekstowo wywolan getterow zaimkowych Java, zwlaszcza wspolny literal `her` (#143).
- 3516 starszych tekstow API bez pelnej recenzji; 16 poprawionych/nowych tekstow 1.0.46 nadal do kontroli w grze.
- 253 skorygowane w poprzednich etapach wiersze dialogow oraz 81 tekstow `PF`, 77 ilosci i 15 interpunkcji do natywnego UI Windows.
- Brak pelnego audytu tekstow widocznych w grze i brak natywnej rozgrywki Windows; **nie wydawac jako 1.1**.
