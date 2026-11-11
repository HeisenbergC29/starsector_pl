# Starsector PL ASCII — polonizacja Starsector 0.98a-RC8

**Stan (1.0.12):** rozwijana polonizacja, docelowe wydanie **1.1** NIE jest jeszcze ukończone.

Repozytorium ma umożliwić innemu agentowi odtworzenie i kontynuowanie pracy bez historii rozmowy.

**Aktualny snapshot źródeł: 1.0.12** (870 plików danych, nowa polonizacja misji m2/m3; JAR mapy bez zmian). Wydanie 1.1 jeszcze nie ukończone.

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
