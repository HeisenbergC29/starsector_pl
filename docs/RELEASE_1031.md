# Starsector PL 1.0.31 (0.98a-RC8) — wydanie robocze w drodze do 1.1

**Nie jest to gotowa 1.1.** Ten etap naprawia jedna konkretna niepoprawna polska odmiane i weryfikuje stan starszych map Java.

## Poprawka gramatyczna w zasobach

`data/hullmods/SurveyingEquipment.java`, uzywany do opisu wyposazenia pomiarowego floty:

- Dotychczasowa fraza: `jednostek zaopatrzenia i %s jednostek ciezkiego sprzetu.`
- Nowa: `jedn. zaopatrzenia i %s jedn. ciezkich maszyn.`
- Rozwiazuje `1 jednostek` przy wartosci 1; nazwa `ciezkie maszyny` zgadza sie z tlumaczeniem towaru Heavy Machinery.
- Zachowane oba znaczniki `%s`, ASCII, CRLF (86 zakonczen linii) oraz wszystkie instrukcje Java.
- Zmiana dokladnie jednego literału; odmowa przy niezgodnej sumie SHA-256 pliku wejściowego. Nie dokonywano zmian w mapach ani wykonywalnym bajtkodzie `starfarer_obf.jar` / `starfarer.api.jar` (te pozostaja na stanie 1.0.30).

SHA-256 pliku Java przed: `ab222125daf0304b91e5d1f9bfd1a61f386635225197147e6af1c074132bf407`, po: `3e2439b5e21fb40cf9b5daef6ad12eb3c07af0ee9ff73b23a016c5718b8de385`.

Kod: `tools/apply_1031.py`; walidator `tools/verify_1031.py`; oddzielny patcher oryginalnego pliku prywatnego z gry `tools/patch_survey_1031.py` (nigdy nie dodawac komercyjnego zrodla w calosci do GitHuba). Kompilacja oryginalnego i zmienionego `.java` na dostarczonych JAR oraz porownanie instrukcji JVM przeprowadzone lokalnie; **nie jest to test dzialania kodu w samej grze**.

## Ważna korekta: faktycznie zastosowane tlumaczenia API

W 1.0.30 mapowanie `TLUMACZENIA_JAR_1030.csv` ma 5219 wierszy i 5217 faktycznie zastosowanych w oryginalnym API JAR: **dwa** stare wpisy nie maja dopasowania.

Status `DRAFT_ONLY_NOT_INSTALLED` jest mylacy — Go patcher nie filtruje wedlug statusu. Z 1008 wpisow oznaczonych w ten sposob **1006 rzeczywiscie jest zapisanych w spatchowanym JAR** (pozostale 2 bez trafienia). Dlatego zadnych wpisow DRAFT nie wolno pominac z recenzji na podstawie ich nazwy.

Odtwarzalny prywatny audyt dla original + patched JAR: `tools/audit_api_effective_1031.py`; porownanie dotyczy dokladnej puli JVM `CONSTANT_String` i sum SHA-256, nie heurystyk znajdowania napisow w bajtach.

## 30 skontrolowanych tlumaczen API

Ledger `docs/API_SEMANTIC_REVIEW_1031.json` zawiera nieodwracalne SHA-256 wierszy i typ dowodu, bez publikowania komercyjnych fragmentow. Sprawdzenie kontekstow: 10 nazw z konstruktora enum przypisan floty, 3 etykiety raportu miesiecznego i 17 fragmentow z metody UI `addPara`. Każdy ma zatwierdzony sens offline, zachowane znaczniki i sprawdzony wpis w oryginalnym oraz spatchowanym `CONSTANT_String`.

Przed: 3658 wpisow ze starszymi statusami DRAFT/OPTIONAL. Obecnie: **30 pozycji z recenzja offline**, **3628 do takiej recenzji**, lecz **3658 bez udokumentowanego osobnego testu Windows/gameplay**.

Skrypt `tools/verify_review_1031.py` uniewaznia recenzje po najmniejszej zmianie tlumaczenia, wykrywa duplikaty, formaty lub nieuprawniona kategorie dowodu. `tools/check_release_gates_1031.py` liczy pozostale recenzje z ledger i blokuje finalna 1.1, gdy inne bramki nadal otwarte. Ta recenzja *nie jest* testem wizualnym ani potwierdzeniem poprawnosci calej gry.

## Kontrole wydania

- 870 plikow `mod/data/`, zmieniony tylko jeden wzgledem paczki 1.0.30; 873 pliki w ZIP.
- `rules.csv`: 7371/7371 prawidlowych opcji, bez bledow separatora.
- Mapa OBF = 3510 zmienionych literalow, API = 5217 dopasowan; JAR i Go patchery pozostaly z 1.0.30.
- Testy regresyjne Python: 8 testow; testy `go test` i `go vet` trzech komponentow; 3 poprawne pliki PE32+ Windows x64.
- ZIP: `Starsector_PL_ASCII_0.98a_RC8_1.0.31_MINIMALNY.zip`, 14 637 638 bajtow, SHA-256 `fda00cf498901e00b02f0acdce9d0ac81ce195f63b6fb9a01d0cee1dbbbe3a32`; test ZIP CRC prawidlowy. 
- Zmieniony instalator przechodzi testy kompilacji, ale **natywny test na Windows i w grze nie zostal wykonany**.

Odtworzenie po nalozeniu 1013...1030:

```bash
python3 tools/apply_1031.py worktree
python3 tools/verify_1031.py worktree
python3 tools/verify_review_1031.py --map worktree/buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1030.csv --ledger docs/API_SEMANTIC_REVIEW_1031.json
python3 tools/check_release_gates_1031.py worktree --gates docs/RELEASE_GATES_11.json --ledger docs/API_SEMANTIC_REVIEW_1031.json
python3 tools/test_1031.py
python3 tools/test_release_gates_1031.py
(cd worktree && sh build_windows.sh)
python3 tools/package_1031.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.31_MINIMALNY.zip
```

**Otwarte do wersji 1.1:** 81 odwolania do `Misc.STORY`, 219 wywolan zaimkow, 3628 zaleglych recenzji semantycznych, test gry Windows, potwierdzenie kompletnego pokrycia. Zaawansowanie audytu nie jest procentem ukonczenia polonizacji.
