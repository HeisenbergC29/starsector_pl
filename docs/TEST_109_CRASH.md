# Awaria 1.0.9 przy starcie — fakt i naprawa

Zrzut: `Fatal: For input string: "lpp_devAddFaithful"`. Log: `java.lang.NumberFormatException` w `Float.parseFloat`, wywolane z `com.fs.starfarer.campaign.rules.Rules`. W innym podejsciu tak samo `gaRR_acceptPirate`. Nie jest to błąd uzytkownika.

Potwierdzenie w oryginalnym OBF: `javap -c -p com.fs.starfarer.campaign.rules.Rules` pokazuje rozbicie stringu `options` po dwukropku. Warianty: 2 pola `ID:tekst`, 3 pola `numeric_order:ID:tekst`; nie-numeryczna pierwsza czesc przy trzech polach jest przekazywana do `Float.parseFloat` i wywala wyjatek.

W `rules.csv` wersji 1.0.10 wykryto **38** blednych pozycji wsrod **7371** opcji (przykladowo `lpp_devAddFaithful:ustaw postawe gracza: wierny`). W 1.0.11 wymieniono w nich tylko dodatkowe dwukropki tekstu na ` - `. Zachowano ID oraz skrypty i CRLF. Po zmianie parser testowy: **0/7371 nieprawidlowych**. Zmieniony tylko jeden z 868 plikow danych.

Odtwarzalny test: `python3 worktree/maintenance/check_rules_options.py worktree/mod/data/campaign/rules.csv`. Naprawa: `worktree/maintenance/fix_rules_option_colons.py` (wejscie rules 1.0.10; nie uruchamiaj ponownie na 1.0.11).

W logu wystepuja tez komunikaty `Ship hull spec [flare] not found` i `[module_hightech_decor]` — sa osobnymi pozycjami do audytu; nie stwierdzono, ze powodowaly opisany wyjatek.
