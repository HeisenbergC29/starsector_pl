# Starsector PL ASCII 1.0.60 — poprawa tras flot handlowych i odmiany ladunku

**Gra:** Starsector 0.98a-RC8. **Wydanie robocze:** 1.0.60 / Windows x64. **Cel 1.1: nadal NIEUKONCZONY.**

## Faktyczne zmiany tlumaczen

Audyt oryginalnego `starfarer.api.jar` ujawnil brakujace elementy widocznych pol UI w `TradeFleetDepartureIntel` i `ProcurementMissionIntel` oraz dwa blednie poskladane polskie zdania o przewozie ladunku.

| Klasa | Angielski fragment | Polski fragment 1.0.60 | Rodzaj |
| --- | --- | --- | --- |
| TradeFleetDepartureIntel | `From ` | `Trasa: ` | nowe |
| TradeFleetDepartureIntel | ` to ` | `, cel: ` | nowe |
| TradeFleetDepartureIntel | `goods` | `towary` | nowe |
| TradeFleetDepartureIntel | `materiel` | `materialy` | nowe |
| ProcurementMissionIntel | `Faction: ` | `Frakcja: ` | nowe |
| TradeFleetDepartureIntel | `It's noteworthy because it's carrying a large quantity of ` | `To warte uwagi: flota przewozi znaczne ilosci ladunku. Rodzaj: ` | poprawka |
| TradeFleetDepartureIntel | `It's noteworthy because it's carrying a large quantity of valuable ` | `To warte uwagi: flota przewozi znaczne ilosci cennego ladunku. Rodzaj: ` | poprawka |

W oryginalnej metodzie `TradeFleetDepartureIntel.getWhat()` wartosc dobierana jest sposrod `goods`, `materiel` oraz `goods and materiel` (to ostatnie tlumaczenie jest juz aktywne jako `towary i materialy`). Wersja 1.0.59 generowala np. `To warte uwagi, bo przewozi duza ilosc cennych towary i materialy.` — gramatycznie bledne dla kazdej z trzech kombinacji. Nowy wariant zmienia konstrukcje na rzeczownikowy opis rodzaju ladunku, niezalezny od przypadku nazwy towaru.

**Warianty zweryfikowane:** 9 opisow ladunku (3 rodzaje x 3 okolicznosci), 4 trasy i 3 nazwy frakcji, lacznie **16**. Przyklad: `Trasa: Jangala, cel: Chicomoztoc`; `To warte uwagi: flota przewozi znaczne ilosci cennego ladunku. Rodzaj: towary i materialy.`

**Wylaczenia techniczne:** celowo nie tlumaczono `Trade` w `ProcurementMissionIntel.getIntelTags()` ani `Smuggling` w `TradeFleetDepartureIntel.getIntelTags()`. Te ciagi sa uzywane w zestawach kategorii i moga sluzyc do filtrowania/porownan. Nie ruszano nazw dostepu do tekstur, kluczy konfiguracji, skryptow, instrukcji Java, pozostalch klas ani danych gry.

## Weryfikacja oryginalnych bibliotek

- Potwierdzona wersja oryginalnego `starfarer.api.jar`: SHA-256 `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.
- **7 rzeczywistych miejsc `ldc/ldc_w`** w 2 klasach oryginalnego JVM zostalo niezaleznie sprawdzonych (`tools/audit_original_jvm_1060.py`, `docs/JVM_AUDIT_1060.json`). Odpowiednie wartosci trafiaja do podpowiedzi, etykiet lub skladowych opisu ladunku.
- Na oryginalnych komercyjnych JAR: **fresh 1.0.60 = upgrade 1.0.59 -> 1.0.60** bajt w bajt; ponowne uruchomienie patchera nie zmienia JAR; restore przywraca oryginalne SHA; uszkodzony JAR jest odrzucany. Sprawdzono w `tools/private_upgrade_1060.py` i `docs/PRIVATE_UPGRADE_1060.json`.
- W obrazie JAR pomiedzy 1.0.59 a 1.0.60 zmienily sie **dokladnie 2 klasy**: `ProcurementMissionIntel.class` i `TradeFleetDepartureIntel.class`. Dla obu ich offsety i instrukcje JVM (`javap -c -p`) sa identyczne; zmodyfikowane sa wylacznie stale tekstowe.
- Nowy wynik API: SHA-256 `fb27387ebe7ed703012dd1300a15d401af1a69889c228aa1a1d67a43af896b1f`. OBF pozostaje `85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1`.
- Mapa API: **5304 -> 5309 wpisow** (+5 nowych, 2 historyczne poprawione), **5302 -> 5307 skutecznych podmian**, 938 klas mapy wykonawczej bez nowych klas.
- Pozostaly niezmienione **870 plikow danych** (`rules.csv`: SHA-256 `4fcf72e3aad0a0c72bac3bea021a311b36f12c4d201d4dcf9b9c7edf2eeb0e04`), w tym 11 107 wierszy dialogow i 7371 poprawnych opcji.

## Kontrole techniczne

- `tools/verify_1060.py` potwierdza bitowo cala mape 1.0.60, dokladnie 5 nowych par i 2 zatwierdzone korekty, oraz integralnosc danych i wersji Go.
- `tools/test_1060.py`: **11 nieprawidlowych mutacji** odrzuconych.
- `tools/test_package_contract_1060.py`: **5 nieprawidlowych stanow** odrzuconych.
- `go test ./...` oraz `go vet ./...` dla patcherow API, OBF i instalatora: PASS.
- `sh build_windows.sh`: skompilowano 3 poprawne programy PE32+ x64.
- `maintenance/check_rules_options.py`: 7371 opcji, zero nieprawidlowych.
- Paczka lokalna: `Starsector_PL_ASCII_0.98a_RC8_1.0.60_LOCAL.zip`, **873** wpisy, **870** plikow danych, CRC PASS, zadnych komercyjnych JAR. SHA-256 `eb13089c8fc3d016e0f16eb555fe7dabcff3b344628acd456b777da0da66d6aa`.

## Historia i bramki 1.1

To wydanie nie jest ponowna recenzja starych map: 2 poprawione pozycje pozostaja w historycznym dlugu (wymagaja pelnego audytu kontekstowego), a 5 nowych nie bylo czescia 3658 historycznych wpisow. Historyczne API **391/3658**, nierozpatrzone **3267** (bez sztucznego zwiekszania licznika). Gettery JVM **186** do analizy; zmienne plciowe **1953** wystapienia w **1006** rekordach; poprzednich **555** recenzji tekstowych nie liczono ponownie. Wszystkie wydania 1.0.60 pozostaja nieprzetestowane w **uruchomionej grze Windows**. Wydanie **1.1 nadal zablokowane**.

## Reprodukcja

Po `python3 tools/restore_snapshot.py` i nakladkach `tools/apply_1013.py` do `tools/apply_1059.py`:

```sh
python3 tools/apply_1060.py worktree
python3 tools/verify_1060.py worktree
python3 tools/test_1060.py worktree
python3 tools/test_package_contract_1060.py worktree
python3 tools/check_release_gates_1060.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1059.json
python3 tools/test_release_gates_1060.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1059.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1060.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.60_MINIMALNY.zip
```

Prywatny audyt JVM: `python3 tools/audit_original_jvm_1060.py --jar /PRIVATE/starsector-core/starfarer.api.jar`. Prywatny test aktualizacji: `python3 tools/private_upgrade_1060.py --jars /PRIVATE/starsector-core --worktree worktree`. **Nigdy nie dodawac komercyjnych JAR do repozytorium lub ZIP.**
