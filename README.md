# QGIS territory analyst

Wyświetla statystyki dla poszczególnych grup obiektów i uaktualnia je, gdy przynależność obiektu do grupy zostaje zmieniona lub gdy pojedyncze wartości zostaną zmienione.

- Czyta dane z warstw wektorowych dodanych do okna mapy
- Tworzy statystyki dla kolumn z numerycznym typem danych


### Instrukcja:	
1) dodaj warstwę wektorową do mapy

2) wybierz warstwę na panelu po prawej stronie i kliknij *Importuj*

  * Jeśli dodano nowy plik do mapy, należy wyłączyć i włączyć wtyczkę, aby uaktualnić listę warstw

3) wyświetlą się dostępne pola z danymi numerycznymi, zaznacz wybrane i wybierz z dostępnych opcji *Suma* lub *Średnia*

  * Dane muszą być pozbawione wartości `NULL`
  * Jeśli dodano nowe kolumny, należy jeszcze raz kliknąć "Importuj" przy danej warstwie

4) u góry lewego panelu wybierz, wg której kolumny grupować dane

  * Prawy panel można schować przyciskiem `>>`

5) kliknij **Odśwież**

  * Po zmianach danych w tabeli atrybutów należy kliknąć "Odśwież" żeby uaktualnić tabelę

6) pokaż wykres klikając **Wykres**

  * Wykres zostanie stworzony dla tej kolumny z danymi, w której kliknięta jest jakakolwiek komórka


##### Dodatkowe informacje
- Sortować można klikając na nagłówki kolumn
- Klikając na nagłówek wiersza zaznaczają się atrybuty z danej grupy
- Aby usunąć zaznaczenie wystarczy kliknąć "Odśwież"