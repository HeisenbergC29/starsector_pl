# STATUS 2026-11-11

- Bazowe wydanie **1.0.10**: 868 plikow danych, mapy Java 3116 OBF / 5040 API (liczby podmian, nie procent ukonczenia).
- Test uzytkownika na 1.0.9: gra nie startuje; `NumberFormatException` w parserze rules z ciagami `lpp_devAddFaithful`, a w innym podejsciu `gaRR_acceptPirate`.
- Wydanie **1.0.11**: poprawiono 38 nielegalnych dwukropkow w opcjach `rules.csv`, wszystkie 7371 opcji zwalidowane (0 bledow). Po porownaniu z 1.0.10 tylko `data/campaign/rules.csv` zostal zmieniony. Patchery JAR maja niezmienione mapy 1.0.10.
- `1.0.11` minimalny ZIP stworzony poza GitHub: SHA256 `2c733c171c311c79365fe3b064876d87a131b7f089669b87909069320a1fee00` (871 plikow). Zbudowany instalator PE32+ x64; testy jednostkowe Go PASS; **nie przetestowano natywnie Windows ani uruchomienia gry 1.0.11**.
- GitHub przechowuje kompletny stan **wlasnych i zmodyfikowanych plikow projektowych**, w 7 czesciach archiwum zstd: `snapshots/*`. Odtworz `python3 tools/restore_snapshot.py`.
- Nie ma w nim oryginalnych plikow gry, co jest celowym ograniczeniem dystrybucyjnym.

**DO UKONCZENIA 1.1:** szczegolowy audyt wszystkich pozostalych literałów Java i nazw/skrotow; kontrola niepodmienionych oryginalnych danych; testy rzeczywistego dzialania i wyswietlania. Poprzednia lista heurystyczna ~652 API / 896 OBF — zawiera potencjalne komunikaty techniczne, to NIE jest potwierdzona liczba brakow.

Pierwszy priorytet: uzytkownik powinien sprawdzic start gry po poprawce `rules.csv`; na blad reagowac kolejnym konkretnym audytem.
