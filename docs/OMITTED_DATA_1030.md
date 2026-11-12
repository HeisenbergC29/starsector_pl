# Audyt 1.1: 529 zasobow data/ pozostawionych bez nadpisania

Odtwarzalna kontrola oryginalnego prywatnego `data.rar` (Starsector 0.98a-RC8, SHA-256 archiwum `e3c4f28ddae07b4b9adcef155962688db6f1205719369784a70c5b9a8575ecd1`) wobec polonizacji 1.0.29.

**Zrodlo:** 1399 niepustych plikow; **polonizacja:** 870 (wszystkie w zbiorze oryginalow); **pominięte:** 529. Pominięcie nie jest automatycznie bledem, ale kazda aktywna wartosc widoczna dla gracza musi zostac rozpatrzona.

## Rozklad 529 plikow

| Format | Ilosc | Klasyfikacja robocza |
|---|---:|---|
| `.wpn` | 163 | definicje broni (grafika, parametry, techniczne ID) |
| `.proj` | 110 | definicje pociskow |
| `.system` | 63 | definicje systemow okretowych |
| `.java` | 50 | skrypty: osobny audyt aktywnych literalow |
| `.json` | 30 | konfiguracja, gospodarka i generatory; nie zmieniac kluczy |
| `.skill` | 28 | konfiguracja efektow umiejetnosci |
| `.ship` | 24 | specyfikacja kadlubow; 23 nazwy zgodne z lokalna tabela |
| `.csv` | 18 | dane techniczne, losowanie, misje, lista plikow, imiona i nazwiska |
| `.variant` | 16 | warianty okretow, 4 z `displayName` do kontroli |
| `.jpg`, `.png` | 22 | obrazy, nie pliki tekstowe |
| `.sample` | 4 | przyklady/format pomocniczy |
| `.txt` | 1 | `game_mechanics.txt`: wpis w `text_codex_entries.csv` jest skomentowany |

### Weryfikacja 23 nazw kadlubow

We wszystkich 23 pominietych plikach `.ship` majacych pole `hullName` nazwa jest **identyczna z nazwa w spolonizowanym `hulls/ship_data.csv`**. Nie znaleziono sprzecznej nazwy. Jeden plik `.ship` nie ma `hullName`. Samo porownanie nie rozstrzyga polityki tlumaczenia kazdej nazwy wlasnej.

### Cztery nazwy wariantow do rozstrzygniecia

- `variants/prometheus_Super.variant` zawiera `displayName=Super` (ten sam zapis funkcjonuje po polsku).
- Trzy warianty DEM (Hammerhead, Gryphon, Conquest) maja `displayName=DEM` (akronim/oznaczenie; nie zmieniac na slepo bez identyfikacji rozwinięcia i miejsca wyswietlenia).

### 50 niepodmienionych skryptow Java

`tools/audit_java_source_1030.py` zanalizowal literały z **aktywnych fragmentow kodu**, ignorujac komentarze: **238 literałów** w 50 plikach, z czego jeden zawiera dwa angielskie slowa: diagnostyczne `BUTTON PRESSED: ` w `scripts/plugins/TestCombatPlugin.java`, przekazywane do `System.out.println`. W tej samej klasie teksty `TEST` i `Tick` sa elementami testowego UI, a ich sciezka w `advance()` znajduje sie po instrukcji `if (true) return;`. Nie jest to zidentyfikowany ekran rozgrywki. Pozostale teksty to przewaznie klucze, nazwy, wartosci liczbowe i fragmenty szablonow.

**Wniosek czesciowy:** nie uzyskano dowodu, ze trzeba automatycznie nadpisywac wszystkie 529 plikow. Potwierdzono pozostale miejsca wymagajace kontekstowej decyzji (4 `displayName` i potencjalne uzycia w kodzie). Kontrola leksykalna nie jest natywnym testem runtime ani dowodem kompletnego 1.1.

## Odtworzenie audytu (oryginaly prywatne)

```sh
python3 tools/audit_omitted_data_1030.py --original /PRIVATE/data-unpacked --localized worktree/mod --out /PRIVATE/OMITTED_DATA_FULL.json --summary /PRIVATE/OMITTED_DATA_SUMMARY.json
python3 tools/audit_java_source_1030.py --original /PRIVATE/data-unpacked --localized worktree/mod --out /PRIVATE/OMITTED_JAVA_FULL.json --summary /PRIVATE/OMITTED_JAVA_SUMMARY.json
python3 tools/test_java_lex_1030.py
```

Publiczne liczniki i klasyfikacje: `docs/OMITTED_DATA_1030_SUMMARY.json`, `docs/JAVA_SOURCE_1030_SUMMARY.json`. Szczegolowe wyniki zostaja prywatne. Testy nie modyfikuja gry.
