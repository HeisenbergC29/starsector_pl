# Audyt danych 1.0.11 — zakres zmian i zabezpieczenia

Źródło porównania: `data.rar` przesłane prywatnie przez użytkownika (oryginalne `data/campaign/rules.csv`), a lokalizacja: snapshot 1.0.11 z `snapshots/`.

- `rules.csv`: 11107 rekordów, kolumny `id,trigger,conditions,script,text,options,notes` niezmienione strukturalnie.
- `text`: 6735 rekordów ma inne wartości niż oryginał.
- `options`: 5577 rekordów ma inne wartości niż oryginał.
- `id`, `trigger`, `conditions`, `notes`: nie wykryto zmian wartości.
- **Wyjątek:** pięć rekordów ma zmieniony argument tekstowy w polu `script`, wyłącznie w wywołaniach `SetTextHighlights` (`Transverse Jump` → `Skok Poprzeczny`/`Skoku Poprzecznego`). Konieczne do właściwego podświetlania przetłumaczonych zwrotów; żadna nazwa polecenia ani instrukcja warunkowa nie została zmieniona.
- W wersji 1.0.10 w 38 tłumaczonych opcjach występowały dodatkowe dwukropki. W 1.0.11 poprawiono je bez zmiany ID; `7371/7371` opcji przechodzi test formatu parsera.
- Wszystkie 868 plików w `data/` są ASCII. `mod_info.json`: 41 wpisów `replace`, bez duplikatów, każdy wskazuje istniejący plik.

Nowy `tools/check_project.py` (uruchamiany w CI) sprawdza: liczbę danych, ASCII, pełną obecność plików `replace`, strukturę i liczbę rekordów oraz składnię wszystkich opcji dialogowych. Test negatywny celowo wprowadza nieprawidłowy dwukropek i wymaga błędu walidacji.

**Ograniczenie:** testy statyczne i kompilacja EXE w Linuksie nie zastępują uruchomienia na Windows ani testu gry. Nie dowodzą pełnego pokrycia tłumaczeń dla 1.1.