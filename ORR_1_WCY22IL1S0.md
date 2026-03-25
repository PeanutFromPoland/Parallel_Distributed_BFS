# Szablon sprawozdania

## Laboratoria: Obliczenia Równoległe i Rozproszone

> Dokument jest przeznaczony do stopniowego uzupełniania w trakcie całego cyklu zajęć laboratoryjnych. Celem nie jest długi opis, tylko czytelny zapis decyzji, wyników i wniosków.

## 0. Informacje podstawowe

- **Temat zadania:** BFS
- **Skład zespołu:** Marcin Laskowski, Mateusz Klimas
- **Grupa laboratoryjna:** WCY22IL1S0
- **Język programowania:** Python
- **Główna technologia / biblioteka:** NumPy


## 1. Problem i zakres

### 1.1. Problem w 2-3 zdaniach

Przeszukanie grafów wszerz, których liczba wierzchołków wynosi co najmniej $10^4$ o zróżnicowanej budowie (model ER, model BA, Bianconi-Barabasi, planarny, grid, etc.)

### 1.2. Wejście

- Format danych wejściowych:

    Wejście powinno zawierać:
    - liczbę wierzchołków $n$ (numeracja od $1$ do $n$),
    - liczbę krawędzi $m$,
    - listę krawędzi,
    - wierzchołek startowy $s$.

- Przykład wejścia: 
    ```
    5 7
    1 4
    1 5
    4 5
    4 2
    4 3
    5 3
    1
    ```
- Dane pochodzą z autorskiej implementacji generatora grafów.

### 1.3. Wynik

Program zwraca listę dystansów wierzchołków od wierzchołka początkowego w formie tablicy liczb całkowitych 

### 1.4. Kryterium poprawności

- Sposób sprawdzania poprawności:

    Implementacja jest poprawna, jeżeli dla każdego wierzchołka v zachodzi:

    - $dist[s] = 0$,
    - dla każdego wierzchołka osiągalnego $dist[v]$ jest równe długości najkrótszej ścieżki od $s$ do $v$,
    - $dist[v] = dist[parent[v]] + 1$,
    wszystkie wierzchołki na poziomie $k$ są odkrywane przed przejściem do poziomu $k+1$.

    W wersjach równoległej i rozproszonej poprawność oznacza:

    - zgodność tablicy $dist$ z wersją sekwencyjną,
    - poprawny podział na poziomy BFS,
    - brak pominiętych osiągalnych wierzchołków,
    - brak fałszywie oznaczonych odległości.

    Minimalny przypadek testowy: 
    ```
    5 7
    1 4
    1 5
    4 5
    4 2
    4 3
    5 3
    1
    ```
    Oczekiwany wynik dla małego przykładu:
    ```
    dist: 0 2 2 1 1
    *kolejność przejścia wierzchołków: 1 4 5 2 3*
    ```

### 1.5. Minimalny zakres zadania

#### 1.5.1. Część wspólna dla wszystkich wersji

Każda implementacja powinna:

- przyjmować graf oraz wierzchołek startowy,
- wyznaczać odległość od wierzchołka startowego do  wszystkich osiągalnych wierzchołków,
- poprawnie obsługiwać grafy:
    - rzadkie i gęste,
    - małe i duże,
    - z cyklami i bez cykli.

#### 1.5.2. Wersja sekwencyjna

- klasyczna implementacja BFS oparta na kolejce FIFO,
- reprezentacja grafu jako lista sąsiedztwa,
- obsługa pojedynczego źródła,
- zwrócenie tablicy odległości.

Wersja sekwencyjna stanowi implementację referencyjną, względem której należy porównywać poprawność pozostałych wersji.

#### 1.5.3. Wersja równoległa

- implementacja BFS dla pamięci współdzielonej,
- wykorzystanie wielu wątków lub mechanizmu równoległości na jednej maszynie,
- równoległe przetwarzanie frontieru danego grafu spójnego algorytmem BFS,
- synchronizacja między kolejnymi poziomami,
- unikanie wielokrotnego odwiedzenia tego samego wierzchołka.

Należy wykonać:

- poprawne wyznaczanie poziomów BFS,
- pomiar czasu dla różnych liczb wątków,
- analizę speedupu względem wersji sekwencyjnej.

#### 1.5.4. Wersja rozproszona

- implementacja BFS działająca na wielu procesach,
- podział grafu między procesy,
- wymiana informacji o nowo odkrytych wierzchołkach między procesami,
- synchronizacja kolejnych poziomów BFS,
- obsługa komunikacji międzyprocesowej.

Dopuszczalny model realizacji:

- MPI lub inny model pamięci rozproszonej.

Należy wykonać:

- podział zbioru wierzchołków lub krawędzi między urządzenia,
- przekazywanie informacji o frontierze między urządzeniami,
- poprawne wyznaczanie odległości globalnych,
- pomiar czasu działania dla różnych liczb urządzeń,
- ocenę skalowalności i kosztu komunikacji.

### 1.6. Czego świadomie nie robimy

- Nie uwzględniamy wag krawędzi i wierzchołków
- Nie implementujemy algorytmu dla grafów niespójnych

## 2. Ryzyka na starcie

| Ryzyko | Dlaczego jest istotne | Jak będzie ograniczane |
| --- | --- | --- |
| [uzupełnić] | [uzupełnić] | [uzupełnić] |
| [uzupełnić] | [uzupełnić] | [uzupełnić] |

## 3. Plan danych i skali problemu

### 3.1. Dane wejściowe

| Zestaw | Opis | Rozmiar | Do czego służy |
| --- | --- | --- | --- |
| Small | [uzupełnić] | [uzupełnić] | test poprawności |
| Medium | [uzupełnić] | [uzupełnić] | pierwszy benchmark |
| Large | [uzupełnić] | [uzupełnić] | analiza skalowania |

### 3.2. Parametry skalowania

- Co będzie zwiększane: [np. liczba rekordów / liczba prób / rozmiar obrazu / liczba zadań]
- Jakie poziomy skali będą testowane: [uzupełnić]

## 4. Wersja sekwencyjna

### 4.1. Opis rozwiązania

[krótki opis logiki wersji referencyjnej]

### 4.2. Sposób uruchomienia

```bash
# [uzupełnić]
```

### 4.3. Test poprawności

- Jak uruchomić test: [uzupełnić]
- Wynik testu: [uzupełnić]

### 4.4. Ograniczenia baseline'u

- [uzupełnić]
- [uzupełnić]

## 5. Plan wersji równoległej

### 5.1. Co dokładnie będzie równoleglone

[opis fragmentu obliczeń, który ma być podzielony]

### 5.2. Jednostka pracy

- Jednostka pracy: [uzupełnić]
- Dlaczego ten podział ma sens: [uzupełnić]

### 5.3. Scalanie wyników

[opis sposobu łączenia wyników częściowych]

### 5.4. Przewidywane narzuty

- synchronizacja: [mała / średnia / duża + komentarz]
- kopiowanie danych: [mała / średnia / duża + komentarz]
- start workerów / procesów: [mały / średni / duży + komentarz]

## 6. Wersja równoległa

### 6.1. Opis implementacji

[krótki opis finalnego wariantu parallel]

### 6.2. Konfiguracje testowe

| Konfiguracja | Liczba workerów / wątków / procesów | Uwagi |
| --- | --- | --- |
| C1 | [uzupełnić] | [uzupełnić] |
| C2 | [uzupełnić] | [uzupełnić] |
| C3 | [uzupełnić] | [uzupełnić] |

### 6.3. Poprawność względem baseline'u

- Czy wynik zgadza się z wersją sekwencyjną: [tak / nie]
- Jak to sprawdzono: [uzupełnić]

### 6.4. Pierwsze obserwacje

- [uzupełnić]
- [uzupełnić]

## 7. Plan wersji rozproszonej

### 7.1. Architektura

- coordinator / scheduler: [uzupełnić]
- worker: [uzupełnić]
- co jest wysyłane do workera: [dane / parametry / opis zadania]
- co wraca z workera: [uzupełnić]

### 7.2. Dlaczego to jest naprawdę wariant rozproszony lub distributed-like

[opis miejsca występowania jawnej komunikacji, serializacji albo task shipping]

### 7.3. Partie pracy

- Jak duże są partie: [uzupełnić]
- Dlaczego wybrano taki rozmiar: [uzupełnić]

### 7.4. Przewidywane koszty

- serializacja: [uzupełnić]
- komunikacja: [uzupełnić]
- start workerów: [uzupełnić]
- scalanie wyników: [uzupełnić]

## 8. Wersja rozproszona / distributed-like

### 8.1. Opis implementacji

[krótki opis wariantu końcowego]

### 8.2. Sposób uruchomienia

```bash
# [uzupełnić]
```

### 8.3. Poprawność względem baseline'u

- Czy wynik zgadza się z wersją sekwencyjną: [tak / nie]
- Jak to sprawdzono: [uzupełnić]

### 8.4. Ograniczenia środowiska

- [uzupełnić]
- [uzupełnić]

## 9. Benchmark i analiza wyników

### 9.1. Środowisko uruchomieniowe

- system / runtime: [uzupełnić]
- CPU / RAM: [uzupełnić]
- lokalnie / Codespaces / Colab / inne: [uzupełnić]
- biblioteki i wersje: [uzupełnić]

### 9.2. Zasady benchmarku

- Czy wszystkie wersje używają tych samych danych: [tak / nie]
- Liczba powtórzeń: [uzupełnić]
- Czy kontrolowana jest losowość: [tak / nie / nie dotyczy]
- Jak mierzony jest czas: [uzupełnić]

### 9.3. Wyniki

| Rozmiar danych / liczba zadań | Seq | Parallel C1 | Parallel C2 | Distributed C1 | Distributed C2 | Uwagi |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| [uzupełnić] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| [uzupełnić] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| [uzupełnić] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### 9.4. Dodatkowe metryki

Jeśli dotyczy:

- speedup,
- efficiency,
- koszt startu workerów,
- koszt serializacji,
- jakość wyniku / błąd przybliżenia.

| Metryka | Wartość | Komentarz |
| --- | --- | --- |
| [uzupełnić] | [uzupełnić] | [uzupełnić] |
| [uzupełnić] | [uzupełnić] | [uzupełnić] |

### 9.5. Interpretacja wyników

#### Co rzeczywiście przyspiesza

[uzupełnić]

#### Gdzie pojawia się największy narzut

[uzupełnić]

#### Kiedy dodatkowa złożoność ma sens

[uzupełnić]

#### Kiedy dodatkowa złożoność jest przerostem formy nad treścią

[uzupełnić]

## 10. Peer review i poprawki

### 10.1. Otrzymana recenzja od innego zespołu

- Zespół recenzujący: [uzupełnić]
- Najważniejsze uwagi: [uzupełnić]

### 10.2. Wprowadzone poprawki

| Uwaga | Czy została wdrożona? | Co zmieniono |
| --- | --- | --- |
| [uzupełnić] | [tak / nie] | [uzupełnić] |
| [uzupełnić] | [tak / nie] | [uzupełnić] |

## 11. AI use log

| Data / etap | Do czego użyto AI | Co zostało przyjęte | Co poprawiono ręcznie |
| --- | --- | --- | --- |
| [uzupełnić] | [uzupełnić] | [uzupełnić] | [uzupełnić] |
| [uzupełnić] | [uzupełnić] | [uzupełnić] | [uzupełnić] |

## 12. Uruchomienie i reprodukowalność

### 12.1. Minimalna instrukcja uruchomienia

```bash
# 1. [uzupełnić]
# 2. [uzupełnić]
# 3. [uzupełnić]
```

### 12.2. Struktura repozytorium / plików

- `src/` lub odpowiednik: [uzupełnić]
- `data/` lub odpowiednik: [uzupełnić]
- skrypty benchmarkowe: [uzupełnić]
- test poprawności: [uzupełnić]

## 13. Wnioski końcowe

### 13.1. Najkrótsze podsumowanie w 3 zdaniach

[uzupełnić]

### 13.2. Co działa dobrze

- [uzupełnić]
- [uzupełnić]

### 13.3. Co nie działa lub działa gorzej niż oczekiwano

- [uzupełnić]
- [uzupełnić]

### 13.4. Najważniejsza lekcja techniczna

[uzupełnić]

## 14. Checklista przed oddaniem

- [ ] Temat, wejście, wyjście i kryterium poprawności są jasno opisane.
- [ ] Istnieje działający baseline sekwencyjny.
- [ ] Istnieje test poprawności lub inny wiarygodny sposób weryfikacji wyniku.
- [ ] Wersja równoległa rozwiązuje ten sam problem co wersja sekwencyjna.
- [ ] Wersja rozproszona lub distributed-like rozwiązuje ten sam problem co baseline.
- [ ] Wszystkie porównania wykonano na porównywalnych danych.
- [ ] W benchmarku użyto kilku rozmiarów danych lub liczby zadań.
- [ ] W benchmarku użyto kilku konfiguracji wykonania.
- [ ] Wnioski opisują nie tylko wynik, ale też źródła narzutu.
- [ ] AI use log został uzupełniony.
- [ ] Da się wskazać minimalny sposób uruchomienia rozwiązania.
