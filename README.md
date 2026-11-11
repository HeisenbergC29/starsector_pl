# Starsector PL ASCII — polonizacja Starsector 0.98a-RC8

**Stan (1.0.21):** rozwijana polonizacja, docelowe wydanie **1.1** NIE jest jeszcze ukończone.

Repozytorium ma umożliwić innemu agentowi odtworzenie i kontynuowanie pracy bez historii rozmowy.

**Aktualny stan roboczy: 1.0.21** (snapshot 1.0.12 + kolejne overlaye 1013–1021; +2 etykiety OBF, +1 naglowek API i 4 korekty w trzech plikach danych). Cel 1.1 nieukonczony.

## Zacznij tutaj
1. [AGENTS.md](AGENTS.md) — niezmienne zasady pracy i lokalizacji.
2. [docs/STATUS.md](docs/STATUS.md) — prawdziwy stan, znane błędy i następne kroki.
3. [docs/SOURCES.md](docs/SOURCES.md) — oryginalne pliki, sumy SHA-256 i odtwarzanie środowiska.
4. [docs/BUILD.md](docs/BUILD.md) — kompilacja i testy patcherów.
5. [docs/TEST_109_CRASH.md](docs/TEST_109_CRASH.md) — błąd zgłoszony podczas testu 1.0.9.

## Zakres
- Polonizujemy **wszystkie pola wyświetlające tekst graczowi**: dane, dialogi, kod OBF/API i teksty dynamiczne.
- Tłumaczymy nazwy mające ustalone polskie odpowiedniki, pseudonimy i skróty z przetłumaczonym rozwinięciem.
- Nie tłumaczymy imion/nazwisk osób ani technicznych ID, warunków, skryptów, parametrów i odwołań.
- Polski ASCII (bez znaków diakrytycznych) w zasobach gry, dopóki nie zostanie potwierdzona obsługa znaków.
- Każdą zmianę weryfikujemy względem źródeł. Samo przejście testu instalatora NIE dowodzi ukończenia lokalizacji.

## Prawo i bezpieczeństwo
**Nie dodawać oryginalnych JAR, pełnych zasobów komercyjnej gry ani logów z prywatnymi ścieżkami użytkownika do publicznego GitHuba.** Użytkownik ma oryginały w archiwach przekazanych prywatnie. Do repo należą źródła narzędzi, mapy przekładu, praca własna, instrukcje i testy.

## Test gry
Zgłoszony crash na 1.0.9 został odtworzony poprzez analizę `rules.csv` i bajtkodu parsera. Ścieżka naprawy opisana jest w `docs/TEST_109_CRASH.md`.

Wersja 1.1 dopiero po pełnym audycie, a nie po samym wzroście liczby podmian.

## Rozwój 1.0.13
Po odtworzeniu `worktree` z archiwum 1.0.12 wykonaj `python3 tools/apply_1013.py worktree` przed kompilacja. Nowy plik `TLUMACZENIA_JAR_1013.csv` jest generowany na podstawie niezmienionej mapy `1010` (wymaganej do aktualizacji). Mapy OBF nie zmieniono. Wynik testow i SHA-256 paczki: `docs/RELEASE_1013.md`.

## Rozwój 1.0.14
Po odtworzeniu migawki wywołaj kolejno `python3 tools/apply_1013.py worktree` i `python3 tools/apply_1014.py worktree`. Historia obu map 1013/1014 jest zachowana dla aktualizacji starszych instalacji. Go test zawiera regresję dla nie-ASCII w literałach z oryginalnego JAR. Szczegóły: [docs/RELEASE_1014.md](docs/RELEASE_1014.md).

## Rozwój 1.0.15
Po odtworzeniu bazy wykonaj po kolei `python3 tools/apply_1013.py worktree`, `python3 tools/apply_1014.py worktree`, `python3 tools/apply_1015.py worktree`. Zapisano wszystkie historyczne mapy do aktualizacji. Zobacz [docs/RELEASE_1015.md](docs/RELEASE_1015.md).

## Rozwój 1.0.16
Po `python3 tools/restore_snapshot.py` wykonaj po kolei `tools/apply_1013.py`, `tools/apply_1014.py`, `tools/apply_1015.py`, `tools/apply_1016.py` z argumentem `worktree`. Obie historyczne mapy OBF/API sa zachowane dla upgrade. Zobacz [docs/RELEASE_1016.md](docs/RELEASE_1016.md).

## Rozwój 1.0.17
Po odtworzeniu bazy wykonaj w kolejnosci `tools/apply_1013.py` do `tools/apply_1017.py` z argumentem `worktree`. Zweryfikowano odtwarzalnosc 1000 plikow zrodlowych. Zobacz [docs/RELEASE_1017.md](docs/RELEASE_1017.md).

## Rozwój 1.0.18
Po odtworzeniu bazy wykonaj `tools/apply_1013.py` do `tools/apply_1018.py` kolejno z argumentem `worktree`, a nastepnie `python3 tools/verify_subject_pronouns_1018.py worktree`. Inne zaimki i `Misc.STORY` wymagaja audytu. Wyniki: [docs/RELEASE_1018.md](docs/RELEASE_1018.md).

## Rozwój 1.0.19
Wykonaj kolejno `tools/apply_1013.py`–`tools/apply_1019.py` na przywroconym `worktree`, nastepnie `tools/verify_1019_tooltip.py`. Nowy niezalezny audyt 81 odwolan `Misc.STORY` i 219 wywolan metod zaimkowych: `tools/audit_dynamic_calls_1019.py`. [Raport](docs/RELEASE_1019.md).

## Rozwój 1.0.20
Po odtworzeniu snapshotu wykonaj nakladki 1013–1020 w kolejnosci i `python3 tools/verify_1020_dialogs.py worktree`. Nowy `tools/audit_exact_literals_1020.py` porownuje faktyczne `CONSTANT_String` oryginalnych JAR z mapami bez blednych escape'ow z `javap`. Wyniki: [docs/RELEASE_1020.md](docs/RELEASE_1020.md).

## Rozwój 1.0.21
Po odtworzeniu bazy uruchom kolejno overlaye 1013–1021, potem `python3 tools/verify_1021_delta.py worktree`. Audyt wzgledem prywatnego oryginalnego `data.rar` obejmuje **870 plikow**: 833 struktur, 18 CSV i 19 TXT do recenzji semantycznej. Kod: `tools/verify_source_fields_1021.py`; testy zabezpieczen: `tools/test_source_fields_1021.py`. [Szczegoly](docs/RELEASE_1021.md).
