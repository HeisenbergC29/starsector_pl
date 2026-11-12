# Starsector PL ASCII 1.0.33 — lokalizacja 81 kontekstow punktow fabularnych

Data: 2026-11-12. Gra: Starsector **0.98a-RC8**. Docelowa polonizacja: **1.1, jeszcze nieukonczona**.

## Zmiany

- Wspolna wyswietlana stala `com.fs.starfarer.api.util.Misc.STORY`, ktorej oryginalna wartosc to `story`, otrzymala polski, nieodmienny skrot `PF` od **punktow fabularnych**.
- Audyt oryginalnych bibliotek wykazal **81** instrukcji odczytujacych te sama stala (`65 OBF + 16 API`) w **24** klasach. **69** bezposrednio nastepujacych angielskich koncowek ` point` / ` points` zostalo przetlumaczonych kontekstowo lub usunietych, aby nie pozostawaly konstrukcje `PF points`.
- Zmieniono rownoczesnie poprzednio przetlumaczone fragmenty sasiednie: dialogi punktow, opis korzystania z PF, zdolnosci elitarne, ulepszenia kolonii, trwale modyfikacje kadluba, odzyskiwanie okretow i samouczek. Dodatkowo poprawiono dwa niezgrabne zdania podczas koncowego przegladu: `Wydaj PF, aby podniesc umiejetnosc ...` oraz `Zdobyto 2 PF jako zwrot za wczesniejsze wydatki`.
- Mapa OBF: **3510 -> 3534** wiersze: **24 nowe**, **40 poprawionych**; po instalacji **3534** zmienione literały w **539** klasach.
- Mapa API: **5225 -> 5242** wiersze: **17 nowych**, **5 poprawionych**; w oryginalnym JAR API rzeczywiscie wystepuje **5240** podmian w **938** klasach (2 historyczne mapy bez odpowiednikow API).
- Wszystkie **870** plikow `mod/data/` sa bajtowo identyczne jak w 1.0.32. Nie zmieniono identyfikatorow, znacznikow, kodu gry ani reguł rozgrywki. Zrodla danych gry i oryginalne biblioteki komercyjne nie sa publikowane w repo.

## Przyklady zlozonych wynikow po korekcie

- `Punkty fabularne (PF) umozliwiaja wykonywanie wyjatkowych dzialan.`
- `Zmiana przydzialu umiejetnosci wymaga PF i nie zapewnia dodatkowego doswiadczenia.`
- `Wydaj PF, aby podniesc umiejetnosc do poziomu elitarnego`
- `Brak dostepnych PF`
- `Kazde ulepszenie w kolonii podwaja liczbe PF potrzebnych do kolejnego ulepszenia.`
- `Zdobyto 2 PF jako zwrot za wczesniejsze wydatki`
- `Masz %s PF.`

Dziesiec reprezentatywnych pelnych konstrukcji sklada i sprawdza `tools/verify_story_1033.py`. **Nie sa to zrzuty ekranu ani dowod przetestowania faktycznego rysowania przez silnik Windows**.

## Testy wykonane na oryginalnych prywatnych plikach gry

- SHA-256 oryginalnych bibliotek Starsector zweryfikowane z dokumentacja zrodel.
- Oryginalne i faktycznie spatchowane JAR porownane na poziomie wszystkich plikow i wszystkich klas: rozny jest tylko dozwolony `CONSTANT_String`, ewentualnie dopisany `CONSTANT_Utf8` oraz dozwolony manifest OBF; **zero zmian bajtowych wykonywalnej czesci klas**.
- Weryfikacja pelnego prywatnego rejestru: **81/81** odczytow `Misc.STORY`, **24/24** klasy, **69/69** bezposrednich koncowek liczby. Rowniez pomocniczy token techniczny `$story_critical` jest nienaruszony.
- Swieza instalacja OBF i API, *rzeczywista* aktualizacja ze spatchowanej 1.0.32, ponowna instalacja bez zmian, przywracanie obu oryginalnych bibliotek bajtowo: **PASS**.
- Celowo uszkodzone pliki JAR obu rodzajow sa odrzucane bez nadpisania: **PASS**.
- **14** negatywnych testow zabezpieczenia map i rejestru recenzji; **10** zlozonych konstrukcji w testach tekstowych: **PASS**.
- Testy Go `go test ./...`, `go vet ./...` we wszystkich trzech komponentach, kompilacja **3** EXE Windows PE32+ x64: **PASS**.
- **7371** opcji `data/campaign/rules.csv`: **0** blednych. **870** plikow danych bez zmian, paczka ZIP **873** wpisy, CRC **PASS**.

Oryginalne JAR SHA-256:

- OBF: `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`
- API: `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`

Spatchowane 1.0.33 SHA-256:

- OBF: `03729bc8e6ad0100ce4d0f7bf2f71bc198f917ff9e1b2fa5f9dacf4f35960a7a`
- API: `148f70c8bb45ef5d1e59c7ada1157766eb032e582bc12522b2e613e95a84839a`

Paczka gracza `Starsector_PL_ASCII_0.98a_RC8_1.0.33_MINIMALNY.zip`: **15191487 B**, SHA-256 `7dc561ffe9ad2f358efa49bc4d0a545cba2dc1582861906e72be998a3868d2ee`.

## Odtworzenie z publicznego GitHuba

```bash
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024 1025 1026 1027 1028 1029 1030 1031 1032 1033; do
    python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_story_1033.py worktree
python3 tools/verify_review_1033.py --map worktree/buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1033.csv --old-ledger docs/API_SEMANTIC_REVIEW_1032.json --ledger docs/API_SEMANTIC_REVIEW_1033.json
python3 tools/test_story_1033.py worktree --old-ledger docs/API_SEMANTIC_REVIEW_1032.json --ledger docs/API_SEMANTIC_REVIEW_1033.json --gates docs/RELEASE_GATES_11.json
python3 tools/check_release_gates_1033.py worktree --gates docs/RELEASE_GATES_11.json --prior-ledger docs/API_SEMANTIC_REVIEW_1032.json --ledger docs/API_SEMANTIC_REVIEW_1033.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1033.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.33_MINIMALNY.zip
```

Pelne porownanie klas i wszystkich 81 kontekstow wymaga *prywatnych oryginalnych bibliotek i raportu odczytow JVM*, ktory pozostaje poza repo; opcjonalne argumenty `--obf-orig`, `--api-orig`, `--obf-patched`, `--api-patched`, `--callsite-report` w `tools/verify_story_1033.py`.

## Stan do docelowej 1.1 — otwarte

1. `Misc.STORY`: **81 miejsc ma poprawki i zostalo zweryfikowanych offline**, ale wciaz **81 do kontroli wizualnej w grze Windows**. Bramki 1.1 nie zamknieto.
2. **219** wywolan metod zaimkowych, w tym kolizja `her` we wspolnej puli stalych, nadal wymaga pelnej recenzji i poprawy.
3. **3600** wczesniejszych tlumaczen API nadal bez recenzji jezykowej offline, **3681** historycznych/nowych w sledzonych grupach bez testu w grze. Rejestr ma **58** zaakceptowanych offline pozycji.
4. Pelna niezalezna kontrola wszystkich widocznych tekstow oraz **natywny test rozgrywki na Windows** nie zostaly wykonane.

**Nie oznaczac wydania jako 1.1.** Techniczne CI Linux i kompilacja EXE nie potwierdzaja braku bledow w dzialajacej grze.
