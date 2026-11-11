# Starsector PL 1.0.14 — wersja robocza (2026-11-11)

**Cel 1.1: niezakończony.** Gra: Starsector 0.98a-RC8.

## Zawartość zmian
- 17 potwierdzonych w oryginalnym JAR tekstów interfejsu: dymki autofitu (7), umiejętności (2), podpowiedź podróży (1), modyfikacja okrętu (1), dialogi i opisy kampanii (6).
- W API patcher usunięto błąd zakazujący źródłowych znaków UTF-8, np. `×` w angielskim opisie zdolności; nowe polskie literały nadal pozostają w ASCII. Dodano test regresyjny z syntetyczną pulą stałych JVM.
- Mapa API: **5074 rekordy / 5072 faktycznie dopasowanych podmian** w **933 klasach** (wersja 1.0.13: 5055 podmian w 931 klasach). Mapa OBF nadal 3116.
- 870 plików `data/` bajtowo identycznych z 1.0.13.

## Reprodukcja bez komercyjnych plików w repo
```bash
python3 tools/restore_snapshot.py
python3 tools/apply_1013.py worktree
python3 tools/apply_1014.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
```
Snapshot w `snapshots/` pozostaje bazową wersją 1.0.12; zmiany 1013 i 1014 są deterministycznymi warstwami źródeł. Mapy obu wersji są zachowane na potrzeby upgrade. Oryginalne JAR i `data.rar` znajdują się wyłącznie poza publicznym repozytorium.

## Zweryfikowane testy (Linux, oryginalne JAR użytkownika)
- Oba oryginalne JAR zgadzają się z SHA-256 w `docs/SOURCES.md`.
- API preview/install/reinstall/restore **PASS**: 5072 podmian w 933 klasach; po restore dokładnie oryginalny SHA-256.
- Upgrade 1.0.13 -> 1.0.14 -> restore **PASS**; starsze tłumaczenia pozostają zachowane.
- Audit `tools/audit_1014_jar.py` oryginał vs instalacja: **2607 niezmienionych pozycji ZIP**, **933 klasy z dozwolonymi zmianami**, **5072 zatwierdzone przepisania referencji `CONSTANT_String`**, zero zmian poza tekstami w metodach i nagłówkach klas. Jest to audyt zmian API w tej wersji, nie dowód pełnej lokalizacji.
- Go test/vet dla OBF, API, instalatora **PASS**; test źródłowego UTF-8 **PASS**, build PE32+ Windows x64 **PASS**.
- `rules.csv`: 7371/7371 opcji poprawnych, 11107 rekordów, 41 wpisów `replace`, 870 plików danych ASCII. ZIP CRC **PASS**.

## Pakiet gracza
`Starsector_PL_ASCII_0.98a_RC8_1.0.14_MINIMALNY.zip`
- Rozmiar: **10 289 809 bajtów**
- SHA-256: `2acf8d012da747c0767c777b62bb4cfc28f3879c02430d44e97125b83c03f99f`
- 873 pliki: 870 danych, `mod_info.json`, `CZYTAJ.txt`, jeden EXE Windows x64.
- ZIP i raport `Starsector_PL_1.0.14_TESTY.json` zapisano w prywatnej Bibliotece projektu.

## Niepotwierdzone
Natywny Windows i uruchomiona gra **nie były testowane**. Wersja 1.1 wymaga dalszej klasyfikacji oryginalnych plików i nieprzetłumaczonych literałów, analizy nazw i skrótów oraz kontroli statusów `DRAFT_ONLY_NOT_INSTALLED` (patcher w rzeczywistości je stosuje). Aktywne zgłoszenia #1, #2, #3.
