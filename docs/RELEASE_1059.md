# Starsector PL ASCII 1.0.59 — kompletne naglowki i skladanie raportu miesiecznego

**Gra:** Starsector 0.98a-RC8. **Platforma instalatora:** Windows x64. **Cel 1.1: NIEUKONCZONY.**

## Faktycznie zmienione teksty

Audyt oryginalnego `starfarer.api.jar` ujawnil szesc angielskich literalow `CONSTANT_String` nieobecnych w mapie 1.0.58, lecz uzywanych w aktywnym interfejsie klasy `com.fs.starfarer.api.impl.campaign.MonthlyReportNodeTooltipCreator`. Bez zmiany instrukcji JVM przetlumaczono:

| Oryginalna stala | Nowy polski fragment | Miejsce |
| --- | --- | --- |
| `Equipment` | `Wyposazenie` | Naglowek raportu produkcji |
| `Ships` | `Okrety` | Naglowek listy okretow (3 aktywne wystapienia) |
| `Resources` | `Zasoby` | Naglowek zasobow (2 aktywne wystapienia) |
| `unit` | pusty fragment | Singular w skladanym zdaniu |
| `units` | pusty fragment | Plural w skladanym zdaniu |
| ` of ` | pusty fragment | Angielski lacznik w skladanym zdaniu |

Jednoczesnie skorygowano istniejacy fragment `Approximately %s `: 

- **Poprzednio:** `Okolo %s ` + `unit(s)` + ` of ` + nazwa towaru + `.` — mieszanka polskiego i angielskiego.
- **Obecnie:** `Szacunkowa ilosc: %s jedn. Towar: ` + nazwa towaru + `.`. Na przyklad: `Szacunkowa ilosc: 5 jedn. Towar: Ruda.`

Dzieki rozdzieleniu nazwy towaru po dwukropku nie trzeba sztucznie odmieniac dynamicznie wstawianej nazwy; dziala tez dla towarow o dowolnym rodzaju i liczbie. Przetestowano 15 kombinacji: liczby 1, 2, 5, 12, 21 oraz nazwy Ruda, Paliwo, Ciezka maszyna.

**Zakres:** szesc nowych wpisow mapy API + jedna korekta istniejacego wpisu, **dokladnie jedna zmodyfikowana klasa Java**. Mapa API: 5298 → **5304 wiersze** (5296 → **5302 skuteczne podmiany**), nadal 938 klas. Mapa OBF 3537 podmian w 539 klasach bez zmian. Nie zmieniano zadnego pliku `mod/data/` ani `rules.csv`.

## Weryfikacja oryginalnego JVM

- Sprawdzono SHA-256 oryginalnego `starfarer.api.jar` (`a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`).
- Potwierdzono **10/10 rzeczywistych instrukcji `ldc/ldc_w`**. Etykiety wywoluja `TooltipMakerAPI.addSectionHeading`, a reszta sklada widoczny tekst przez `StringBuilder` i `TooltipMakerAPI.addPara`. Raport: `docs/JVM_AUDIT_1059.json`, skrypt: `tools/audit_original_jvm_1059.py`.
- Porownanie plikow wewnatrz JAR po patche 1.0.58 i 1.0.59 wykazalo **jedna zmieniona klase `.class` z 3540 wpisow archiwum**. Instrukcje JVM z `javap -c` — **545/545 identycznych pozycji, opcode i operandow**; nowa wersja uzywa zmienionych stalych tekstowych.
- Oryginalne biblioteki komercyjne nie sa publikowane ani commitowane.

## Testy instalacji i aktualizacji

- **Fresh 1.0.59 = upgrade 1.0.58 → 1.0.59** na oryginalnych komercyjnych JAR. Wynik API: SHA-256 `9d7424d40ae88d62cf85c09cc1ff99a4e3abeba6cad896683b68d8ac74afcf3e`.
- OBF bez nowych zmian: `85b4b2afb4f6175cabedf1ef5cb9976e0097e39403dff0fc18c728c9d48894e1`.
- Ponowna instalacja API: no-op; przywracanie obu oryginalnych JAR: bajtowo identyczne; uszkodzony JAR odrzucony bez nadpisania. Raport: `docs/PRIVATE_UPGRADE_1059.json`; powtorzenie: `tools/private_upgrade_1059.py`.
- W mapie 1.0.59 nie ma nowych podmian technicznych ID. Wszystkie 870 plikow `mod/data` maja identyczny laczny digest jak w 1.0.58; 11 107 rekordow dialogowych i 7371 opcji pozostaje bez zmian.
- Walidacja mapy: dokladnie 6 dodanych wpisow, jedna korygowana wartosc, 10 negatywnych mutacji odrzuconych; 5 falszywych metadanych paczki odrzuconych. `go test ./...`, `go vet ./...` dla obu patcherow przeszly.

## Audyt nie jest podwojnie liczony

17 historycznych wpisow tej samej klasy bylo juz ujete w `docs/API_SEMANTIC_REVIEW_1055.json`. **Licznik historycznych recenzji pozostaje 391/3658**, a 3267 historycznych wpisow wymaga dalszej recenzji. Dodane w tym wydaniu 6 nowych literalow nie jest historycznymi pozycjami, a poprawa jednego starego nie zwieksza licznika.

Wciaz pozostaje **186** niewyjasnionych getterow JVM, **1953** surowych zmiennych plci w 1006 dialogach, audyt pelnej kompletnosci tekstow i **natywny test Windows w uruchomionej grze**. Nie deklarowac gotowosci 1.1 na podstawie samego CI.

## Odtworzenie z repozytorium

Po odtworzeniu snapshotu 1.0.12 i zastosowaniu kolejno nakladek 1013–1058:

```sh
python3 tools/apply_1059.py worktree
python3 tools/verify_1059.py worktree
python3 tools/test_1059.py worktree
python3 tools/test_package_contract_1059.py worktree
python3 tools/check_release_gates_1059.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1058.json
python3 tools/test_release_gates_1059.py worktree --gates docs/RELEASE_GATES_11.json --previous docs/RELEASE_GATES_1058.json
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1059.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.59_MINIMALNY.zip
```

Oryginalne biblioteki JAR pozostaja wylacznie w prywatnym testowym folderze. Test JVM: `python3 tools/audit_original_jvm_1059.py --jar /PRIVATE/starfarer.api.jar`. Test aktualizacji: `python3 tools/private_upgrade_1059.py --jars /PRIVATE/starsector-core --worktree worktree`.
