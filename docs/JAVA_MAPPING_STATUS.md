# Znaczenie statusow w mapach Java (audyt 2026-11-11)

Patchery OBF i API **nie odczytuja kolumny `status` jako filtra instalacji**. Kazda poprawna para `source_class` + `english_literal` + `polish_ascii_draft` trafia do mapy podmian. Dokladne dopasowanie do oryginalnych `CONSTANT_String`:

- OBF: 3116 / 3116 wpisow, w tym 1590 oznaczonych `REVIEWED_OBF_PATCH_EXPERIMENTAL`.
- API: 5040 / 5042 wpisow, w tym **1012** faktycznie stosowanych z etykieta `DRAFT_ONLY_NOT_INSTALLED`; **2301** `OPTIONAL_PATCHER_NOT_GAME_TESTED` oraz **356** `DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME`.

Etykiety sa HISTORYCZNYMI informacjami o stopniu recenzji, **nie sa dowodem ze wpis nie zostal zainstalowany**. Dopasowanie literału w klasie nie dowodzi jeszcze, ze tekst jest wyswietlany; moze to byc ciag techniczny. Nie nalezy usuwac calych grup statusow bez recenzji, bo cofneloby to istotne tlumaczenia.

Reprodukcja z prywatnymi oryginalnymi JAR:
```sh
python3 tools/restore_snapshot.py
python3 tools/audit_jar_mappings.py \
  --obf-jar /sciezka/starfarer_obf.jar \
  --api-jar /sciezka/starfarer.api.jar \
  --obf-csv worktree/buildtools/NARZEDZIA_OBF/TLUMACZENIA_OBF_10109.csv \
  --api-csv worktree/buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1010.csv
```
Wynik szczegolowy: `docs/MAP_STATUS_1011.json`. Skrypt wymaga zgodnosci sum SHA-256 oryginalnych JAR. **Do 1.1 wymagany przeglad znaczenia i kontekstu tych literałów**, a nie tylko przeliczanie wierszy.
