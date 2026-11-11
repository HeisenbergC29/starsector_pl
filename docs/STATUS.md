# Stan projektu — Starsector PL 0.98a-RC8, 2026-11-11

**Wydanie robocze 1.0.12. Cel 1.1 pozostaje otwarty.**

- **Dane:** 870 zmodyfikowanych lub dodanych plików z oryginalnego `data.rar`; wcześniejsze 868 plików bajtowo identyczne z 1.0.11. Nowo podmieniane: `data/missions/m2/mission_text.txt` i `data/missions/m3/mission_text.txt` (misje treningowe; w m3 zachowane znaczniki `\\n`). Tłumaczenia nazw okrętów i uzbrojenia zgodne z polskimi polami w `ship_data.csv` i `weapon_data.csv`.
- **JAR:** tablice bez zmian od 1.0.10: 3116 OBF, 5040 rzeczywistych podmian API. Oba oryginalne JAR sprawdzone na Linuxie: podgląd, zastosowanie i przywrócenie do oryginalnych SHA-256, wszystkie wykonane próby PASS. Nie jest to test natywny Windows.
- **Instalator:** aktualizacja nazwy wydania na 1.0.12, cross-kompilacja trzech Windows x64 PE32+; testy Go i vet PASS. Paczka minimalna: 873 wpisy ZIP, 870 danych i instalator+instrukcja+mod_info. SHA256 `54f2222355dc6ab56c69a77d6a968696fb586a4b83e5757f72c8664852f1d78a`.
- **Audyt źródła:** niezależnie rozpakowane `data.rar` zawiera 1399 niepustych plików. W 1.0.12 podmienianych 870, pozostaje 529 oryginalnych plików niepodmienianych, przeważnie technicznych. Potrzebna dalsza klasyfikacja pól widocznych dla gracza.
- **Zabezpieczenia:** `tools/check_project.py` sprawdza 870 plików, ASCII, 41 wpisów replace, 11107 rekordów oraz 7371 opcji dialogowych; test w GitHub Actions i test negatywny na celowo uszkodzonym dwukropku. Nie zgłaszaj fałszywie kompletności 1.1.
- **Awaria 1.0.9:** naprawa 38 dwukropków opcji w `rules.csv` pozostaje zawarta w 1.0.12. Wystąpienie `NumberFormatException` ma osobne zgłoszenie #1; **wynik naprawy w grze na Windows nie jest jeszcze potwierdzony**.
- **Uwaga krytyczna:** patchery ignorują kolumnę `status`, więc wpisy `DRAFT_ONLY_NOT_INSTALLED` również były patchowane. Dokładne wyniki w `docs/JAVA_MAPPING_STATUS.md`, issue #3.

## Do pełnej wersji 1.1
1. Natywny test uruchomienia 1.0.12 w Windows i kontrola dziennika po awarii 1.0.9.
2. Rozstrzygnięcie pozostałych kandydatów Java OBF/API i weryfikacja tłumaczonych literałów, także nieprzeznaczonych dla interfejsu.
3. Dokończenie kontroli nazw zwyczajowych, pseudonimów, skrótów z tłumaczonym rozwinięciem, odmiany tekstów dynamicznych.
4. Potwierdzenie, że wszystkie zmiany odpowiadają tylko polom do lokalizacji. Pięć zmian w `rules.csv` dotyczy wyłącznie argumentów `SetTextHighlights` potrzebnych do podświetlenia polskiego tekstu.
5. Rozstrzygnięcie wariantów 67 plików różniących się między oryginalnymi archiwami; wyniki audytu nie dowodzą braków w działającej grze.

## Odtworzenie
`python3 tools/restore_snapshot.py` tworzy `worktree/` z aktualnych dziewięciu części `snapshots/starsector_sources_1012.part000..008`. Nie zawiera oryginalnych JAR ani binariów Windows. Szczegóły: `docs/BUILD.md`, `AGENTS.md`.