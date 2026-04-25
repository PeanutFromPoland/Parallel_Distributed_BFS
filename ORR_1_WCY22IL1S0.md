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

## 2. Ryzyka na starcie

| Ryzyko                                    | Dlaczego jest istotne                                                                          | Jak będzie ograniczane                                                                                               |
|-------------------------------------------|------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Problemy z komunikacją pomiędzy procesami | Bardzo znacząco może spowolnić pracę algorytmu, czyniąc implementację rozproszoną bezużyteczną | Procesy dostaną osobne części grafu, aby zostały one osobno przetworzone, w celu ograniczenia komunikacji do minimum |

## 3. Plan danych i skali problemu

### 3.1. Dane wejściowe

| Zestaw | Opis                                                              | Rozmiar                    | Do czego służy |
| --- |-------------------------------------------------------------------|----------------------------| --- |
| Small | Grafy losowe, Small World, bezskalowe oraz typu grid + kombinacje | Kilkadziesiąt wierzchołków | test poprawności |
| Medium | Grafy losowe, Small World, bezskalowe oraz typu grid + kombinacje | Kilkaset wierzchołków      | pierwszy benchmark |
| Large | Grafy losowe, Small World, bezskalowe oraz typu grid + kombinacje | Kilka tysięcy wierzchołków | analiza skalowania |

### 3.2. Parametry skalowania

- Co będzie zwiększane: Liczba wierzchołków
- Jakie poziomy skali będą testowane: kilkadziesiąt, kilkaset i kilka tysięcy wierzchołków

## 4. Wersja sekwencyjna

### 4.1. Opis rozwiązania

Algorytm BFS wybiera pierwszy wierzchołek z listy sąsiedztwa 
i od tego miejsca odwiedza po kolei swoich sąsiadów. 
Czynność powtarzana jest aż do odwiedzenia ostatniego wierzchołka. 
Jeżeli zostałyby wierzchołki nieodwiedzone, to 

### 4.2. Sposób uruchomienia

```bash
python baseline.py
```

### 4.3. Test poprawności

Uruchomienie testu
```bash
python generate_graphs.py # jeżeli nie wygenerowano grafów
python main.py
```
Wynik testu (komunikat podsumowujący): 
```bash
----------------------------------------------------------------------------------------------------

  Łączny czas BFS (spójne):      1.1303s
  Łączny czas BFS (niespójne):   2.1735s
  Łączny czas BFS (wszystkie):   3.3038s
  Liczba grafów:                 60

  [OK] WSZYSTKIE TESTY POPRAWNOSCI ZALICZONE
====================================================================================================

```

### 4.4. Ograniczenia baseline'u

- Algorytm ten powinien być używany dla grafów nieskierowanych, ponieważ krawędzie skierowane mogą zostać potraktowane jako krawędzie nieistniejące
## 5. Plan wersji równoległej

### 5.1. Co dokładnie będzie równoleglone

Równoleglona będzie faza ekspansji bieżącego frontieru w pojedynczej warstwie BFS. Frontier to zbiór wierzchołków należących do bieżącej warstwy BFS, czyli tych,
które zostały odkryte w poprzednim kroku i których sąsiedzi będą teraz przeglądani.
Dla każdego wierzchołka z aktualnego frontieru niezależnie przeglądana jest jego lista
sąsiedztwa i wykonywana jest próba odwiedzenia sąsiadów.

Ponieważ rozważane są również grafy niespójne, algorytm nie kończy działania po
opróżnieniu frontieru dla jednej składowej. W takiej sytuacji wyszukiwany jest kolejny
nieodwiedzony wierzchołek, od którego rozpoczynany jest BFS dla następnej składowej.

Pętla po warstwach BFS w obrębie jednej składowej pozostaje sekwencyjna, ponieważ kolejna
warstwa może zostać wyznaczona dopiero po pełnym przetworzeniu warstwy bieżącej. Równoległość
występuje wewnątrz danej warstwy przez podział pracy między wątki zgodnie z partycjonowaniem 1D.

### 5.2. Jednostka pracy

- Jednostka pracy: fragment bieżącego frontieru lub odpowiadający mu zakres wierzchołków i ich list sąsiedztwa przypisany do danego wątku.
- Dlaczego ten podział ma sens: w obrębie jednej warstwy operacje na poszczególnych wierzchołkach frontieru są w dużej mierze niezależne, więc można je przetwarzać równolegle. Partycjonowanie 1D upraszcza rozdział pracy, dobrze współpracuje ze wspólną pamięcią i pozwala ograniczyć koszt zarządzania danymi.

### 5.3. Scalanie wyników

Każdy wątek podczas przetwarzania swojej części frontieru tworzy lokalną listę wierzchołków
należących do `next_frontier`. Po zakończeniu pracy nad bieżącą warstwą lokalne bufory są
łączone w jeden globalny frontier następnego poziomu.

Po opróżnieniu `next_frontier` dla danej składowej sprawdzane jest, czy istnieją jeszcze
nieodwiedzone wierzchołki. Jeśli tak, jeden z nich inicjuje nowy frontier i przetwarzanie
jest kontynuowane dla kolejnej składowej.

Aby uniknąć wielokrotnego dodania tego samego wierzchołka, współdzielona tablica `visited`
jest aktualizowana w sposób zsynchronizowany. Tylko wątek, który jako pierwszy oznaczy
wierzchołek jako odwiedzony, dodaje go do lokalnego `next_frontier`.

### 5.4. Przewidywane narzuty

- synchronizacja: **średnia** — potrzebna jest synchronizacja przy wyznaczaniu kolejnych warstw oraz przy oznaczaniu wierzchołków jako odwiedzonych; dodatkowy koszt może pojawić się przy przechodzeniu między składowymi
- kopiowanie danych: **mała** — graf pozostaje we wspólnej pamięci, a scalaniu podlegają głównie lokalne bufory `next_frontier`
- start workerów / procesów: **mały** — przy zastosowaniu stałej puli wątków koszt uruchomienia jest jednorazowy; kolejne składowe mogą być przetwarzane bez ponownego tworzenia workerów

## 6. Wersja równoległa

### 6.1. Opis implementacji

Wersja równoległa wykorzystuje moduł `multiprocessing` (procesy, nie wątki) w celu osiągnięcia
rzeczywistej równoległości obliczeń, omijając ograniczenia GIL w Pythonie. Implementacja składa się
z dwóch głównych plików: `src/parallel.py` (logika BFS) oraz `main.py` (orkiestracja benchmarku).

**Reprezentacja grafu — format CSR (Compressed Sparse Row).** Graf wejściowy (słownik list sąsiedztwa)
konwertowany jest na trzy tablice: `offsets` (przesunięcia, długość $n+1$), `edges` (spłaszczona lista
sąsiadów) oraz `visited` (tablica odwiedzeń). Tablice te są przechowywane w pamięci współdzielonej
(`RawArray` z modułu `ctypes`), co pozwala procesom roboczym odczytywać dane grafu bez kopiowania.

**Cykl życia puli procesów.** Kontekst równoległy (pula procesów + pamięć współdzielona) tworzony jest
jednorazowo przez funkcję `create_parallel_context()` przed przetworzeniem wszystkich grafów. Pamięć
współdzielona jest pre-alokowana do rozmiarów maksymalnych (`MAX_NODES = 15 000`, `MAX_EDGES = 15 000 000`)
i używana ponownie dla kolejnych grafów — dla każdego grafu nadpisywane są jedynie potrzebne fragmenty tablic.
Po przetworzeniu wszystkich grafów pula zamykana jest przez `destroy_parallel_context()`.

**Algorytm BFS — podział frontieru (partycjonowanie 1D).** W każdej warstwie (poziomie) BFS bieżący
frontier dzielony jest na $P$ fragmentów (chunków), gdzie $P$ to liczba procesów roboczych. Każdy
worker otrzymuje swój fragment i dla każdego wierzchołka z fragmentu przegląda listę sąsiadów w
pamięci współdzielonej, zwracając listę kandydatów — sąsiadów, którzy wg odczytu tablicy `visited`
nie zostali jeszcze odwiedzeni. Proces główny zbiera listy kandydatów, deduplikuje je (filtruje
wierzchołki już oznaczone jako odwiedzone) i buduje frontier następnego poziomu.

**Próg równoległości (PARALLEL_THRESHOLD).** Jeżeli rozmiar frontieru jest mniejszy niż próg
(`max(512, num_workers × 32)`), warstwa przetwarzana jest sekwencyjnie w procesie głównym,
unikając narzutu komunikacji międzyprocesowej (IPC) dla małych warstw.

**Obsługa grafów niespójnych.** Po opróżnieniu frontieru dla danej składowej algorytm przeszukuje
tablicę `visited` w poszukiwaniu kolejnego nieodwiedzonego wierzchołka i rozpoczyna nowy BFS.

**Kluczowe decyzje projektowe:**
- Workery TYLKO CZYTAJĄ z pamięci współdzielonej → brak locków, brak deadlocków
- Deduplikacja i zapis do `visited`/`dist` odbywa się WYŁĄCZNIE w procesie głównym → gwarancja poprawności
- Pula procesów tworzona jest RAZ i używana ponownie dla wielu grafów → jednorazowy koszt startu workerów

### 6.2. Konfiguracje testowe

| Konfiguracja | Liczba workerów / wątków / procesów | Uwagi |
| --- | --- | --- |
| C1 | 12 procesów | pełne obciążenie CPU (12 rdzeni), `PARALLEL_THRESHOLD = 512` |

### 6.3. Poprawność względem baseline'u

- Czy wynik zgadza się z wersją sekwencyjną: **tak**
- Jak to sprawdzono: Dla każdego z 60 grafów testowych (12 spójnych + 48 niespójnych) porównano wynik równoległego BFS z oczekiwanymi wynikami wygenerowanymi przez `generate_graphs.py`. Weryfikacja obejmuje: liczbę składowych spójności, wierzchołek startowy każdej składowej, zbiór wierzchołków w składowej oraz tablicę odległości. Wynik testu: `[OK] WSZYSTKIE TESTY POPRAWNOSCI ZALICZONE`.

### 6.4. Pierwsze obserwacje

- Dla dużych, gęstych grafów (≥ 1 mln krawędzi) osiągnięto przyspieszenie 2.5–3.6× przy 12 procesach (np. `random/large`: 5000 wierzchołków, 7.5 mln krawędzi → przyspieszenie **3.58×**)
- Dla małych i rzadkich grafów (< 500 wierzchołków, < 20 tys. krawędzi) przyspieszenie wynosi 0.5–1.2× — narzut IPC (`pool.map`) i serializacji dominuje nad zyskiem z równoległości, gdy czas sekwencyjnego BFS wynosi < 0.01 s
- Łączny przyspieszenie dla wszystkich 60 grafów: **2.63×** (łączny czas sekwencyjny: 2.38 s, równoległy: 0.91 s)
- Krytycznym czynnikiem wydajności okazał się koszt tworzenia puli procesów — na Windows (metoda `spawn`) utworzenie `mp.Pool(12)` trwa ~5–10 s. Pierwotna implementacja tworzyła pulę od nowa dla każdego grafu, co dawało łączny narzut ~300–600 s na 60 grafów. Po przeniesieniu tworzenia puli do jednorazowej inicjalizacji czas łączny spadł z 604.5 s do 0.9 s

## 7. Plan wersji rozproszonej

### 7.1. Architektura

- **coordinator (proces główny):** Wczytuje graf niespójny, identyfikuje składowe spójności (za pomocą BFS/DFS na pełnym grafie lub — w wersji zoptymalizowanej — korzystając z zakresów numeracji wierzchołków wynikających z generatora grafów niespójnych). Dla każdej składowej wyodrębnia podgraf (listę sąsiedztwa ograniczoną do wierzchołków składowej) i wysyła go jako niezależne zadanie do wolnego workera. Po zebraniu wyników od wszystkich workerów scala tablice odległości w globalny wynik.

- **worker (proces roboczy):** Odbiera kompletny podgraf (listę sąsiedztwa jednej składowej spójności) wraz z wierzchołkiem startowym. Wykonuje na nim klasyczny, sekwencyjny BFS (kolejka FIFO) i zwraca tablicę odległości `{node: dist}` dla wszystkich wierzchołków w składowej.

- **co jest wysyłane do workera:**
    - podgraf w formie `dict[int, list[int]]` (lista sąsiedztwa danej składowej),
    - wierzchołek startowy `start` (najmniejszy numerycznie wierzchołek w składowej — zachowanie spójne z wersją sekwencyjną i równoległą).

- **co wraca z workera:**
    - krotka `(start, {node: dist})` — wierzchołek startowy składowej oraz słownik odległości wszystkich wierzchołków od niego.

### 7.2. Dlaczego to jest naprawdę wariant rozproszony lub distributed-like

Implementacja realizuje model **task shipping** charakterystyczny dla systemów rozproszonych:

1. **Jawna serializacja danych** — każdy podgraf (lista sąsiedztwa składowej) jest serializowany przez `pickle` w procesie koordynatora i deserializowany w procesie roboczym. Dane nie są współdzielone w pamięci; worker dostaje własną, niezależną kopię fragmentu grafu.

2. **Brak pamięci współdzielonej** — w odróżnieniu od wersji równoległej (§ 6), workery nie korzystają z `RawArray` ani żadnych struktur w pamięci współdzielonej. Każdy proces roboczy operuje wyłącznie na danych przesłanych mu przez IPC (Inter-Process Communication) — identycznie jak w architekturze master–worker w systemie rozproszonym.

3. **Niezależność workerów** — workery nie komunikują się między sobą ani z koordynatorem w trakcie obliczeń. Każdy worker przetwarza swoją składową od początku do końca, bez potrzeby synchronizacji warstw BFS z innymi procesami. Jest to model **embarrassingly parallel** z perspektywy poszczególnych składowych.

4. **Komunikacja wyłącznie na granicach zadania** — komunikacja zachodzi dwukrotnie: (a) wysyłka zadania (podgraf + start) do workera, (b) odbiór wyniku (tablica odległości). Odpowiada to wzorcowi `scatter → compute → gather` typowemu dla MPI i systemów rozproszonych.

5. **Przenośność na prawdziwy klaster** — architektura jest zaprojektowana tak, aby `mp.Pool` mógł zostać zastąpiony komunikacją sieciową (np. gniazda TCP, MPI `comm.send`/`comm.recv`) bez zmiany logiki algorytmu. Jedyną różnicą byłby transport danych — zamiast IPC na jednej maszynie, przesyłka przez sieć.

### 7.3. Partie pracy

- **Jak duże są partie:** Każda partia pracy to **jeden pełny podgraf spójny** (składowa spójności grafu niespójnego). Rozmiar partii odpowiada liczbie wierzchołków i krawędzi w danej składowej. Dla grafów generowanych przez `generate_inconsistent_graph` z `parts_count=2` oznacza to dwa zadania — każde obejmujące około połowy wierzchołków grafu (z losową wariancją wynikającą z `_partition_vertices`).

- **Dlaczego wybrano taki rozmiar:** Podział na składowe spójności jest naturalną granicą podziału pracy dla BFS — wierzchołki z różnych składowych nie mają wspólnych krawędzi, więc BFS na jednej składowej jest w pełni niezależny od pozostałych. Taki podział:
    - **eliminuje komunikację między workerami** w trakcie obliczeń (brak krawędzi przecinających),
    - **maksymalizuje granularność zadań** — każde zadanie jest wystarczająco duże, aby zamortyzować narzut serializacji i IPC,
    - **gwarantuje poprawność** — worker nie potrzebuje informacji z innych składowych, więc wynik lokalnego BFS jest od razu wynikiem globalnym dla tej części grafu.

### 7.4. Przewidywane koszty

- **serializacja:** **średnia do dużej** — cały podgraf (lista sąsiedztwa) jest serializowany `pickle`-em przy wysyłce do workera, a tablica odległości przy odbiorze. Dla dużych składowych (np. 25 000 wierzchołków z dużą liczbą krawędzi) rozmiar serializowanego obiektu może wynieść kilka–kilkadziesiąt MB. Koszt ten jest ponoszony dwukrotnie na składową (tam i z powrotem).

- **komunikacja:** **mała do średniej** — komunikacja zachodzi wyłącznie na granicach zadań (przed i po BFS), bez wymiany danych w trakcie obliczeń. Dla 2–4 składowych na graf to zaledwie 4–8 operacji IPC na cały benchmark. Wąskim gardłem może być serializacja, nie sam transport.

- **start workerów:** **mały (jednorazowy)** — pula procesów (`mp.Pool`) tworzona jest raz przed przetworzeniem wszystkich grafów (analogicznie do wersji równoległej). Narzut startu procesów (~5–10 s na Windows z metodą `spawn`) jest amortyzowany na wszystkich grafach.

- **scalanie wyników:** **minimalne** — coordinator jedynie zbiera krotki `(start, {node: dist})` od workerów i dołącza je do listy `components`. Nie ma potrzeby deduplikacji ani łączenia nakładających się wyników, ponieważ składowe są rozłączne — wystarczy proste `append`.

## 8. Wersja rozproszona / distributed-like

### 8.1. Opis implementacji

Końcowa wersja rozproszona została umieszczona w katalogu `distributed/` i działa w architekturze
**coordinator-worker** uruchamianej przez Docker Compose. W odróżnieniu od wersji równoległej z § 6
procesy nie współdzielą pamięci. Każdy worker jest osobnym serwisem TCP, a koordynator wysyła mu
kompletne zadanie w postaci podgrafu oraz wierzchołka startowego.

Najważniejsze pliki implementacji:

- `distributed/coordinator/coordinator.py` - główna logika benchmarku, komunikacja z workerami,
  podział grafu na składowe, harmonogram zadań i weryfikacja wyniku,
- `distributed/coordinator/component_detector.py` - detekcja składowych spójności oraz zachłanny
  przydział pracy do workerów,
- `distributed/worker/worker.py` - serwer TCP wykonujący sekwencyjny BFS na otrzymanym podgrafie,
- `distributed/shared/protocol.py` - wspólny protokół komunikacji z nagłówkiem długości wiadomości,
- `distributed/docker-compose.yml` - konfiguracja trzech workerów i koordynatora.

Przepływ działania jest następujący:

1. Koordynator wczytuje graf z katalogu `graphs/`.
2. Dla tego grafu wykonywany jest sekwencyjny BFS, który pełni rolę baseline'u czasowego i
   referencyjnego.
3. Koordynator wykrywa rzeczywiste składowe spójności za pomocą BFS (`detect_components_bfs`).
   Wcześniejsze założenie o wykrywaniu składowych wyłącznie po lukach w numeracji okazało się
   niepoprawne dla wygenerowanych grafów niespójnych, ponieważ ich wierzchołki mogą mieć numerację
   ciągłą mimo rozłącznych składowych.
4. Dla każdej składowej tworzony jest podgraf. Jeżeli graf ma tylko jedną składową, nie wykonuje się
   dodatkowego filtrowania list sąsiedztwa i do workera trafia cały graf.
5. Składowe są przydzielane zachłannie do workerów. Jako wagę zadania przyjęto liczbę krawędzi w
   składowej, ponieważ koszt BFS zależy nie tylko od liczby wierzchołków, ale przede wszystkim od
   liczby przeglądanych list sąsiedztwa.
6. Każdy worker odbiera zadanie przez TCP, wykonuje klasyczny BFS z kolejką FIFO i odsyła słownik
   `{node: dist}`.
7. Koordynator zbiera wyniki, sortuje komponenty według wierzchołka startowego i porównuje je z
   plikiem `*_expected.txt`.

Komunikacja odbywa się przez gniazda TCP. Każda wiadomość ma format:

```text
<4 bajty długości big-endian><payload pickle>
```

W finalnej wersji zamiast JSON zastosowano `pickle`, ponieważ pozwala przesyłać słowniki z kluczami
typu `int` bez kosztownej konwersji `int -> str -> int`. Jest to istotne zwłaszcza dla dużych grafów,
gdzie sam podgraf może zawierać miliony krawędzi.

W pętli BFS nie sortuje się już sąsiadów. Kolejność odwiedzania może się przez to różnić, ale
odległości BFS pozostają takie same, a to one są kryterium poprawności. Dzięki temu wersja
sekwencyjna i rozproszona unikają zbędnego kosztu `sorted(...)` w najczęściej wykonywanej części
algorytmu.

### 8.2. Sposób uruchomienia

```bash
# z katalogu głównego projektu
python generate_graphs.py

# uruchomienie wersji rozproszonej
cd distributed
docker compose up --build --abort-on-container-exit --exit-code-from coordinator
```

Domyślna konfiguracja uruchamia trzy workery:

```yaml
worker-1:5000
worker-2:5000
worker-3:5000
```

Koordynator otrzymuje ich adresy przez zmienną środowiskową `WORKERS`, a katalog z grafami jest
montowany jako wolumen tylko do odczytu:

```yaml
../graphs:/app/graphs:ro
```

### 8.3. Poprawność względem baseline'u

- Czy wynik zgadza się z wersją sekwencyjną: **tak**
- Jak to sprawdzono: dla każdego z 60 grafów testowych wynik wersji rozproszonej porównano z
  oczekiwanymi wynikami zapisanymi w plikach `*_expected.txt`.

Weryfikacja obejmuje:

- liczbę składowych spójności,
- wierzchołek startowy każdej składowej,
- liczbę odwiedzonych wierzchołków,
- odległość `dist` dla każdego wierzchołka.

Po poprawieniu detekcji składowych pełny benchmark Docker Compose zakończył się komunikatem:

```text
[OK] WSZYSTKIE TESTY POPRAWNOSCI ZALICZONE
```

Warto zaznaczyć, że przed poprawką wersja rozproszona nie była poprawna dla grafów niespójnych:
48 z 60 przypadków raportowało jedną składową zamiast dwóch. Przyczyną było błędne założenie, że
składowe można wykryć po przerwach w numeracji wierzchołków. Finalna implementacja używa pełnej
detekcji BFS, co jest wolniejsze od heurystyki po numeracji, ale jest poprawne i uczciwe względem
baseline'u.

### 8.4. Ograniczenia środowiska

- Wersja rozproszona dzieli pracę po składowych spójności. Dla grafu spójnego istnieje tylko jedno
  zadanie, więc pracuje praktycznie jeden worker, a pozostałe nie mają użytecznej pracy.
- Dla grafów niespójnych generowanych w projekcie zwykle występują dwie składowe, więc przy trzech
  workerach maksymalnie dwa workery wykonują BFS. Ogranicza to możliwy speedup niezależnie od liczby
  dostępnych kontenerów.
- Do czasu wersji rozproszonej wliczono detekcję składowych, przygotowanie podgrafów, scheduling,
  komunikację TCP oraz BFS workerów. Nie wliczono startu kontenerów, łączenia z workerami,
  wczytywania grafu ani wczytywania pliku `*_expected.txt`.
- Narzut serializacji i przesyłania całych podgrafów jest duży w stosunku do samego BFS, szczególnie
  dla małych i średnich grafów.
- Implementacja jest distributed-like, ponieważ używa osobnych procesów i komunikacji TCP, ale
  wszystkie kontenery działają lokalnie na jednej maszynie. Nie testowano opóźnień sieciowych
  typowych dla prawdziwego klastra.
- Aktualny model nie równolegli pojedynczej składowej. Aby uzyskać przyspieszenie dla grafów
  spójnych, należałoby podzielić pracę wewnątrz jednej składowej, np. według frontieru albo
  partycji wierzchołków, oraz wymieniać informacje o nowo odkrytych wierzchołkach między workerami.

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
