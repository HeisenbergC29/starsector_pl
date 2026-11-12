# Audyt semantyczny 1.1: status starszych map API (stan 1.0.29)

Nowy deterministyczny skaner `tools/audit_semantic_queue_1030.py` utworzyl **prywatna kolejke 3659 pozycji** z klasycznymi statusami DRAFT/OPTIONAL. Dla kazdej pozycji zapisuje metode identyfikacji, klase, tekst zrodlowy, polska wersje, heurystyczne ryzyka oraz status przegladu (`UNREVIEWED`). **Samo utworzenie kolejki nie jest weryfikacja tlumaczen.** Nie opublikowano tekstow komercyjnych w publicznym repo.

Wersja 1.0.29, liczby mapy API:

- `OPTIONAL_PATCHER_NOT_GAME_TESTED`: **2295**
- `DRAFT_ONLY_NOT_INSTALLED`: **1008**
- `DRAFT_OPTIONAL_JAR_NOT_TESTED_IN_GAME`: **356**
- Razem: **3659**; etykieta `DRAFT_ONLY_NOT_INSTALLED` jest historycznie mylaca, bo status nie jest filtrem instalacji.
- Oddzielna grupa `OFFLINE_VERIFIED_OPTIONAL_PATCH` zawiera 184 wpisy, nieuwzglednione w tej 3659-elementowej kolejce. Nazwa statusu nie zastępuje testu w grze.

Raport heurystyczny wykazal **2 roznice granicznych przecinkow**. Oba przypadki (angielski przecinek przed `and` pominiety przed polskim `i`) byly juz skontrolowane i zaakceptowane w audycie 1.0.25, nie sa nowymi bledami. Wykryto takze **173 wpisy wymagajace oceny, poniewaz ten sam angielski literal bywa tlumaczony roznie w kilku klasach**. Roznice moga byc calkowicie poprawne kontekstowo, np. odmiana fraz, wiec nie nalezy ich automatycznie ujednolicac. Krotkie fragmenty (<15 znakow) oznaczono do przegladu zdania w calosci, nie do masowej zamiany.

Po usunieciu falszywych alarmow o znaku `%` w procentowych premiach skaner **nie stwierdzil braku znacznikow formatowania** w tej grupie wedlug zastosowanego wzorca. Ten wynik nie zastępuje szerszego audytu `tools/audit_draft_boundaries_1025.py` ani recenzji semantycznej.

Odtworzenie prywatne:

```bash
python3 tools/audit_semantic_queue_1030.py \
  worktree/buildtools/NARZEDZIA_JAR/ZRODLA_EXE_GO/translations/TLUMACZENIA_JAR_1029.csv \
  --private-out /PRIVATE/SEMANTIC_REVIEW_1030_PRIVATE.json \
  --summary-out /PRIVATE/SEMANTIC_REVIEW_1030_SUMMARY.json
```

Publiczny raport licznikow: `docs/SEMANTIC_AUDIT_1030_SUMMARY.json`. Do zamkniecia brakuje recenzji jezykowej rzeczywistych komunikatow, w szczegolnosci sklejanych zdań, nazw, nickname'ow i skrotow. Nie nazywac kolejki recenzja zakonczona.
