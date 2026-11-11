# Starsector PL 1.0.15 — wydanie robocze 2026-11-11

**Gra:** Starsector 0.98a-RC8. **Cel: pelna lokalizacja 1.1 (NIE UKONCZONA).**

## Nowe tlumaczenia (8)

**OBF +5:** podpowiedzi: poziomy przychodow (gwiazdki); lokalna produkcja i dostawca; dwa warianty ryzyka szturmu ladowego/piechoty morskiej; dialog potwierdzenia rozkazu pelnego ataku.

**API +3:** opis sygnalu czarnej dziury; komunikat odzyskiwania okretow; dialog naukowca.

Wybrane literaly zweryfikowane w oryginalnych JAR i lokalnym bytecode/javap jako teksty widoczne w grze. Zmieniono tlumaczenia, nie ID, warunki ani kod gry.

## Weryfikacja wykonana lokalnie (Linux, oryginalne biblioteki gry)

| Test | Wynik |
|---|---|
| Identycznosc SHA-256 obu oryginalnych JAR | PASS |
| OBF — 3121 podmian referencji CONSTANT_String, 526 klas | PASS |
| API — 5075 podmian referencji CONSTANT_String, 933 klasy | PASS |
| Porownanie JAR na poziomie pul stalych/manifestu: kod metod bez zmian | PASS |
| OBF — 526 wpisow manifestu odpowiada 526 zmienionym klasom | PASS |
| OBF — 2401 niezmienionych wpisow archiwum | PASS |
| API — 2607 niezmienionych wpisow archiwum | PASS |
| Instalacja na czystych oryginalnych JAR | PASS |
| Aktualizacja obu JAR z 1.0.14 do 1.0.15 | PASS |
| Powtorna instalacja bez ponownego patchowania | PASS |
| Przywrocenie oryginalnych SHA-256 | PASS |
| Skrypt overlay 1015 na odtworzonym stanie 1014 — bajtowa zgodnosc z buildem | PASS |
| Go test / vet: OBF, API, instalator | PASS |
| Cross-kompilacja 3 PE32+ EXE Windows x64 | PASS |
| Kontrola rules.csv — 7371/7371 opcji poprawnych | PASS |
| 870 plikow data identycznych z 1.0.14 | PASS |
| ZIP: CRC, 873 wpisy | PASS |
| Natywny test na Windows | NIE WYKONANO |
| Test w uruchomionej grze | NIE WYKONANO |
| Pelna lokalizacja 1.1 | NIE POTWIERDZONO |

OBF zaktualizowany ma SHA-256 `6fbf5af6e570de156ef40c7f8a3684fafa582f1a981da51c2e1aeb5e4a24d087`; patcher API zostal nauczony rozpoznawania tej wersji dla instalacji i aktualizacji.

## Paczka gracza

`Starsector_PL_ASCII_0.98a_RC8_1.0.15_MINIMALNY.zip`: 10 614 671 B, SHA-256 `94ae0179c3ca616b67e484a1790e90b1e86dc27bc34f381973ab8a67c43c1d8b`. 873 elementy: 870 danych, `mod_info.json`, `CZYTAJ.txt`, jeden instalator Windows EXE. Prywatna Biblioteka zawiera ZIP i `Starsector_PL_1.0.15_TESTY.json`. Oryginalne JAR nie sa dystrybuowane.

## Odtworzenie stanu z GitHub

```sh
python3 tools/restore_snapshot.py
python3 tools/apply_1013.py worktree
python3 tools/apply_1014.py worktree
python3 tools/apply_1015.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
```

Skrypt `tools/audit_1015_jars.py` wymaga dwoch oryginalnych JAR dostarczonych prywatnie przez uzytkownika. Nie dodawac ich ani pelnych zasobow gry do publicznego GitHuba. `tools/audit_localization_risks.py` kontroluje aktywne mapy OBF/API i daje tylko diagnostycznych kandydatow do recenzji.

## Otwarte zagadnienia 1.1

- Issue #1: potwierdzenie uruchomienia na Windows i ewentualnych bledow rules.csv.
- Issue #2: dalszy audyt pelnego pokrycia wszystkich pol widocznych (w tym dynamiczne teksty, nazwy, nicki i skroty).
- Issue #3: statusy map `DRAFT_ONLY_NOT_INSTALLED` sa ignorowane przez patcher i wymagaja przegladu kontekstow.
- 529 niepodmienionych plikow data, z czego `data/codex/game_mechanics.txt` nie jest aktywowany przez wpisy kodeksu — nie dodawac bez dowodu, ze jest uzywany.

Numery 1.0.x oznaczaja kolejne etapy. Nie twierdzic, ze 1.1 lub 100% jest osiagniete.
