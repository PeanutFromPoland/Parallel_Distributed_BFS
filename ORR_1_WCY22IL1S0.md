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
- wyznaczać odległość od wierzchołka startowego do wszystkich osiągalnych wierzchołków,
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

- **System hosta:** Windows NT 10.0, build 26200 (25H2), architektura AMD64.
- **CPU / RAM:** AMD Ryzen 7 7800X3D (8 rdzeni, 16 procesorów logicznych), 31,2 GB RAM.
- **Runtime lokalny:** CPython 3.14.3. Wersja sekwencyjna i równoległa były uruchamiane
  bezpośrednio na hoście.
- **Runtime rozproszony:** Docker Engine 29.5.2, Docker Compose 5.1.4 oraz obrazy
  `python:3.12-slim`. Koordynator i trzy workery działały jako osobne kontenery połączone
  lokalną siecią Docker bridge.
- **Biblioteki:** właściwe implementacje BFS, komunikacji TCP i benchmarku korzystają przede
  wszystkim z biblioteki standardowej Pythona (`multiprocessing`, `socket`, `pickle`,
  `threading`, `collections`, `statistics`). Pakiety `networkx 3.6.1` i
  `matplotlib 3.10.8` służą generatorom i wizualizacji, ale nie znajdują się w mierzonej
  ścieżce wykonania BFS.
- **Miejsce wykonania:** jedna lokalna stacja robocza. Wariant rozproszony bada narzut
  architektury coordinator-worker i komunikacji TCP między kontenerami, ale nie uwzględnia
  opóźnień fizycznej sieci ani osobnych maszyn.

### 9.2. Zasady benchmarku

- **Dane:** wszystkie wersje korzystają z tych samych plików grafów i tych samych plików
  `*_expected.txt`. Zbadano 602 konfiguracje, po 5 instancji każdej konfiguracji, czyli
  łącznie 3010 grafów. Zestaw obejmuje rozmiary od 50 do 500 000 wierzchołków, cztery
  typy generatorów, trzy profile gęstości oraz grafy niespójne z konfiguracjami
  `few=5`, `medium=50` i `many=500` zadanych części. Rzeczywista liczba składowych jest
  wykrywana algorytmicznie i w części grafów zawierających `small_world` może być większa,
  jeżeli wygenerowany podgraf nie uzyskał spójności.
- **Liczba powtórzeń:** każdy algorytm wykonano 3 razy dla każdej instancji grafu. W CSV
  zapisano wyniki pojedynczych prób oraz średnią, medianę, minimum, maksimum i odchylenie
  standardowe.
- **Losowość:** benchmark korzysta z utrwalonych plików wejściowych, więc wszystkie wersje
  otrzymują identyczne dane. Aktualny generator wyznacza seed deterministycznie z pełnej
  konfiguracji i numeru instancji, dlatego nowe generowanie nie zależy od kolejności.
  Ponieważ sposób wyznaczania seedu został zmieniony po utworzeniu badanego zestawu,
  regeneracja grafów wymaga ponownego wykonania wszystkich benchmarków.
- **Pomiar czasu:** użyto `time.perf_counter()`. Wczytanie grafu i pliku expected oraz
  weryfikacja poprawności nie wchodzą do czasu żadnego wariantu.
- **Wersja sekwencyjna i równoległa:** pula 16 procesów jest tworzona raz i używana dla
  wszystkich grafów. Raportowany `par_time` zaczyna się jednak dopiero po konwersji grafu
  do CSR i skopiowaniu tablic do pamięci współdzielonej. Jest to zatem czas jądra BFS,
  a nie pełny czas przygotowania i wykonania wariantu równoległego.
- **Wersja rozproszona:** start kontenerów, nawiązanie połączeń oraz wczytanie grafu są
  pomijane, ale `dist_time` obejmuje detekcję składowych, tworzenie podgrafów, scheduling,
  serializację, komunikację TCP i BFS workerów.
- **Agregacja:** w tabeli czasy są średnimi z pięciu instancji danej konfiguracji.
  Speedup konfiguracji jest średnią z pięciu speedupów instancji, natomiast speedup globalny
  policzono jako iloraz sum średnich czasów. Efektywność to `speedup / liczba workerów`.

### 9.3. Wyniki

Tabela przedstawia czasy średnie w sekundach po agregacji grafów o tej samej liczbie
wierzchołków, profilu gęstości i zadanej liczbie części. Struktura grafu, generator oraz numer
instancji są pomijane. Profile gęstości z etykiet odwzorowano jako `sparse=0,1`,
`medium=0,3` i `dense=0,5`. Dla grafów siatkowych (`grid`) generator nie przyjmuje
parametru gęstości, dlatego wpisano `N/D`. Konfiguracje `C4`, `C8`, `C12`, `C16`
oznaczają liczbę procesów, natomiast `C2`, `C3`, `C5`, `C10` liczbę stacji roboczych.

| Wierzchołki | Gęstość | Liczba części | Seq [s] | Parallel C4 [s] | Parallel C8 [s] | Parallel C12 [s] | Parallel C16 [s] | Distributed C2 [s] | Distributed C3 [s] | Distributed C5 [s] | Distributed C10 [s] | Uwagi |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 50 | 0,1 | 1 | 0,001238 | 3,991e-5 | 3,386e-5 | 4,505e-5 | 4,102e-5 | 0,008876 | 0,009556 | 0,008817 | 0,008604 | graf spójny |
| 50 | 0,3 | 1 | 0,001142 | 5,670e-5 | 4,872e-5 | 4,937e-5 | 6,106e-5 | 0,003343 | 0,004438 | 0,004300 | 0,003987 | graf spójny |
| 50 | 0,5 | 1 | 0,001401 | 8,208e-5 | 9,713e-5 | 8,369e-5 | 9,873e-5 | 0,007630 | 0,007723 | 0,007231 | 0,007067 | graf spójny |
| 50 | N/D (grid) | 1 | 9,868e-4 | 3,518e-5 | 3,633e-5 | 3,114e-5 | 4,712e-5 | 0,006641 | 0,005815 | 0,006273 | 0,005721 | graf spójny; siatka bez parametru gęstości |
| 500 | 0,1 | 1 | 1,499e-4 | 3,642e-4 | 4,383e-4 | 3,996e-4 | 4,356e-4 | 8,039e-4 | 0,001100 | 8,133e-4 | 8,370e-4 | graf spójny |
| 500 | 0,3 | 1 | 2,102e-4 | 5,507e-4 | 5,223e-4 | 6,036e-4 | 6,233e-4 | 0,001028 | 0,001238 | 0,001048 | 0,001032 | graf spójny |
| 500 | 0,5 | 1 | 2,984e-4 | 7,934e-4 | 9,123e-4 | 7,911e-4 | 0,001016 | 0,001440 | 0,001500 | 0,001260 | 0,001263 | graf spójny |
| 500 | N/D (grid) | 1 | 1,273e-4 | 3,623e-4 | 3,129e-4 | 3,124e-4 | 4,279e-4 | 7,815e-4 | 0,001008 | 7,909e-4 | 7,794e-4 | graf spójny; siatka bez parametru gęstości |
| 5000 | 0,1 | 1 | 0,001514 | 0,014623 | 0,015959 | 0,017628 | 0,024718 | 0,005831 | 0,006368 | 0,005763 | 0,005739 | graf spójny |
| 5000 | 0,3 | 1 | 0,002471 | 0,004792 | 0,004794 | 0,004985 | 0,005641 | 0,008419 | 0,008888 | 0,008231 | 0,008319 | graf spójny |
| 5000 | 0,5 | 1 | 0,003500 | 0,006449 | 0,005259 | 0,004839 | 0,005846 | 0,011366 | 0,012468 | 0,011239 | 0,011264 | graf spójny |
| 5000 | N/D (grid) | 1 | 0,001386 | 0,003194 | 0,003771 | 0,003189 | 0,004442 | 0,005298 | 0,005935 | 0,005484 | 0,005313 | graf spójny; siatka bez parametru gęstości |
| 50000 | 0,1 | 1 | 0,020620 | 0,027961 | 0,025301 | 0,025899 | 0,027168 | 0,067376 | 0,075382 | 0,066439 | 0,066973 | graf spójny |
| 50000 | 0,3 | 1 | 0,039039 | 0,039406 | 0,034111 | 0,032120 | 0,032521 | 0,109275 | 0,130044 | 0,110196 | 0,109567 | graf spójny |
| 50000 | 0,5 | 1 | 0,062506 | 0,066685 | 0,046270 | 0,042484 | 0,047727 | 0,168230 | 0,199236 | 0,171356 | 0,170117 | graf spójny |
| 50000 | N/D (grid) | 1 | 0,018176 | 0,036728 | 0,035189 | 0,036064 | 0,042790 | 0,056656 | 0,066213 | 0,056924 | 0,055861 | graf spójny; siatka bez parametru gęstości |
| 500000 | 0,1 | 1 | 0,417902 | 0,327991 | 0,293196 | 0,295728 | 0,298778 | 1,1991 | 1,5257 | 1,2125 | 1,2012 | graf spójny |
| 500000 | 0,3 | 1 | 0,752506 | 0,441051 | 0,351391 | 0,331549 | 0,347504 | 1,9900 | 2,7345 | 1,9793 | 1,9852 | graf spójny |
| 500000 | 0,5 | 1 | 1,1287 | 0,650616 | 0,455801 | 0,434480 | 0,443354 | 2,9713 | 3,9571 | 2,9654 | 2,9898 | graf spójny |
| 500000 | N/D (grid) | 1 | 0,294899 | 0,449663 | 0,505192 | 0,597477 | 0,687569 | 0,914090 | 1,1048 | 0,925369 | 0,931949 | graf spójny; siatka bez parametru gęstości |
| 50 | 0,1 | 5 | 5,260e-4 | 3,330e-5 | 3,314e-5 | 3,301e-5 | 3,224e-5 | 0,001421 | 0,001867 | 0,001976 | 0,001882 | profil few parts |
| 50 | 0,3 | 5 | 8,112e-4 | 4,100e-5 | 3,954e-5 | 4,274e-5 | 3,957e-5 | 0,001864 | 0,003337 | 0,003615 | 0,003609 | profil few parts |
| 50 | 0,5 | 5 | 7,546e-4 | 5,127e-5 | 5,200e-5 | 5,279e-5 | 4,834e-5 | 0,003589 | 0,004906 | 0,005030 | 0,005023 | profil few parts |
| 50 | N/D (grid) | 5 | 5,620e-4 | 4,935e-5 | 2,882e-5 | 3,016e-5 | 2,897e-5 | 9,596e-4 | 0,001463 | 0,001397 | 0,001417 | profil few parts; siatka bez parametru gęstości |
| 500 | 0,1 | 5 | 1,276e-4 | 3,279e-4 | 3,158e-4 | 3,188e-4 | 3,202e-4 | 0,001296 | 0,001729 | 0,001740 | 0,001760 | profil few parts |
| 500 | 0,3 | 5 | 1,734e-4 | 4,944e-4 | 4,848e-4 | 5,215e-4 | 4,918e-4 | 0,001478 | 0,001889 | 0,001880 | 0,001891 | profil few parts |
| 500 | 0,5 | 5 | 2,319e-4 | 7,221e-4 | 7,410e-4 | 7,424e-4 | 7,617e-4 | 0,001650 | 0,002099 | 0,002032 | 0,002050 | profil few parts |
| 500 | N/D (grid) | 5 | 1,235e-4 | 3,250e-4 | 2,946e-4 | 3,121e-4 | 3,143e-4 | 0,001322 | 0,001990 | 0,001711 | 0,001707 | profil few parts; siatka bez parametru gęstości |
| 5000 | 0,1 | 5 | 0,001389 | 0,003717 | 0,003898 | 0,003669 | 0,004235 | 0,006159 | 0,006460 | 0,005639 | 0,005706 | profil few parts |
| 5000 | 0,3 | 5 | 0,002116 | 0,005110 | 0,005042 | 0,005121 | 0,005505 | 0,008367 | 0,008687 | 0,007909 | 0,007949 | profil few parts |
| 5000 | 0,5 | 5 | 0,002849 | 0,006927 | 0,006547 | 0,006461 | 0,006897 | 0,010756 | 0,011131 | 0,010155 | 0,010023 | profil few parts |
| 5000 | N/D (grid) | 5 | 0,001388 | 0,004107 | 0,003639 | 0,003196 | 0,003681 | 0,005871 | 0,007395 | 0,005581 | 0,005400 | profil few parts; siatka bez parametru gęstości |
| 50000 | 0,1 | 5 | 0,017307 | 0,031570 | 0,030243 | 0,031425 | 0,031934 | 0,062420 | 0,068628 | 0,059130 | 0,058650 | profil few parts |
| 50000 | 0,3 | 5 | 0,031030 | 0,042802 | 0,037528 | 0,038260 | 0,037961 | 0,099657 | 0,111248 | 0,098043 | 0,097703 | profil few parts |
| 50000 | 0,5 | 5 | 0,044901 | 0,055775 | 0,044924 | 0,043417 | 0,042301 | 0,136765 | 0,155786 | 0,140862 | 0,133091 | profil few parts |
| 50000 | N/D (grid) | 5 | 0,016790 | 0,039239 | 0,034495 | 0,032268 | 0,033141 | 0,055866 | 0,081349 | 0,053646 | 0,054514 | profil few parts; siatka bez parametru gęstości |
| 500000 | 0,1 | 5 | 0,315633 | 0,346298 | 0,311361 | 0,309734 | 0,294999 | 1,2566 | 1,4477 | 1,2448 | 1,2173 | profil few parts |
| 500000 | 0,3 | 5 | 0,524841 | 0,450121 | 0,371077 | 0,355291 | 0,334270 | 1,9596 | 2,2487 | 1,9728 | 1,9286 | profil few parts |
| 500000 | 0,5 | 5 | 0,741533 | 0,582746 | 0,444989 | 0,408333 | 0,384514 | 2,7521 | 3,0633 | 2,7489 | 2,6899 | profil few parts |
| 500000 | N/D (grid) | 5 | 0,269185 | 0,405556 | 0,369724 | 0,370423 | 0,352080 | 1,1793 | 1,5406 | 1,1741 | 1,1594 | profil few parts; siatka bez parametru gęstości |
| 500 | 0,1 | 50 | 0,001059 | 3,322e-4 | 3,389e-4 | 3,257e-4 | 3,466e-4 | 0,007388 | 0,010938 | 0,011452 | 0,012752 | profil some parts |
| 500 | 0,3 | 50 | 6,863e-4 | 4,218e-4 | 4,166e-4 | 4,213e-4 | 4,216e-4 | 0,004421 | 0,005639 | 0,006201 | 0,007552 | profil some parts |
| 500 | 0,5 | 50 | 6,631e-4 | 5,150e-4 | 5,294e-4 | 5,544e-4 | 5,184e-4 | 0,004520 | 0,005641 | 0,006138 | 0,007895 | profil some parts |
| 500 | N/D (grid) | 50 | 0,001032 | 2,968e-4 | 2,831e-4 | 3,027e-4 | 2,987e-4 | 0,005259 | 0,009082 | 0,008881 | 0,010463 | profil some parts; siatka bez parametru gęstości |
| 5000 | 0,1 | 50 | 0,001354 | 0,003593 | 0,003541 | 0,003353 | 0,003993 | 0,008904 | 0,010325 | 0,010127 | 0,011433 | profil some parts |
| 5000 | 0,3 | 50 | 0,001894 | 0,005404 | 0,005410 | 0,005285 | 0,005556 | 0,010663 | 0,012067 | 0,011504 | 0,012817 | profil some parts |
| 5000 | 0,5 | 50 | 0,002535 | 0,007764 | 0,007950 | 0,007229 | 0,007904 | 0,012761 | 0,014185 | 0,013025 | 0,014398 | profil some parts |
| 5000 | N/D (grid) | 50 | 0,001255 | 0,003360 | 0,003533 | 0,003148 | 0,003757 | 0,008431 | 0,009938 | 0,009813 | 0,011126 | profil some parts; siatka bez parametru gęstości |
| 50000 | 0,1 | 50 | 0,014565 | 0,034498 | 0,034506 | 0,036830 | 0,037680 | 0,057622 | 0,066061 | 0,050866 | 0,052510 | profil some parts |
| 50000 | 0,3 | 50 | 0,023763 | 0,048975 | 0,046650 | 0,049483 | 0,049275 | 0,080237 | 0,090690 | 0,070007 | 0,070748 | profil some parts |
| 50000 | 0,5 | 50 | 0,034784 | 0,068093 | 0,061358 | 0,063807 | 0,064022 | 0,109285 | 0,126815 | 0,097677 | 0,096545 | profil some parts |
| 50000 | N/D (grid) | 50 | 0,014846 | 0,034372 | 0,033651 | 0,031059 | 0,031240 | 0,055572 | 0,074179 | 0,050335 | 0,051287 | profil some parts; siatka bez parametru gęstości |
| 500000 | 0,1 | 50 | 0,241765 | 0,352647 | 0,332852 | 0,346830 | 0,342067 | 0,993938 | 1,0921 | 0,924170 | 0,919964 | profil some parts |
| 500000 | 0,3 | 50 | 0,353251 | 0,459848 | 0,395654 | 0,396268 | 0,391856 | 1,4017 | 1,4964 | 1,2766 | 1,2563 | profil some parts |
| 500000 | 0,5 | 50 | 0,470299 | 0,595578 | 0,479251 | 0,456198 | 0,436511 | 1,8896 | 1,9966 | 1,7059 | 1,6680 | profil some parts |
| 500000 | N/D (grid) | 50 | 0,238922 | 0,367863 | 0,363719 | 0,356661 | 0,346996 | 1,0441 | 1,1962 | 0,982846 | 0,974108 | profil some parts; siatka bez parametru gęstości |
| 5000 | 0,1 | 500 | 0,002073 | 0,003561 | 0,003505 | 0,003291 | 0,003651 | 0,038296 | 0,047751 | 0,054096 | 0,060047 | profil many parts |
| 5000 | 0,3 | 500 | 0,002240 | 0,004671 | 0,004842 | 0,004480 | 0,005077 | 0,039404 | 0,049427 | 0,055179 | 0,061050 | profil many parts |
| 5000 | 0,5 | 500 | 0,002514 | 0,005716 | 0,005715 | 0,005272 | 0,005765 | 0,040016 | 0,050809 | 0,055878 | 0,061738 | profil many parts |
| 5000 | N/D (grid) | 500 | 0,002082 | 0,003501 | 0,003531 | 0,002994 | 0,003834 | 0,038419 | 0,050284 | 0,053615 | 0,059769 | profil many parts; siatka bez parametru gęstości |
| 50000 | 0,1 | 500 | 0,014009 | 0,032590 | 0,032649 | 0,031529 | 0,032303 | 0,085468 | 0,105926 | 0,096226 | 0,100269 | profil many parts |
| 50000 | 0,3 | 500 | 0,021743 | 0,051000 | 0,050118 | 0,049684 | 0,049830 | 0,106422 | 0,130124 | 0,113381 | 0,116952 | profil many parts |
| 50000 | 0,5 | 500 | 0,030795 | 0,072650 | 0,070177 | 0,072539 | 0,070146 | 0,130746 | 0,161130 | 0,136737 | 0,141629 | profil many parts |
| 50000 | N/D (grid) | 500 | 0,013884 | 0,033448 | 0,032298 | 0,030480 | 0,031582 | 0,082383 | 0,113464 | 0,092444 | 0,098049 | profil many parts; siatka bez parametru gęstości |
| 500000 | 0,1 | 500 | 0,217050 | 0,380634 | 0,383862 | 0,401773 | 0,403544 | 0,961420 | 1,0629 | 0,910905 | 0,911229 | profil many parts |
| 500000 | 0,3 | 500 | 0,296896 | 0,516579 | 0,491694 | 0,514688 | 0,516793 | 1,2696 | 1,3713 | 1,1779 | 1,1837 | profil many parts |
| 500000 | 0,5 | 500 | 0,378451 | 0,706950 | 0,647438 | 0,663810 | 0,671182 | 1,6381 | 1,7233 | 1,5285 | 1,5031 | profil many parts |
| 500000 | N/D (grid) | 500 | 0,220678 | 0,356419 | 0,360588 | 0,347849 | 0,342200 | 1,0185 | 1,2594 | 1,0137 | 0,984511 | profil many parts; siatka bez parametru gęstości |

### 9.4. Dodatkowe metryki

Przyspieszenie obliczono jako iloraz średniego czasu sekwencyjnego i średniego czasu
danej konfiguracji: `speedup = Seq / T_konfiguracji`. Wartość większa od `1×` oznacza
przyspieszenie względem wersji sekwencyjnej, a wartość mniejsza od `1×` oznacza spowolnienie.

| Wierzchołki | Gęstość | Liczba części | Parallel C4 | Parallel C8 | Parallel C12 | Parallel C16 | Distributed C2 | Distributed C3 | Distributed C5 | Distributed C10 | Komentarz |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 50 | 0,1 | 1 | 31,016× | 36,559× | 27,480× | 30,178× | 0,139× | 0,130× | 0,140× | 0,144× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C8 36,559×. Distributed: maks. C10 0,144×. |
| 50 | 0,3 | 1 | 20,136× | 23,435× | 23,128× | 18,701× | 0,342× | 0,257× | 0,266× | 0,286× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C8 23,435×. Distributed: maks. C2 0,342×. |
| 50 | 0,5 | 1 | 17,073× | 14,427× | 16,744× | 14,194× | 0,184× | 0,181× | 0,194× | 0,198× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C4 17,073×. Distributed: maks. C10 0,198×. |
| 50 | N/D (grid) | 1 | 28,051× | 27,166× | 31,691× | 20,943× | 0,149× | 0,170× | 0,157× | 0,172× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C12 31,691×. Distributed: maks. C10 0,172×. |
| 500 | 0,1 | 1 | 0,412× | 0,342× | 0,375× | 0,344× | 0,186× | 0,136× | 0,184× | 0,179× | Brak przyspieszenia; najlepsze: Parallel C4 0,412×, Distributed C2 0,186×. |
| 500 | 0,3 | 1 | 0,382× | 0,403× | 0,348× | 0,337× | 0,205× | 0,170× | 0,201× | 0,204× | Brak przyspieszenia; najlepsze: Parallel C8 0,403×, Distributed C2 0,205×. |
| 500 | 0,5 | 1 | 0,376× | 0,327× | 0,377× | 0,294× | 0,207× | 0,199× | 0,237× | 0,236× | Brak przyspieszenia; najlepsze: Parallel C12 0,377×, Distributed C5 0,237×. |
| 500 | N/D (grid) | 1 | 0,351× | 0,407× | 0,407× | 0,297× | 0,163× | 0,126× | 0,161× | 0,163× | Brak przyspieszenia; najlepsze: Parallel C12 0,407×, Distributed C10 0,163×. |
| 5000 | 0,1 | 1 | 0,104× | 0,095× | 0,086× | 0,061× | 0,260× | 0,238× | 0,263× | 0,264× | Brak przyspieszenia; najlepsze: Parallel C4 0,104×, Distributed C10 0,264×. |
| 5000 | 0,3 | 1 | 0,516× | 0,515× | 0,496× | 0,438× | 0,293× | 0,278× | 0,300× | 0,297× | Brak przyspieszenia; najlepsze: Parallel C4 0,516×, Distributed C5 0,300×. |
| 5000 | 0,5 | 1 | 0,543× | 0,665× | 0,723× | 0,599× | 0,308× | 0,281× | 0,311× | 0,311× | Brak przyspieszenia; najlepsze: Parallel C12 0,723×, Distributed C5 0,311×. |
| 5000 | N/D (grid) | 1 | 0,434× | 0,368× | 0,435× | 0,312× | 0,262× | 0,234× | 0,253× | 0,261× | Brak przyspieszenia; najlepsze: Parallel C12 0,435×, Distributed C2 0,262×. |
| 50000 | 0,1 | 1 | 0,737× | 0,815× | 0,796× | 0,759× | 0,306× | 0,274× | 0,310× | 0,308× | Brak przyspieszenia; najlepsze: Parallel C8 0,815×, Distributed C5 0,310×. |
| 50000 | 0,3 | 1 | 0,991× | 1,144× | 1,215× | 1,200× | 0,357× | 0,300× | 0,354× | 0,356× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C12 1,215×. Distributed: maks. C2 0,357×. |
| 50000 | 0,5 | 1 | 0,937× | 1,351× | 1,471× | 1,310× | 0,372× | 0,314× | 0,365× | 0,367× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C12 1,471×. Distributed: maks. C2 0,372×. |
| 50000 | N/D (grid) | 1 | 0,495× | 0,517× | 0,504× | 0,425× | 0,321× | 0,275× | 0,319× | 0,325× | Brak przyspieszenia; najlepsze: Parallel C8 0,517×, Distributed C10 0,325×. |
| 500000 | 0,1 | 1 | 1,274× | 1,425× | 1,413× | 1,399× | 0,349× | 0,274× | 0,345× | 0,348× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C8 1,425×. Distributed: maks. C2 0,349×. |
| 500000 | 0,3 | 1 | 1,706× | 2,142× | 2,270× | 2,165× | 0,378× | 0,275× | 0,380× | 0,379× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C12 2,270×. Distributed: maks. C5 0,380×. |
| 500000 | 0,5 | 1 | 1,735× | 2,476× | 2,598× | 2,546× | 0,380× | 0,285× | 0,381× | 0,378× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C12 2,598×. Distributed: maks. C5 0,381×. |
| 500000 | N/D (grid) | 1 | 0,656× | 0,584× | 0,494× | 0,429× | 0,323× | 0,267× | 0,319× | 0,316× | Brak przyspieszenia; najlepsze: Parallel C4 0,656×, Distributed C2 0,323×. |
| 50 | 0,1 | 5 | 15,795× | 15,873× | 15,937× | 16,316× | 0,370× | 0,282× | 0,266× | 0,280× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C16 16,316×. Distributed: maks. C2 0,370×. |
| 50 | 0,3 | 5 | 19,786× | 20,517× | 18,980× | 20,502× | 0,435× | 0,243× | 0,224× | 0,225× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C8 20,517×. Distributed: maks. C2 0,435×. |
| 50 | 0,5 | 5 | 14,718× | 14,510× | 14,293× | 15,609× | 0,210× | 0,154× | 0,150× | 0,150× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C16 15,609×. Distributed: maks. C2 0,210×. |
| 50 | N/D (grid) | 5 | 11,388× | 19,500× | 18,633× | 19,397× | 0,586× | 0,384× | 0,402× | 0,396× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C8 19,500×. Distributed: maks. C2 0,586×. |
| 500 | 0,1 | 5 | 0,389× | 0,404× | 0,400× | 0,399× | 0,098× | 0,074× | 0,073× | 0,073× | Brak przyspieszenia; najlepsze: Parallel C8 0,404×, Distributed C2 0,098×. |
| 500 | 0,3 | 5 | 0,351× | 0,358× | 0,333× | 0,353× | 0,117× | 0,092× | 0,092× | 0,092× | Brak przyspieszenia; najlepsze: Parallel C8 0,358×, Distributed C2 0,117×. |
| 500 | 0,5 | 5 | 0,321× | 0,313× | 0,312× | 0,304× | 0,140× | 0,110× | 0,114× | 0,113× | Brak przyspieszenia; najlepsze: Parallel C4 0,321×, Distributed C2 0,140×. |
| 500 | N/D (grid) | 5 | 0,380× | 0,419× | 0,396× | 0,393× | 0,093× | 0,062× | 0,072× | 0,072× | Brak przyspieszenia; najlepsze: Parallel C8 0,419×, Distributed C2 0,093×. |
| 5000 | 0,1 | 5 | 0,374× | 0,356× | 0,378× | 0,328× | 0,225× | 0,215× | 0,246× | 0,243× | Brak przyspieszenia; najlepsze: Parallel C12 0,378×, Distributed C5 0,246×. |
| 5000 | 0,3 | 5 | 0,414× | 0,420× | 0,413× | 0,384× | 0,253× | 0,244× | 0,268× | 0,266× | Brak przyspieszenia; najlepsze: Parallel C8 0,420×, Distributed C5 0,268×. |
| 5000 | 0,5 | 5 | 0,411× | 0,435× | 0,441× | 0,413× | 0,265× | 0,256× | 0,281× | 0,284× | Brak przyspieszenia; najlepsze: Parallel C12 0,441×, Distributed C10 0,284×. |
| 5000 | N/D (grid) | 5 | 0,338× | 0,382× | 0,434× | 0,377× | 0,237× | 0,188× | 0,249× | 0,257× | Brak przyspieszenia; najlepsze: Parallel C12 0,434×, Distributed C10 0,257×. |
| 50000 | 0,1 | 5 | 0,548× | 0,572× | 0,551× | 0,542× | 0,277× | 0,252× | 0,293× | 0,295× | Brak przyspieszenia; najlepsze: Parallel C8 0,572×, Distributed C10 0,295×. |
| 50000 | 0,3 | 5 | 0,725× | 0,827× | 0,811× | 0,817× | 0,311× | 0,279× | 0,316× | 0,318× | Brak przyspieszenia; najlepsze: Parallel C8 0,827×, Distributed C10 0,318×. |
| 50000 | 0,5 | 5 | 0,805× | 0,999× | 1,034× | 1,061× | 0,328× | 0,288× | 0,319× | 0,337× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C16 1,061×. Distributed: maks. C10 0,337×. |
| 50000 | N/D (grid) | 5 | 0,428× | 0,487× | 0,520× | 0,507× | 0,301× | 0,206× | 0,313× | 0,308× | Brak przyspieszenia; najlepsze: Parallel C12 0,520×, Distributed C5 0,313×. |
| 500000 | 0,1 | 5 | 0,911× | 1,014× | 1,019× | 1,070× | 0,251× | 0,218× | 0,254× | 0,259× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C16 1,070×. Distributed: maks. C10 0,259×. |
| 500000 | 0,3 | 5 | 1,166× | 1,414× | 1,477× | 1,570× | 0,268× | 0,233× | 0,266× | 0,272× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C16 1,570×. Distributed: maks. C10 0,272×. |
| 500000 | 0,5 | 5 | 1,272× | 1,666× | 1,816× | 1,928× | 0,269× | 0,242× | 0,270× | 0,276× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C16 1,928×. Distributed: maks. C10 0,276×. |
| 500000 | N/D (grid) | 5 | 0,664× | 0,728× | 0,727× | 0,765× | 0,228× | 0,175× | 0,229× | 0,232× | Brak przyspieszenia; najlepsze: Parallel C16 0,765×, Distributed C10 0,232×. |
| 500 | 0,1 | 50 | 3,187× | 3,124× | 3,250× | 3,055× | 0,143× | 0,097× | 0,092× | 0,083× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C12 3,250×. Distributed: maks. C2 0,143×. |
| 500 | 0,3 | 50 | 1,627× | 1,647× | 1,629× | 1,628× | 0,155× | 0,122× | 0,111× | 0,091× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C8 1,647×. Distributed: maks. C2 0,155×. |
| 500 | 0,5 | 50 | 1,288× | 1,253× | 1,196× | 1,279× | 0,147× | 0,118× | 0,108× | 0,084× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C4 1,288×. Distributed: maks. C2 0,147×. |
| 500 | N/D (grid) | 50 | 3,477× | 3,646× | 3,410× | 3,455× | 0,196× | 0,114× | 0,116× | 0,099× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C8 3,646×. Distributed: maks. C2 0,196×. |
| 5000 | 0,1 | 50 | 0,377× | 0,382× | 0,404× | 0,339× | 0,152× | 0,131× | 0,134× | 0,118× | Brak przyspieszenia; najlepsze: Parallel C12 0,404×, Distributed C2 0,152×. |
| 5000 | 0,3 | 50 | 0,351× | 0,350× | 0,358× | 0,341× | 0,178× | 0,157× | 0,165× | 0,148× | Brak przyspieszenia; najlepsze: Parallel C12 0,358×, Distributed C2 0,178×. |
| 5000 | 0,5 | 50 | 0,327× | 0,319× | 0,351× | 0,321× | 0,199× | 0,179× | 0,195× | 0,176× | Brak przyspieszenia; najlepsze: Parallel C12 0,351×, Distributed C2 0,199×. |
| 5000 | N/D (grid) | 50 | 0,374× | 0,355× | 0,399× | 0,334× | 0,149× | 0,126× | 0,128× | 0,113× | Brak przyspieszenia; najlepsze: Parallel C12 0,399×, Distributed C2 0,149×. |
| 50000 | 0,1 | 50 | 0,422× | 0,422× | 0,395× | 0,387× | 0,253× | 0,220× | 0,286× | 0,277× | Brak przyspieszenia; najlepsze: Parallel C4 0,422×, Distributed C5 0,286×. |
| 50000 | 0,3 | 50 | 0,485× | 0,509× | 0,480× | 0,482× | 0,296× | 0,262× | 0,339× | 0,336× | Brak przyspieszenia; najlepsze: Parallel C8 0,509×, Distributed C5 0,339×. |
| 50000 | 0,5 | 50 | 0,511× | 0,567× | 0,545× | 0,543× | 0,318× | 0,274× | 0,356× | 0,360× | Brak przyspieszenia; najlepsze: Parallel C8 0,567×, Distributed C10 0,360×. |
| 50000 | N/D (grid) | 50 | 0,432× | 0,441× | 0,478× | 0,475× | 0,267× | 0,200× | 0,295× | 0,289× | Brak przyspieszenia; najlepsze: Parallel C12 0,478×, Distributed C5 0,295×. |
| 500000 | 0,1 | 50 | 0,686× | 0,726× | 0,697× | 0,707× | 0,243× | 0,221× | 0,262× | 0,263× | Brak przyspieszenia; najlepsze: Parallel C8 0,726×, Distributed C10 0,263×. |
| 500000 | 0,3 | 50 | 0,768× | 0,893× | 0,891× | 0,901× | 0,252× | 0,236× | 0,277× | 0,281× | Brak przyspieszenia; najlepsze: Parallel C16 0,901×, Distributed C10 0,281×. |
| 500000 | 0,5 | 50 | 0,790× | 0,981× | 1,031× | 1,077× | 0,249× | 0,236× | 0,276× | 0,282× | Przyspiesza tylko wariant równoległy; najlepszy Parallel C16 1,077×. Distributed: maks. C10 0,282×. |
| 500000 | N/D (grid) | 50 | 0,649× | 0,657× | 0,670× | 0,689× | 0,229× | 0,200× | 0,243× | 0,245× | Brak przyspieszenia; najlepsze: Parallel C16 0,689×, Distributed C10 0,245×. |
| 5000 | 0,1 | 500 | 0,582× | 0,591× | 0,630× | 0,568× | 0,054× | 0,043× | 0,038× | 0,035× | Brak przyspieszenia; najlepsze: Parallel C12 0,630×, Distributed C2 0,054×. |
| 5000 | 0,3 | 500 | 0,479× | 0,463× | 0,500× | 0,441× | 0,057× | 0,045× | 0,041× | 0,037× | Brak przyspieszenia; najlepsze: Parallel C12 0,500×, Distributed C2 0,057×. |
| 5000 | 0,5 | 500 | 0,440× | 0,440× | 0,477× | 0,436× | 0,063× | 0,049× | 0,045× | 0,041× | Brak przyspieszenia; najlepsze: Parallel C12 0,477×, Distributed C2 0,063×. |
| 5000 | N/D (grid) | 500 | 0,595× | 0,590× | 0,695× | 0,543× | 0,054× | 0,041× | 0,039× | 0,035× | Brak przyspieszenia; najlepsze: Parallel C12 0,695×, Distributed C2 0,054×. |
| 50000 | 0,1 | 500 | 0,430× | 0,429× | 0,444× | 0,434× | 0,164× | 0,132× | 0,146× | 0,140× | Brak przyspieszenia; najlepsze: Parallel C12 0,444×, Distributed C2 0,164×. |
| 50000 | 0,3 | 500 | 0,426× | 0,434× | 0,438× | 0,436× | 0,204× | 0,167× | 0,192× | 0,186× | Brak przyspieszenia; najlepsze: Parallel C12 0,438×, Distributed C2 0,204×. |
| 50000 | 0,5 | 500 | 0,424× | 0,439× | 0,425× | 0,439× | 0,236× | 0,191× | 0,225× | 0,217× | Brak przyspieszenia; najlepsze: Parallel C16 0,439×, Distributed C2 0,236×. |
| 50000 | N/D (grid) | 500 | 0,415× | 0,430× | 0,456× | 0,440× | 0,169× | 0,122× | 0,150× | 0,142× | Brak przyspieszenia; najlepsze: Parallel C12 0,456×, Distributed C2 0,169×. |
| 500000 | 0,1 | 500 | 0,570× | 0,565× | 0,540× | 0,538× | 0,226× | 0,204× | 0,238× | 0,238× | Brak przyspieszenia; najlepsze: Parallel C4 0,570×, Distributed C5 0,238×. |
| 500000 | 0,3 | 500 | 0,575× | 0,604× | 0,577× | 0,574× | 0,234× | 0,217× | 0,252× | 0,251× | Brak przyspieszenia; najlepsze: Parallel C8 0,604×, Distributed C5 0,252×. |
| 500000 | 0,5 | 500 | 0,535× | 0,585× | 0,570× | 0,564× | 0,231× | 0,220× | 0,248× | 0,252× | Brak przyspieszenia; najlepsze: Parallel C8 0,585×, Distributed C10 0,252×. |
| 500000 | N/D (grid) | 500 | 0,619× | 0,612× | 0,634× | 0,645× | 0,217× | 0,175× | 0,218× | 0,224× | Brak przyspieszenia; najlepsze: Parallel C16 0,645×, Distributed C10 0,224×. |

### 9.5. Interpretacja wyników

#### Obraz ogólny

Wyniki obejmują **68 profili danych** opisanych
przez liczbę wierzchołków, profil gęstości i liczbę części. Dla każdego profilu
porównano cztery konfiguracje równoległe i cztery rozproszone, czyli po **272 porównania**
na wariant. Zaniedbana została struktura grafu.

Wariant równoległy przekroczył `1×` w **81 z 272** porównań i co najmniej jedna
konfiguracja przyspieszyła wykonanie dla **22 z 68** profili. Wariant rozproszony nie
przekroczył `1×` w żadnym z 272 porównań. Oznacza to, że lokalna równoległość
może być korzystna dla wybranych danych, natomiast badana architektura coordinator-worker
nie była szybsza od wspólnego baseline'u sekwencyjnego.

#### Wersja równoległa

Najbardziej wiarygodne przyspieszenia pojawiają się dla dużych i bardzo dużych grafów,
gdy koszt przejścia po krawędziach jest wystarczający do zamortyzowania synchronizacji
procesów. Dla grafu spójnego o 500 000 wierzchołkach najlepsze wyniki wyniosły:

- profil gęsty: **2,598×** dla `Parallel C12`,
- profil średni: **2,270×** dla `Parallel C12`,
- profil rzadki: **1,425×** dla `Parallel C8`.

Podobny trend wystąpił dla grafów z pięcioma częściami. Dla profilu `huge & dense`
najlepszy był `Parallel C16` z wynikiem **1,928×**, a dla `huge & medium` uzyskano
**1,570×**. Zwiększanie liczby procesów nie daje jednak monotonicznej poprawy. Spośród
68 profili najlepsza była konfiguracja C12 w 26 przypadkach, C8 w 21, C16 w 12, a C4
w 9 przypadkach. Optymalna liczba procesów zależy więc od ilości pracy w frontierach
i kosztu synchronizacji, a nie wyłącznie od liczby dostępnych rdzeni.

Iloraz sum czasów dla 68 profili wynosi **0,894×** dla C4, **1,004×** dla C8,
**1,000×** dla C12 i **0,995×** dla C16. W ujęciu całego zbioru C8 i C12 są
zatem jedynie na granicy czasu sekwencyjnego. Ponadto raportowany czas równoległy nie
obejmuje konwersji grafu do CSR ani kopiowania danych do pamięci współdzielonej. Pełny
wynik end-to-end byłby z tego powodu mniej korzystny.

Bardzo wysokie wartości dla części profili `tiny`, dochodzące do **36,559×**, nie są
dowodem skalowalności. Czasy mieszczą się tam w dziesiątkach mikrosekund, dlatego
pojedyncze pomiary rozgrzewające i wartości odstające baseline'u silnie zmieniają iloraz.
Dodatkowo wspólna kolumna `Seq` agreguje pomiary lokalne i kontenerowe. Wnioski o wydajności
należy więc opierać przede wszystkim na profilach `large` i `huge`.

#### Wersja rozproszona

Żadna konfiguracja rozproszona nie osiągnęła przyspieszenia. Najlepszy rezultat to
**0,586×** dla grafu `few parts tiny & grid` i dwóch stacji, co nadal oznacza wykonanie
około 1,7 raza wolniejsze od baseline'u. Dla całego zbioru iloraz sum czasów wyniósł:

- **0,279×** dla 2 stacji,
- **0,237×** dla 3 stacji,
- **0,286×** dla 5 stacji,
- **0,288×** dla 10 stacji.

Najlepszy wynik globalny uzyskało 10 stacji, ale wartość **0,288×** oznacza nadal
około 3,5-krotne spowolnienie. Dwie stacje były najlepszą konfiguracją dla 32 profili,
10 stacji dla 22, a 5 stacji dla 14. Konfiguracja z trzema stacjami nie była najlepsza dla
żadnego profilu. Brak monotonicznego skalowania wskazuje, że dodatkowe stacje zwiększają
koszt komunikacji i koordynacji szybciej, niż skracają lokalne obliczenia BFS.

Przyczyną jest zakres mierzonego `dist_time`, który obejmuje detekcję składowych,
budowanie podgrafów, scheduling, serializację i transmisję TCP. Koordynator wykonuje
znaczną część pracy sekwencyjnie przed rozpoczęciem BFS na workerach. W grafie spójnym
tylko jeden worker otrzymuje użyteczne zadanie, a dla wielu małych części koszt utworzenia
i przesłania zadań przewyższa koszt samego BFS.

#### Wpływ parametrów grafu

Gęstość pomaga przede wszystkim wersji równoległej dla dużych grafów. Większa liczba
krawędzi zwiększa pracę obliczeniową przypadającą na proces, dzięki czemu narzut IPC
stanowi mniejszą część czasu. Sam rozmiar nie wystarcza: dla 500 000 wierzchołków i
500 części najlepszy speedup równoległy wynosi tylko około **0,60×**. Fragmentacja pracy
na wiele małych składowych ogranicza korzyści nawet przy dużym grafie.

Liczba części ma wyraźnie negatywny wpływ na obie implementacje. Dla jednej lub pięciu
części wersja równoległa często wykorzystuje duże zadania. Przy 50 częściach tylko
profil `huge & dense` nieznacznie przekracza `1×` (**1,077×** dla C16), natomiast przy
500 częściach żaden profil nie osiąga przyspieszenia. W wersji rozproszonej więcej
części daje więcej potencjalnych zadań, lecz jednocześnie zwiększa koszt detekcji,
ekstrakcji podgrafów i komunikacji, dlatego nie prowadzi do poprawy całkowitego czasu.

#### Wniosek

Obecna wersja równoległa ma uzasadnienie dla wybranych profili `large` i `huge`, zwłaszcza
gęstych oraz zawierających niewiele dużych części. Nie istnieje jedna najlepsza liczba
procesów dla wszystkich danych; najczęściej wygrywają C8 lub C12 dla grafów spójnych,
a C16 dla bardzo dużych grafów z kilkoma częściami.

Obecna wersja rozproszona nie jest szybszym zamiennikiem baseline'u. Jest demonstracją
architektury coordinator-worker i pozwala zidentyfikować narzuty, lecz poprawa wydajności
wymagałaby ograniczenia centralnego przygotowania danych, rozdzielenia grafu przed pomiarem,
partycjonowania pracy wewnątrz pojedynczej składowej oraz zmniejszenia liczby przesyłanych
kopii podgrafów.

## 10. AI use log

| Etap                                  | Do czego użyto AI                                                                                                                                                                                                                                                         | Co zostało przyjęte                                                                                                                                                                               | Co poprawiono ręcznie                                                                               |
|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Opracowanie planu działania           | Zredagowanie minimalnego zakresu zadania                                                                                                                                                                                                                                  | Rozdział 1.5 ORR_1_WCY22IL1S0.md                                                                                                                                                                  | Wyrażenia i sformułowania niebrzmiące poprawnie lub zrozumiale po polsku oraz usunięto zbędne uwagi |
| Implementacja generatora grafów       | Implementacja funkcji do generowania grafów niespójnych oraz grafów typu grid, small world i bianconi-barabasi                                                                                                                                                            | grid.py, bb.py, small_world.py, inconsistent.py, generate_graphs.py                                                                                                                               | Nic                                                                                                 |
| Implementacja wersji sekwencyjnej     | Doimplementowanie sprawdzania poprawności działania algorytmu i zwracanie ścieżki algorytmu BFS dla grafów niespójnych oraz zredagowanie podsumowania osiągniętych celów na danym etapie                                                                                  | baseline.py, utils/loader.py, utils/comparison.py, Rozdział 4 ORR_1_WCY22IL1S0.md                                                                                                                 | Wyrażenia i sformułowania niebrzmiące poprawnie lub zrozumiale po polsku                            |
| Opracowanie planu wersji równoległej  | Zredagowanie opisu implementacji algorytmu opartego o przydzielanie frontierów do procesów                                                                                                                                                                                | Rozdział 5 ORR_1_WCY22IL1S0.md                                                                                                                                                                    | Wyrażenia i sformułowania niebrzmiące poprawnie lub zrozumiale po polsku oraz usunięto zbędne uwagi |
| Implementacja wersji równoległej      | Pełna implementacja algorytmu wykorzystującego wiele rdzeni procesora działającego na współdzielonej pamięci oraz skryptu dokonującego pomiary czasu zarówno dla wersji sekwencyjnej, jak i równoległej oraz zredagowanie podsumowania osiągniętych celów na danym etapie | parallel.py, main.py, Rozdział 6 ORR_1_WCY22IL1S0.md                                                                                                                                              | Nic                                                                                                 |
| Opracowanie planu wersji rozproszonej | Zredagowanie opisu implementacji algorytmu opartego o dzielenie grafu na spójne podgrafy (części) i przydzielanie ich do stacji                                                                                                                                           | Rozdział 7 ORR_1_WCY22IL1S0.md                                                                                                                                                                    | Wyrażenia i sformułowania niebrzmiące poprawnie lub zrozumiale po polsku oraz usunięto zbędne uwagi |
| Implementacja wersji rozproszonej     | Pełna implementacja docker compose wystawiającego kilka węzłów komunikujących się ze sobą oraz zredagowanie podsumowania osiągniętych celów na danym etapie                                                                                                               | coordinator.py, coordinator/Dockerfile, graph_loader.py, shared/__init__.py, protocol.py, worker/Dockerfile, worker.py, docker-compose.yml, distributed/README.md, Rozdział 8 ORR_1_WCY22IL1S0.md | Nic                                                                                                 |
| Rozbudowa benchmarka                  | Rozbudowa skryptu generatora grafów oraz aparatu mierniczego zarówno dla wersji równoległej, jak i rozproszonej tak, aby można było uruchomić pomiary czasu wszystkich grafów dla wielu konfiguracji za jednym poleceniem                                                 | generate_graphs.py, benchmark_scaling.py, docker-compose.scaling.yml                                                                                                                              | Nic                                                                                                 |
| Analiza danych i wnioskowanie         | Implementacja skryptu agregującego wyniki uzyskane dla wielu konfiguracji i grafów. Czytelne przepisanie pomiarów z arkusza results/scaling/scaling_statistics.csv do tabelek w sprawozdaniu oraz zredagowanie wniosków na podstawie zagregowanych danych pomiarowych     | summarize_scaling.py, Rozdział 9, 11-13 ORR_1_WCY22IL1S0.md                                                                                                                                       | Zbędne uwagi                                                                                        |

## 11. Uruchomienie i reprodukowalność

### 11.1. Minimalna instrukcja uruchomienia

Wymagany jest Python 3.12 lub nowszy. Do uruchomienia wariantu rozproszonego i pełnego
benchmarku skalowania potrzebny jest również działający Docker Desktop z Docker Compose v2.
Poniższe polecenia należy wykonać w katalogu głównym repozytorium:

```powershell
# 1. Utworzenie środowiska i instalacja zależności
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Wygenerowanie grafów i wzorcowych wyników BFS
.\.venv\Scripts\python.exe generate_graphs.py

# 3. Lokalny benchmark sekwencyjny i równoległy
.\.venv\Scripts\python.exe main.py --workers 8 --runs 3

# 4. Pełny benchmark skalowania, łącznie z Dockerem
.\.venv\Scripts\python.exe benchmark_scaling.py

# 5. Agregacja wyników użytych w rozdziale 9
.\.venv\Scripts\python.exe summarize_scaling.py
```

Pełny benchmark przetwarza 3010 grafów dla ośmiu konfiguracji wykonania, dlatego może
trwać długo i wymagać znacznej ilości pamięci oraz miejsca na dysku. Jeżeli kompletne
i poprawne pliki CSV już istnieją, `benchmark_scaling.py` wykorzystuje je ponownie.
Opcja `--force` wymusza ponowne wykonanie wszystkich wskazanych konfiguracji.

Do szybkiej kontroli działania można ograniczyć zestaw danych i konfiguracje:

```powershell
# Mały, deterministyczny zestaw grafów
.\.venv\Scripts\python.exe generate_graphs.py --sizes tiny --instances 1

# Wyłącznie lokalna konfiguracja równoległa
.\.venv\Scripts\python.exe benchmark_scaling.py --parallel-only --processes 4 --runs 1

# Wyłącznie konfiguracja rozproszona
.\.venv\Scripts\python.exe benchmark_scaling.py --distributed-only --stations 2 --runs 1

# Podgląd komend bez uruchamiania benchmarku
.\.venv\Scripts\python.exe benchmark_scaling.py --dry-run
```

Sam wariant rozproszony można uruchomić bez skryptu skalowania:

```powershell
docker compose -f distributed/docker-compose.yml up --build --abort-on-container-exit
docker compose -f distributed/docker-compose.yml down --remove-orphans
```

### 11.2. Struktura repozytorium / plików

- `src/baseline.py` - sekwencyjny BFS używany jako baseline.
- `src/parallel.py` - lokalna implementacja równoległa oparta na `multiprocessing`,
  reprezentacji CSR i pamięci współdzielonej.
- `distributed/coordinator/` - koordynator: detekcja składowych, przygotowanie podgrafów,
  harmonogramowanie, wysyłanie zadań, scalanie i weryfikacja wyników.
- `distributed/worker/` - serwer workera wykonujący sekwencyjny BFS na otrzymanym podgrafie.
- `distributed/shared/protocol.py` - protokół TCP z nagłówkiem długości i serializacją
  `pickle`.
- `distributed/docker-compose.yml` - podstawowa konfiguracja coordinator-worker.
- `distributed/docker-compose.scaling.yml` - konfiguracja używana w testach od 2 do
  10 workerów.
- `generators/` i `generate_graphs.py` - generatory grafów spójnych i niespójnych oraz
  zapis wzorcowych wyników `*_expected.txt`.
- `graphs/` - wejściowe grafy pogrupowane według spójności, generatora, liczby części,
  gęstości i rozmiaru.
- `utils/loader.py` - wykrywanie i wczytywanie grafów oraz wyników wzorcowych.
- `utils/comparison.py` - porównanie odległości i składowych zwróconych przez algorytm
  z wynikiem oczekiwanym.
- `main.py` - benchmark sekwencyjny i równoległy dla pojedynczej liczby procesów.
- `benchmark_scaling.py` - automatyzacja konfiguracji 4/8/12/16 procesów oraz
  2/3/5/10 workerów.
- `summarize_scaling.py` - agregacja pomiarów według liczby wierzchołków, profilu
  gęstości i liczby części.
- `results/scaling/` - surowe CSV dla każdej konfiguracji oraz
  `scaling_statistics.csv` wykorzystany do utworzenia tabel w rozdziale 9.

### 11.3. Weryfikacja poprawności

Każdy wygenerowany graf ma odpowiadający plik `*_expected.txt`, zawierający oczekiwane
składowe, wierzchołki startowe i odległości BFS. W każdym powtórzeniu wynik wersji
sekwencyjnej, równoległej i rozproszonej jest porównywany z tym samym plikiem wzorcowym.
CSV zawiera pola `correct` i `message`, a skrypt skalowania ponownie wykorzystuje istniejący
plik tylko wtedy, gdy:

- liczba grafów i prób jest kompletna,
- liczba procesów lub workerów odpowiada konfiguracji,
- wszystkie wyniki mają `correct=True`,
- plik wynikowy nie jest starszy od grafów i plików wzorcowych.

Skrypt `summarize_scaling.py` domyślnie pomija niepoprawne próby. Opcja
`--include-incorrect` istnieje wyłącznie do celów diagnostycznych.

### 11.4. Reprodukowalność wyników

Generator wykorzystuje deterministyczny seed wyprowadzony z pełnej konfiguracji grafu
i numeru instancji. Powtórne wygenerowanie danych tym samym kodem i parametrami powinno
dać taki sam zestaw wejściowy. Dla pełnej reprodukcji należy zachować:

- wersję kodu generatora i implementacji BFS,
- parametry `--sizes`, `--types`, `--densities`, `--parts` i `--instances`,
- liczbę prób oraz konfiguracje procesów i workerów,
- wersję Pythona, Dockera i systemu operacyjnego,
- źródłowe CSV z rekordami pojedynczych prób.

Wyniki czasowe mogą się różnić między maszynami z powodu CPU, systemu, obciążenia,
wersji interpretera i kosztu wirtualizacji Dockera. Odtwarzalne są przede wszystkim dane,
poprawność wyników i procedura pomiarowa; identyczne czasy nie są gwarantowane.

## 12. Wnioski końcowe

### 12.1. Najkrótsze podsumowanie w 3 zdaniach

Zaimplementowano i zweryfikowano trzy warianty BFS: sekwencyjny, lokalny równoległy oraz
rozproszony coordinator-worker. Wersja równoległa daje przyspieszenie dla wybranych dużych
i gęstych grafów z niewielką liczbą części, osiągając maksymalnie **2,598×** dla
zagregowanego, wiarygodnego profilu `one part huge & dense`. Wersja rozproszona nie
przekroczyła `1×`, ponieważ detekcja składowych, przygotowanie podgrafów i komunikacja
TCP były droższe niż praca wykonana przez workery.

### 12.2. Co działa dobrze

- Wszystkie warianty rozwiązują ten sam problem i są automatycznie porównywane z plikami
  wzorcowymi dla 3010 grafów.
- Generator obejmuje pięć rozmiarów, kilka profili gęstości, cztery rodziny struktur oraz
  grafy z 1, 5, 50 i 500 częściami.
- Benchmark automatyzuje wiele konfiguracji, zapisuje pojedyncze próby i pozwala wznowić
  pracę przez ponowne wykorzystanie kompletnych CSV.
- Lokalna implementacja równoległa potrafi wykorzystać większą ilość pracy w dużych,
  gęstych grafach. Dla profilu `one part huge & dense` C12 osiągnęło **2,598×**, a dla
  `few parts huge & dense` C16 osiągnęło **1,928×**.
- Osobne pomiary faz wariantu rozproszonego umożliwiają wskazanie źródeł narzutu zamiast
  ograniczenia analizy do całkowitego czasu.
- Agregacja według rozmiaru, gęstości i liczby części upraszcza analizę oraz oddziela wpływ
  parametrów danych od konkretnego generatora.

### 12.3. Co nie działa lub działa gorzej niż oczekiwano

- Wariant rozproszony nie uzyskał przyspieszenia w żadnym z 272 zagregowanych porównań.
  Najlepszy wynik wyniósł **0,586×**, a globalne ilorazy sum mieściły się między
  **0,237×** i **0,288×**.
- Podział pracy rozproszonej wyłącznie po składowych nie daje równoległości dla grafu
  spójnego, ponieważ użyteczną pracę wykonuje wtedy jeden worker.
- Centralna detekcja składowych i budowanie pełnych kopii podgrafów ograniczają
  skalowalność. Przy wielu częściach rośnie również liczba operacji serializacji
  i komunikacji.
- Zwiększanie liczby procesów lub workerów nie daje monotonicznej poprawy. Dodatkowe
  jednostki wykonawcze mogą zwiększyć koszt IPC, synchronizacji i oczekiwania.
- Raportowany `par_time` nie obejmuje konwersji do CSR ani kopiowania do pamięci
  współdzielonej, dlatego nie jest pełnym czasem end-to-end.
- Wspólny czas `Seq` w tabeli zagregowanej łączy pomiary hosta i kontenera. Jest użyteczny
  do syntetycznego porównania profili, ale bardzo wysokie speedupy dla grafów `tiny`
  należy traktować jako niestabilne i podatne na rozgrzewanie środowiska.
- Uśrednienie po strukturach upraszcza wnioski, ale może ukrywać różnice między
  generatorami i wartości odstające pojedynczych instancji.

### 12.4. Najważniejsza lekcja techniczna

Równoległość jest opłacalna tylko wtedy, gdy ilość użytecznej pracy przypadającej na jedno
zadanie jest wyraźnie większa od kosztu przygotowania danych, synchronizacji i komunikacji.
Samo dodanie procesów lub workerów nie zapewnia skalowania: należy dobrać ziarnistość zadań,
ograniczyć centralne operacje sekwencyjne i mierzyć pełną ścieżkę end-to-end. W przypadku
BFS szczególnie ważny jest sposób partycjonowania grafu - podział wyłącznie po składowych
jest prosty i poprawny, lecz nie wykorzystuje wielu workerów dla grafów spójnych.

## 13. Checklista przed oddaniem

- [x] Temat, wejście, wyjście i kryterium poprawności są jasno opisane.
- [x] Istnieje działający baseline sekwencyjny.
- [x] Istnieje test poprawności lub inny wiarygodny sposób weryfikacji wyniku.
- [x] Wersja równoległa rozwiązuje ten sam problem co wersja sekwencyjna.
- [x] Wersja rozproszona lub distributed-like rozwiązuje ten sam problem co baseline.
- [x] Wszystkie porównania wykonano na tych samych grafach i wynikach wzorcowych.
- [x] W benchmarku użyto pięciu rozmiarów danych: od 50 do 500 000 wierzchołków.
- [x] W benchmarku użyto konfiguracji 4/8/12/16 procesów i 2/3/5/10 workerów.
- [x] Wnioski opisują wyniki oraz koszty przygotowania, synchronizacji i komunikacji.
- [x] AI use log został uzupełniony.
- [x] Minimalny i pełny sposób uruchomienia opisano w rozdziale 11.1.
