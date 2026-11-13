# Starsector PL ASCII 1.0.44 — bezpieczne formy neutralne w dialogach

Data: 2026-11-13. Gra: Starsector 0.98a-RC8. Poprzednia wersja: 1.0.43 (commit `4aafbd2e250da5146ab5af69c7446c892fee2985`). **Cel 1.1 jest nadal otwarty.**

## Rzeczywiste poprawki

W `data/campaign/rules.csv` poprawiono **25 odrębnych wierszy**, dokonując **30 ściśle wskazanych zamian**. Z widocznych tekstów usunięto **31 problematycznych odwołań** do zmiennych płciowych (`$manOrWoman`, `$himOrHerself`, `$HisOrHer`) przez przeredagowanie zdania na neutralną, naturalną formę. Przykładowo `$manOrWoman zaczyna mowic` zastąpiono `Osoba po drugiej stronie lacza zaczyna mowic`, a `na twarzy $manOrWoman` — `na twarzy rozmowcy`. Zachowano znaczenie wypowiedzi i istniejące zmienne wymagane do scenariusza. Tam, gdzie w tekście pozostały inne dynamiczne zmienne, nie uznawano całego dialogu za kompletnie zweryfikowany językowo.

**Nie zmieniono** identyfikatorów, triggerów, warunków, skryptów, opcji ani notatek w `rules.csv`, żadnego innego pliku danych, map OBF/API ani kodu wykonywalnego Java. Polski ASCII i CRLF zachowane.

Nowe sprawdzenia offline: 25 unikalnych ID i ich oczekiwanych fragmentów, reprodukcja dokładnie 30 zamian, odtworzenie wcześniejszego `rules.csv` bajt w bajt, 6 testów odmowy na błędnej podstawie, kontrola wszystkich siedmiu kolumn CSV, poprawności 7371 opcji, poprawność paczki i instalatora w CI.

## Weryfikacja lokalna (przed zapisem na GitHub)

- `rules.csv` 1.0.43 SHA-256: `a43f8a4f5acf91e67c7331c7828e3152564f2e224ea2a6bb46e49b9d6374f8a0`
- `rules.csv` 1.0.44 SHA-256: `cf1e35899c5cebd42430cf45242662a6c59389e3330c493c6b667bf2eafb918b`
- 11107 rekordów dialogowych: zachowana liczba i kolejność; zmieniono tylko `text` w 25 rekordach.
- 870 plików danych; 869 identycznych; 31 odwołań usuniętych; testy negatywne 6/6 PASS.
- Lokalnie sprawdzono kod patchujący i niezależny walidator na rzeczywistej paczce 1.0.43 odzyskanej z Biblioteki projektu.

## Nowy stan 1.1

Łącznie po 1.0.44: **209 poprawionych wierszy dialogowych** i **327 wyeliminowanych wywołań zmiennych** w wybranych widocznych polach `rules.csv` (w stosunku do wcześniejszego rejestru 184/296). **209 wierszy pozostaje bez wizualnych testów Windows.** Historyczne zadania Java nadal otwarte: **186/219 getterów do recenzji**, konflikt współdzielonego `her`, **3536/3658** starszych pozycji API do kontroli znaczenia, **81 kontekstów PF** do testów UI. Audyt pełnego pokrycia gry i natywny gameplay Windows są niewykonane.

## Reprodukcja

Po `python3 tools/restore_snapshot.py` oraz wszystkich `tools/apply_1013.py`–`tools/apply_1043.py` (w tej kolejności):

```bash
python3 tools/apply_1044.py worktree --ledger-out /tmp/RULES_GENDER_1044_generated.json
python3 tools/verify_1044.py worktree
python3 tools/test_1044.py worktree
python3 tools/check_release_gates_1044.py worktree --gates docs/RELEASE_GATES_11.json --ledger docs/RULES_GENDER_REVIEW_1044.json
(cd worktree && sh build_windows.sh)
python3 tools/package_1044.py --worktree worktree --out Starsector_PL_ASCII_0.98a_RC8_1.0.44_MINIMALNY.zip
```

Oryginalne komercyjne JAR gry pozostają prywatne i **nie są** częścią GitHuba ani wydawanej paczki. CI na Linuxie sprawdza strukturę i cross-build Windows x64, ale **nie jest natywnym testem gry**. Paczka 1.0.44 to następny etap roboczy, **nie gotowa 1.1**.