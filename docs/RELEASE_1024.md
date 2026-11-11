# Starsector PL 1.0.24 — robocza polonizacja (2026-11-11)

**Starsector 0.98a-RC8. Pełna wersja 1.1 NIE jest ukończona.**

## Poprawka: 44 nowe tłumaczenia widocznych etykiet Java

| Obszar | JAR | Nowych | Przykłady |
|---|---|---:|---|
| Główne menu | OBF | 8 | Continue → Kontynuuj, Settings → Ustawienia, Credits → Tworcy, Quit → Wyjdz |
| Wybór broni | OBF | 4 | Ballistic → Balistyczna, Energy → Energetyczna |
| Wybór eskadr | OBF | 4 | Interceptors → Przechwytujace, Bombers → Bombowce |
| Grupy uzbrojenia | OBF | 6 | Auto-assign → Auto-przypisz, Flux → Strumien |
| Launcher i jego ustawienia | OBF | 6 | Mods... → Mody..., Options... → Opcje..., Apply → Zastosuj |
| Filtry planet / obszarów | API | 5 | Stars → Gwiazdy, Unclaimed → Bez roszczen |
| Raport kolonii | API | 1 | Colonies → Kolonie |
| Opis specjalnego przedmiotu | API | 2 | None → Brak, Price: → Cena: |
| Opisy zadań flot | API | 8 | Attacking → Atakuje, Following → Podaza, Orbiting → Orbituje |
| **Razem** | **OBF 28 / API 16** | **44** | |

Wszystkie 44 źródłowe teksty potwierdzono w oryginalnych `CONSTANT_String` 11 klas Java, a ich funkcje UI (przyciski, filtry, opis pozycji, tytuły tooltipów, etykiety enum dla zadań flot) w oryginalnym `javap -c -p`. Samo `javap` nie gwarantuje tekstu widocznego w każdej rozgrywce.

**Zachowane bez zmian:** techniczne enum ID `FOLLOW`, `HOLD`, `INTERCEPT`, `RAID_SYSTEM` itd., warunki i skrypty, dane `mod/data`, imiona/nazwiska oraz cały wykonywalny bajtkod. Nie zmieniono wartości `Off` w konfiguracji launchera — potencjalnie bierze udział w porównywaniu wybranej opcji i wymaga odrębnej kontroli.

## Wyniki testów na oryginalnych JAR (Linux)

| Test | Wynik |
|---|---|
| OBF `3213` podmian tekstowych, `533` zmienione klasy | PASS |
| API `5148` podmian tekstowych, `936` zmienionych klas | PASS |
| Audyt oryginalny vs zmodyfikowany `CONSTANT_String`: tylko dopuszczone literały | PASS |
| Niedozwolona modyfikacja kodu metod lub pól technicznych | **0** |
| Manifest OBF: dokładnie 533 zmienione sekcje skrótów | PASS |
| OBF: 2394 niezmienionych wpisów archiwum; API: 2604 | PASS |
| Świeża instalacja na oryginalnych JAR | PASS |
| Upgrade 1.0.23 → 1.0.24: wynik obu JAR identyczny bajtowo ze świeżą instalacją | PASS |
| Powtórna instalacja — idempotencja | PASS |
| Restore — oryginalne JAR odtworzone bajtowo | PASS |
| Zachowanie historycznych map i dokładnie 44 dozwolone nowe rekordy | PASS |
| Testy negatywne: wykrywanie zmienionych starszych tłumaczeń/duplikatów | PASS |
| Go test/vet OBF/API/instalatora, kompilacja 3 PE32+ Windows x64 | PASS |
| 870 plików danych identycznych z 1.0.23 | PASS |
| `rules.csv`: 7371/7371 poprawnych opcji | PASS |
| ZIP 873 wpisy, CRC, bez oryginalnych JAR | PASS |
| Uruchomienie instalatora na Windows / test gry | **NIE WYKONANO** |
| Zakończona 1.1 | **NIE** |

**SHA-256 oryginalnych bibliotek:** OBF `5dd222b9e266d2ac2d63b3dad4983eb05caaf5a247d7dfb82aaeba47ea774cc8`; API `a7ba18f3476ffe704729bd0a7a47443f035fea98a32ac2930eae8b391d013c2a`.

**SHA-256 po patchu 1.0.24:** OBF `ab9933a7c9879879e0b0a12516dec63cedf9bd7517430400bb2bf0a9577c2560`; API `3d584fb28a334adc62894795bb197e3618eee718d1830de129eec22accd5b843`.

**ZIP:** `Starsector_PL_ASCII_0.98a_RC8_1.0.24_MINIMALNY.zip` — **13 031 153 B**, SHA-256 `31bf9f27f2451be4f10e3ebcca0568cceee9e3812295ffdb29686c4f025a0b2f`. Pakiet i raport `Starsector_PL_1.0.24_TESTY.json` zapisano w prywatnej Bibliotece projektu.

**GitHub Actions: PASS** — [przebieg 43110733323](https://github.com/HeisenbergC29/starsector_pl/actions/runs/43110733323), commit `e13b6baa`. Odtworzono wszystkie nakładki od 1.0.12 do 1.0.24, sprawdzono nowe mapy i testy negatywne, walidację danych i opcji dialogowych, Go test/vet oraz Windows x64 cross-build. CI nie uruchamia gry.

## Odtwarzanie i testy

```sh
python3 tools/restore_snapshot.py
for n in 1013 1014 1015 1016 1017 1018 1019 1020 1021 1022 1023 1024; do
  python3 "tools/apply_$n.py" worktree
done
python3 tools/verify_1024_ui.py worktree
python3 tools/test_1024_delta.py worktree
python3 tools/check_project.py worktree/mod
python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv
(cd worktree && sh build_windows.sh)
python3 tools/package_1024.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.24_MINIMALNY.zip
```

Z prywatnymi oryginalnymi JAR, JDK i `javap`:

```sh
python3 tools/verify_1024_callsites.py --obf /prywatna/sciezka/starfarer_obf.jar --api /prywatna/sciezka/starfarer.api.jar
```

Następne zadania do 1.1: pozostałe krótkie etykiety i teksty dynamiczne, odmiana zaimków, 81 miejsc użycia `Misc.STORY`, audyt semantyczny starszych map `DRAFT/OPTIONAL` oraz rzeczywisty test gry na Windows. **Nie mylić zaliczonej kontroli bajtkodu z potwierdzeniem pełnej lokalizacji ani z uruchomieniem gry.**
