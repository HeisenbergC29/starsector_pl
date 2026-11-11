# Wydanie robocze 1.0.12: rzeczywiste zmiany

1. Dwa poprzednio niepodmienione teksty misji: `data/missions/m2/mission_text.txt`, `data/missions/m3/mission_text.txt`. Zachowano techniczny zapis, znaki specjalne i delimitery nowych linii. Nazwy okrętów i uzbrojenia wykorzystują istniejący glosariusz polskiego `ship_data.csv` i `weapon_data.csv`.
2. Stare 868 plików danych **bajtowo bez zmian** w porównaniu do wydania 1.0.11.
3. Instalator ma oznaczenie 1.0.12; mapy OBF/API bez zmian. Testy Go, `go vet`, cross-build Windows x64 i pełny cykl obu oddzielnych patcherów na oryginalnych JAR (preview, apply, restore) PASS. Suma obu przywróconych JAR jest identyczna z oryginałami.
4. 870 plików danych, 11107 rekordów dialogowych i 7371 opcji przeszło test składni; `mod_info.json` ma 41 istniejących wpisów `replace`. Archiwum ZIP zawiera 873 wpisy, CRC PASS, SHA256 `54f2222355dc6ab56c69a77d6a968696fb586a4b83e5757f72c8664852f1d78a`.
5. Brak natywnego uruchomienia EXE na Windows i uruchomienia gry w tym etapie. Polonizacja 1.1 nadal nieukończona.