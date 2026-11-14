# Polityka weryfikacji Starsector PL do wydania 1.1

Decyzja uzytkownika z 2026-11-14: **testy w uruchomionej grze beda prowadzone dopiero wtedy, gdy powstanie wersja 1.1**. Nie nalezy uzalezniac ukończenia 1.1 od wczesniejszego gameplay testu. Lista czynnosci do sprawdzenia w grze jest opcjonalnym materialem przygotowywanym dopiero po wydaniu 1.1.

## Nadal obowiazuja przed 1.1

- Przeglad i rzeczywiste tlumaczenie wszystkich tekstow widocznych dla gracza, lacznie ze skrotami i akronimami z tlumaczonym rozwinięciem; ochrona identyfikatorow technicznych, kodu i osobowych nazw wlasnych.
- Kontrola poprawnego skladania dynamicznych tekstow, liczby, interpunkcji, zmiennych, wyborow i niezaleznej odmiany wstawianych nazw.
- Audyt oryginalnych stalych i uzyc JVM; nie zmieniac semantyki kodu ani zapisanych stanów gry przy podmianie tekstow.
- Automatyczna kontrola CSV/JSON, poprawnosci danych, map i hashy; testy negatywne, regresji, kompilacja instalatora i sprawdzenie paczki ZIP/CRC.
- Testy konwersji/instalacji patchera na prywatnych oryginalnych JAR: fresh=upgrade, powtorzenie operacji, rollback, odrzucanie uszkodzonych plikow. To sa testy narzedzi, a nie testy uruchomionej gry.

## Dopiero po przygotowaniu i wydaniu 1.1

- Rzeczywiste uruchomienie Starsector na Windows, przejscie interfejsu, dialogow, misji, ekranow kolonii, walki, komunikatow i losowych zdarzen.
- Analiza ewentualnych defektow i poprawki wydania 1.1 (np. 1.1.1). Testow tych NIE oznaczac jako wykonane przed ich faktycznym przeprowadzeniem.

Aktualny brak native Windows gameplay nie blokuje wydania **1.1**. Brak kompletnosci tlumaczen lub naruszenie danych/kodu nadal ja blokuje. Wersja 1.0.65 nie jest wersja 1.1.
