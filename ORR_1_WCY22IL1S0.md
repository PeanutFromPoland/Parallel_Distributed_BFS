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

W tabeli wpisane zostały średnie wyniki dla każdej kombinacji parametrów: typu, rozmiaru
i gęstości grafu. Dla grafów niespójnych dodatkowo pokazano konfigurację liczby składowych
(`few`, `medium`, `many`), ponieważ w wersji rozproszonej właśnie składowe są jednostkami
pracy. Czasy są podane w sekundach. `Parallel C1` oznacza wersję równoległą uruchamianą na
16 procesach, a `Distributed C1` oznacza wersję rozproszoną uruchamianą na 3 workerach.
Kolumna `Śr. m` oznacza średnią liczbę wpisów w listach sąsiedztwa. Dla grafu
nieskierowanego jedna krawędź jest zapisana w obu kierunkach, dlatego liczba unikalnych
krawędzi jest w przybliżeniu równa `m/2`.

Kolumna `Seq host [s]` pochodzi z lokalnego benchmarku wersji równoległej. Speedup wersji
rozproszonej został policzony względem osobnego baseline'u sekwencyjnego wykonanego wewnątrz
kontenera w tym samym przebiegu co `Distributed C1`. Nie należy więc próbować odtwarzać
`Speedup Distributed` przez podzielenie widocznej kolumny `Seq host [s]` przez czas
rozproszony. Takie rozdzielenie baseline'ów ogranicza wpływ różnic między CPythonem 3.14 na
hoście i CPythonem 3.12 w kontenerze.

| Spójność | Typ grafu | Składowe | Rozmiar | Gęstość | Śr. m | Seq host [s] | Parallel C1 [s] | Distributed C1 [s] | Speedup Parallel | Speedup Distributed | Efficiency Parallel | Efficiency Distributed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Spójny | bb | 1 | tiny | sparse | 98 | 0.000015 | 0.000025 | 0.02014 | 0.59× | 0.09× | 3.7% | 2.9% |
| Spójny | bb | 1 | tiny | medium | 194 | 0.000021 | 0.000048 | 0.00370 | 0.43× | 0.11× | 2.7% | 3.8% |
| Spójny | bb | 1 | tiny | dense | 380 | 0.000019 | 0.000051 | 0.00529 | 0.37× | 0.13× | 2.3% | 4.4% |
| Spójny | bb | 1 | small | sparse | 998 | 0.000127 | 0.000299 | 0.00101 | 0.43× | 0.13× | 2.7% | 4.3% |
| Spójny | bb | 1 | small | medium | 1994 | 0.000171 | 0.000431 | 0.00100 | 0.41× | 0.15× | 2.5% | 5.0% |
| Spójny | bb | 1 | small | dense | 3980 | 0.000198 | 0.000546 | 0.00111 | 0.36× | 0.16× | 2.3% | 5.5% |
| Spójny | bb | 1 | medium | sparse | 9998 | 0.00128 | 0.00508 | 0.00519 | 0.25× | 0.25× | 1.6% | 8.4% |
| Spójny | bb | 1 | medium | medium | 19994 | 0.00169 | 0.00452 | 0.00630 | 0.37× | 0.26× | 2.3% | 8.7% |
| Spójny | bb | 1 | medium | dense | 39980 | 0.00243 | 0.00432 | 0.00832 | 0.56× | 0.29× | 3.5% | 9.8% |
| Spójny | bb | 1 | large | sparse | 99998 | 0.01611 | 0.02478 | 0.05842 | 0.65× | 0.33× | 4.1% | 11.1% |
| Spójny | bb | 1 | large | medium | 199994 | 0.02296 | 0.02623 | 0.07908 | 0.87× | 0.36× | 5.5% | 12.0% |
| Spójny | bb | 1 | large | dense | 399980 | 0.03717 | 0.03458 | 0.1190 | 1.08× | 0.40× | 6.7% | 13.3% |
| Spójny | bb | 1 | huge | sparse | 999998 | 0.3217 | 0.2457 | 1.0950 | 1.31× | 0.34× | 8.2% | 11.2% |
| Spójny | bb | 1 | huge | medium | 1999994 | 0.4733 | 0.2961 | 1.6007 | 1.60× | 0.39× | 10.0% | 12.9% |
| Spójny | bb | 1 | huge | dense | 3999980 | 0.7178 | 0.3505 | 2.4379 | 2.06× | 0.41× | 12.8% | 13.5% |
| Spójny | grid | 1 | tiny | - | 170 | 0.000019 | 0.000047 | 0.00581 | 0.40× | 0.11× | 2.5% | 3.8% |
| Spójny | grid | 1 | small | - | 1910 | 0.000145 | 0.000428 | 0.00101 | 0.34× | 0.14× | 2.2% | 4.7% |
| Spójny | grid | 1 | medium | - | 19700 | 0.00158 | 0.00444 | 0.00594 | 0.38× | 0.25× | 2.4% | 8.4% |
| Spójny | grid | 1 | large | - | 199100 | 0.01921 | 0.04279 | 0.06621 | 0.45× | 0.36× | 2.8% | 12.1% |
| Spójny | grid | 1 | huge | - | 1997150 | 0.2982 | 0.6876 | 1.1048 | 0.43× | 0.32× | 2.7% | 10.7% |
| Spójny | random | 1 | tiny | sparse | 300 | 0.000027 | 0.000070 | 0.000679 | 0.39× | 0.04× | 2.5% | 1.4% |
| Spójny | random | 1 | tiny | medium | 900 | 0.000030 | 0.000095 | 0.00666 | 0.32× | 0.13× | 2.0% | 4.3% |
| Spójny | random | 1 | tiny | dense | 1500 | 0.000052 | 0.000188 | 0.01288 | 0.28× | 0.13× | 1.7% | 4.3% |
| Spójny | random | 1 | small | sparse | 3000 | 0.000249 | 0.000687 | 0.00135 | 0.36× | 0.18× | 2.3% | 6.0% |
| Spójny | random | 1 | small | medium | 9000 | 0.000360 | 0.000973 | 0.00171 | 0.37× | 0.24× | 2.3% | 8.0% |
| Spójny | random | 1 | small | dense | 15000 | 0.000649 | 0.00189 | 0.00222 | 0.35× | 0.23× | 2.2% | 7.6% |
| Spójny | random | 1 | medium | sparse | 30000 | 0.00278 | 0.06566 | 0.00855 | 0.41× | 0.28× | 2.5% | 9.2% |
| Spójny | random | 1 | medium | medium | 90000 | 0.00439 | 0.00577 | 0.01402 | 0.76× | 0.32× | 4.7% | 10.7% |
| Spójny | random | 1 | medium | dense | 150000 | 0.00689 | 0.00713 | 0.02065 | 0.96× | 0.31× | 6.0% | 10.2% |
| Spójny | random | 1 | large | sparse | 300000 | 0.02647 | 0.02731 | 0.1088 | 0.97× | 0.37× | 6.1% | 12.3% |
| Spójny | random | 1 | large | medium | 900000 | 0.06217 | 0.03903 | 0.2357 | 1.59× | 0.38× | 10.0% | 12.7% |
| Spójny | random | 1 | large | dense | 1500000 | 0.1297 | 0.07509 | 0.3706 | 1.73× | 0.38× | 10.8% | 12.8% |
| Spójny | random | 1 | huge | sparse | 3000000 | 0.5337 | 0.2876 | 2.2656 | 1.86× | 0.40× | 11.6% | 13.5% |
| Spójny | random | 1 | huge | medium | 9000000 | 1.3257 | 0.4676 | 5.2133 | 2.82× | 0.40× | 17.6% | 13.2% |
| Spójny | random | 1 | huge | dense | 15000000 | 2.0370 | 0.6425 | 7.6012 | 3.16× | 0.43× | 19.8% | 14.3% |
| Spójny | small_world | 1 | tiny | sparse | 100 | 0.000012 | 0.000028 | 0.00785 | 0.44× | 0.07× | 2.8% | 2.2% |
| Spójny | small_world | 1 | tiny | medium | 200 | 0.000017 | 0.000040 | 0.00296 | 0.44× | 0.27× | 2.7% | 8.9% |
| Spójny | small_world | 1 | tiny | dense | 400 | 0.000019 | 0.000057 | 0.00500 | 0.35× | 0.10× | 2.2% | 3.3% |
| Spójny | small_world | 1 | small | sparse | 1000 | 0.000128 | 0.000321 | 0.000931 | 0.40× | 0.13× | 2.5% | 4.2% |
| Spójny | small_world | 1 | small | medium | 2000 | 0.000181 | 0.000466 | 0.000999 | 0.40× | 0.14× | 2.5% | 4.8% |
| Spójny | small_world | 1 | small | dense | 4000 | 0.000220 | 0.000611 | 0.00116 | 0.36× | 0.17× | 2.3% | 5.8% |
| Spójny | small_world | 1 | medium | sparse | 10000 | 0.00149 | 0.00341 | 0.00537 | 0.44× | 0.24× | 2.7% | 8.0% |
| Spójny | small_world | 1 | medium | medium | 20000 | 0.00183 | 0.00664 | 0.00634 | 0.28× | 0.26× | 1.7% | 8.7% |
| Spójny | small_world | 1 | medium | dense | 40000 | 0.00271 | 0.00609 | 0.00844 | 0.44× | 0.29× | 2.8% | 9.8% |
| Spójny | small_world | 1 | large | sparse | 100000 | 0.01597 | 0.02942 | 0.05889 | 0.54× | 0.33× | 3.4% | 11.1% |
| Spójny | small_world | 1 | large | medium | 200000 | 0.02240 | 0.03230 | 0.07533 | 0.69× | 0.38× | 4.3% | 12.5% |
| Spójny | small_world | 1 | large | dense | 400000 | 0.03327 | 0.03351 | 0.1082 | 0.99× | 0.37× | 6.2% | 12.4% |
| Spójny | small_world | 1 | huge | sparse | 1000000 | 0.2819 | 0.3630 | 1.2165 | 0.78× | 0.26× | 4.9% | 8.5% |
| Spójny | small_world | 1 | huge | medium | 2000000 | 0.3920 | 0.2788 | 1.3896 | 1.41× | 0.35× | 8.8% | 11.6% |
| Spójny | small_world | 1 | huge | dense | 4000000 | 0.5342 | 0.3370 | 1.8321 | 1.59× | 0.37× | 10.0% | 12.2% |
| Niespójny | bb_bb | few | tiny | sparse | 90 | 0.000013 | 0.000026 | 0.00130 | 0.51× | 0.70× | 3.2% | 23.5% |
| Niespójny | bb_bb | few | tiny | medium | 170 | 0.000015 | 0.000031 | 0.00295 | 0.50× | 0.19× | 3.1% | 6.4% |
| Niespójny | bb_bb | few | tiny | dense | 303 | 0.000017 | 0.000041 | 0.00399 | 0.41× | 0.07× | 2.6% | 2.4% |
| Niespójny | bb_bb | few | small | sparse | 990 | 0.000101 | 0.000251 | 0.00195 | 0.40× | 0.08× | 2.5% | 2.5% |
| Niespójny | bb_bb | few | small | medium | 1970 | 0.000121 | 0.000338 | 0.00176 | 0.36× | 0.08× | 2.2% | 2.8% |
| Niespójny | bb_bb | few | small | dense | 3900 | 0.000168 | 0.000497 | 0.00199 | 0.34× | 0.10× | 2.1% | 3.3% |
| Niespójny | bb_bb | few | medium | sparse | 9990 | 0.00131 | 0.00348 | 0.00626 | 0.40× | 0.21× | 2.5% | 7.0% |
| Niespójny | bb_bb | few | medium | medium | 19970 | 0.00149 | 0.00523 | 0.00700 | 0.28× | 0.24× | 1.8% | 8.1% |
| Niespójny | bb_bb | few | medium | dense | 39900 | 0.00234 | 0.00601 | 0.00905 | 0.39× | 0.27× | 2.4% | 9.0% |
| Niespójny | bb_bb | few | large | sparse | 99990 | 0.01281 | 0.03489 | 0.06802 | 0.37× | 0.30× | 2.3% | 10.1% |
| Niespójny | bb_bb | few | large | medium | 199970 | 0.01733 | 0.02967 | 0.07871 | 0.58× | 0.31× | 3.7% | 10.4% |
| Niespójny | bb_bb | few | large | dense | 399900 | 0.02653 | 0.03256 | 0.1182 | 0.82× | 0.38× | 5.1% | 12.7% |
| Niespójny | bb_bb | few | huge | sparse | 999990 | 0.2250 | 0.2343 | 1.2412 | 0.96× | 0.25× | 6.0% | 8.2% |
| Niespójny | bb_bb | few | huge | medium | 1999970 | 0.3054 | 0.2497 | 1.7408 | 1.22× | 0.28× | 7.6% | 9.3% |
| Niespójny | bb_bb | few | huge | dense | 3999900 | 0.4550 | 0.3068 | 2.2665 | 1.48× | 0.31× | 9.3% | 10.3% |
| Niespójny | bb_bb | medium | small | sparse | 900 | 0.000107 | 0.000251 | 0.00711 | 0.43× | 0.12× | 2.7% | 4.0% |
| Niespójny | bb_bb | medium | small | medium | 1700 | 0.000174 | 0.000383 | 0.00602 | 0.45× | 0.29× | 2.8% | 9.7% |
| Niespójny | bb_bb | medium | small | dense | 3042 | 0.000163 | 0.000436 | 0.00563 | 0.37× | 0.15× | 2.3% | 5.1% |
| Niespójny | bb_bb | medium | medium | sparse | 9900 | 0.00122 | 0.00324 | 0.01074 | 0.38× | 0.13× | 2.4% | 4.2% |
| Niespójny | bb_bb | medium | medium | medium | 19700 | 0.00160 | 0.00389 | 0.01078 | 0.41× | 0.14× | 2.5% | 4.6% |
| Niespójny | bb_bb | medium | medium | dense | 39006 | 0.00198 | 0.00617 | 0.01253 | 0.33× | 0.17× | 2.0% | 5.5% |
| Niespójny | bb_bb | medium | large | sparse | 99900 | 0.01099 | 0.03689 | 0.06544 | 0.30× | 0.27× | 1.9% | 9.0% |
| Niespójny | bb_bb | medium | large | medium | 199700 | 0.01475 | 0.04785 | 0.06536 | 0.31× | 0.28× | 1.9% | 9.4% |
| Niespójny | bb_bb | medium | large | dense | 399000 | 0.02262 | 0.05444 | 0.08679 | 0.42× | 0.32× | 2.6% | 10.6% |
| Niespójny | bb_bb | medium | huge | sparse | 999900 | 0.1908 | 0.3662 | 0.9321 | 0.52× | 0.24× | 3.3% | 7.9% |
| Niespójny | bb_bb | medium | huge | medium | 1999700 | 0.2470 | 0.3144 | 1.1110 | 0.79× | 0.26× | 4.9% | 8.6% |
| Niespójny | bb_bb | medium | huge | dense | 3999000 | 0.3437 | 0.3521 | 1.5216 | 0.98× | 0.26× | 6.1% | 8.8% |
| Niespójny | bb_bb | many | medium | sparse | 9000 | 0.00138 | 0.00335 | 0.05150 | 0.42× | 0.06× | 2.6% | 1.9% |
| Niespójny | bb_bb | many | medium | medium | 17000 | 0.00164 | 0.00362 | 0.04879 | 0.45× | 0.05× | 2.8% | 1.7% |
| Niespójny | bb_bb | many | medium | dense | 30395 | 0.00183 | 0.00496 | 0.04819 | 0.38× | 0.05× | 2.4% | 1.8% |
| Niespójny | bb_bb | many | large | sparse | 99000 | 0.01131 | 0.02505 | 0.1100 | 0.45× | 0.16× | 2.8% | 5.5% |
| Niespójny | bb_bb | many | large | medium | 197000 | 0.01515 | 0.03599 | 0.1262 | 0.42× | 0.18× | 2.6% | 6.1% |
| Niespójny | bb_bb | many | large | dense | 390028 | 0.01963 | 0.04892 | 0.1247 | 0.40× | 0.20× | 2.5% | 6.7% |
| Niespójny | bb_bb | many | huge | sparse | 999000 | 0.1731 | 0.3853 | 0.9499 | 0.45× | 0.21× | 2.8% | 7.0% |
| Niespójny | bb_bb | many | huge | medium | 1997000 | 0.2188 | 0.5054 | 1.1146 | 0.43× | 0.23× | 2.7% | 7.6% |
| Niespójny | bb_bb | many | huge | dense | 3990002 | 0.2919 | 0.5687 | 1.4651 | 0.51× | 0.23× | 3.2% | 7.6% |
| Niespójny | bb_grid | few | tiny | sparse | 102 | 0.000015 | 0.000030 | 0.00134 | 0.50× | 0.56× | 3.1% | 18.7% |
| Niespójny | bb_grid | few | tiny | medium | 156 | 0.000014 | 0.000030 | 0.00310 | 0.47× | 0.20× | 3.0% | 6.5% |
| Niespójny | bb_grid | few | tiny | dense | 254 | 0.000018 | 0.000041 | 0.00513 | 0.45× | 0.10× | 2.8% | 3.3% |
| Niespójny | bb_grid | few | small | sparse | 1338 | 0.000111 | 0.000287 | 0.00170 | 0.39× | 0.08× | 2.4% | 2.6% |
| Niespójny | bb_grid | few | small | medium | 1932 | 0.000122 | 0.000333 | 0.00178 | 0.37× | 0.08× | 2.3% | 2.8% |
| Niespójny | bb_grid | few | small | dense | 3162 | 0.000146 | 0.000436 | 0.00176 | 0.33× | 0.10× | 2.1% | 3.2% |
| Niespójny | bb_grid | few | medium | sparse | 14215 | 0.00145 | 0.00396 | 0.00606 | 0.37× | 0.22× | 2.3% | 7.3% |
| Niespójny | bb_grid | few | medium | medium | 19397 | 0.00153 | 0.00506 | 0.00646 | 0.30× | 0.23× | 1.9% | 7.7% |
| Niespójny | bb_grid | few | medium | dense | 32839 | 0.00208 | 0.00515 | 0.00824 | 0.40× | 0.24× | 2.5% | 8.1% |
| Niespójny | bb_grid | few | large | sparse | 117532 | 0.01321 | 0.03186 | 0.06421 | 0.42× | 0.30× | 2.6% | 9.9% |
| Niespójny | bb_grid | few | large | medium | 179434 | 0.01536 | 0.03094 | 0.06624 | 0.50× | 0.32× | 3.1% | 10.7% |
| Niespójny | bb_grid | few | large | dense | 302100 | 0.02095 | 0.03467 | 0.09365 | 0.61× | 0.33× | 3.8% | 11.1% |
| Niespójny | bb_grid | few | huge | sparse | 1319816 | 0.2322 | 0.2810 | 1.3733 | 0.83× | 0.23× | 5.2% | 7.8% |
| Niespójny | bb_grid | few | huge | medium | 1916269 | 0.3066 | 0.2831 | 1.7352 | 1.09× | 0.26× | 6.8% | 8.7% |
| Niespójny | bb_grid | few | huge | dense | 3165854 | 0.3804 | 0.3366 | 2.0149 | 1.14× | 0.30× | 7.1% | 10.1% |
| Niespójny | bb_grid | medium | small | sparse | 1055 | 0.000114 | 0.000267 | 0.00949 | 0.42× | 0.07× | 2.7% | 2.4% |
| Niespójny | bb_grid | medium | small | medium | 1470 | 0.000125 | 0.000320 | 0.00541 | 0.39× | 0.19× | 2.5% | 6.5% |
| Niespójny | bb_grid | medium | small | dense | 2193 | 0.000142 | 0.000366 | 0.00565 | 0.39× | 0.22× | 2.4% | 7.5% |
| Niespójny | bb_grid | medium | medium | sparse | 13152 | 0.00131 | 0.00363 | 0.00980 | 0.37× | 0.14× | 2.3% | 4.6% |
| Niespójny | bb_grid | medium | medium | medium | 17812 | 0.00143 | 0.00383 | 0.01013 | 0.38× | 0.14× | 2.4% | 4.7% |
| Niespójny | bb_grid | medium | medium | dense | 26555 | 0.00164 | 0.00471 | 0.01183 | 0.35× | 0.15× | 2.2% | 5.0% |
| Niespójny | bb_grid | medium | large | sparse | 135780 | 0.01197 | 0.03375 | 0.06101 | 0.35× | 0.28× | 2.2% | 9.4% |
| Niespójny | bb_grid | medium | large | medium | 189979 | 0.01395 | 0.04097 | 0.07106 | 0.34× | 0.31× | 2.1% | 10.4% |
| Niespójny | bb_grid | medium | large | dense | 274527 | 0.01669 | 0.04382 | 0.08376 | 0.38× | 0.32× | 2.4% | 10.6% |
| Niespójny | bb_grid | medium | huge | sparse | 1388138 | 0.1995 | 0.3596 | 1.0959 | 0.55× | 0.23× | 3.5% | 7.5% |
| Niespójny | bb_grid | medium | huge | medium | 1871924 | 0.2354 | 0.3409 | 1.1755 | 0.69× | 0.24× | 4.3% | 7.8% |
| Niespójny | bb_grid | medium | huge | dense | 2940123 | 0.2850 | 0.3555 | 1.4369 | 0.80× | 0.25× | 5.0% | 8.2% |
| Niespójny | bb_grid | many | medium | sparse | 10532 | 0.00135 | 0.00307 | 0.04730 | 0.44× | 0.06× | 2.7% | 1.9% |
| Niespójny | bb_grid | many | medium | medium | 14646 | 0.00178 | 0.00410 | 0.04691 | 0.43× | 0.05× | 2.7% | 1.7% |
| Niespójny | bb_grid | many | medium | dense | 20978 | 0.00177 | 0.00429 | 0.04890 | 0.42× | 0.06× | 2.6% | 2.0% |
| Niespójny | bb_grid | many | large | sparse | 129648 | 0.01147 | 0.02863 | 0.1102 | 0.40× | 0.17× | 2.5% | 5.8% |
| Niespójny | bb_grid | many | large | medium | 178858 | 0.01326 | 0.03189 | 0.1065 | 0.42× | 0.18× | 2.6% | 6.0% |
| Niespójny | bb_grid | many | large | dense | 279979 | 0.01615 | 0.04184 | 0.1238 | 0.39× | 0.20× | 2.4% | 6.8% |
| Niespójny | bb_grid | many | huge | sparse | 1374399 | 0.1832 | 0.3627 | 1.0567 | 0.51× | 0.22× | 3.2% | 7.3% |
| Niespójny | bb_grid | many | huge | medium | 1876812 | 0.2081 | 0.4318 | 1.1788 | 0.48× | 0.21× | 3.0% | 7.1% |
| Niespójny | bb_grid | many | huge | dense | 2866692 | 0.2432 | 0.4770 | 1.3316 | 0.51× | 0.23× | 3.2% | 7.6% |
| Niespójny | bb_random | few | tiny | sparse | 146 | 0.000015 | 0.000030 | 0.00133 | 0.50× | 0.59× | 3.1% | 19.7% |
| Niespójny | bb_random | few | tiny | medium | 303 | 0.000017 | 0.000041 | 0.00242 | 0.41× | 0.20× | 2.6% | 6.7% |
| Niespójny | bb_random | few | tiny | dense | 491 | 0.000022 | 0.000057 | 0.00322 | 0.38× | 0.07× | 2.4% | 2.4% |
| Niespójny | bb_random | few | small | sparse | 1698 | 0.000118 | 0.000316 | 0.00165 | 0.37× | 0.08× | 2.3% | 2.8% |
| Niespójny | bb_random | few | small | medium | 5274 | 0.000225 | 0.000614 | 0.00201 | 0.36× | 0.11× | 2.3% | 3.8% |
| Niespójny | bb_random | few | small | dense | 8032 | 0.000253 | 0.000824 | 0.00215 | 0.31× | 0.12× | 1.9% | 3.9% |
| Niespójny | bb_random | few | medium | sparse | 15592 | 0.00142 | 0.00419 | 0.00635 | 0.35× | 0.21× | 2.2% | 6.9% |
| Niespójny | bb_random | few | medium | medium | 40223 | 0.00232 | 0.00585 | 0.00853 | 0.39× | 0.24× | 2.5% | 8.0% |
| Niespójny | bb_random | few | medium | dense | 88349 | 0.00370 | 0.00741 | 0.01277 | 0.49× | 0.28× | 3.1% | 9.4% |
| Niespójny | bb_random | few | large | sparse | 160098 | 0.01549 | 0.03422 | 0.06110 | 0.45× | 0.27× | 2.8% | 9.1% |
| Niespójny | bb_random | few | large | medium | 530522 | 0.03682 | 0.03625 | 0.1349 | 1.00× | 0.33× | 6.3% | 11.1% |
| Niespójny | bb_random | few | large | dense | 779832 | 0.04753 | 0.04252 | 0.1663 | 1.08× | 0.35× | 6.8% | 11.8% |
| Niespójny | bb_random | few | huge | sparse | 1880678 | 0.2968 | 0.2544 | 1.3199 | 1.16× | 0.26× | 7.3% | 8.8% |
| Niespójny | bb_random | few | huge | medium | 4164556 | 0.4601 | 0.3090 | 1.9165 | 1.49× | 0.30× | 9.3% | 9.8% |
| Niespójny | bb_random | few | huge | dense | 9977208 | 0.9281 | 0.4245 | 4.1748 | 2.18× | 0.30× | 13.6% | 9.9% |
| Niespójny | bb_random | medium | small | sparse | 1958 | 0.000154 | 0.000373 | 0.01762 | 0.41× | 0.06× | 2.6% | 2.0% |
| Niespójny | bb_random | medium | small | medium | 3670 | 0.000176 | 0.000494 | 0.00592 | 0.36× | 0.19× | 2.2% | 6.4% |
| Niespójny | bb_random | medium | small | dense | 5142 | 0.000214 | 0.000614 | 0.00600 | 0.35× | 0.17× | 2.2% | 5.7% |
| Niespójny | bb_random | medium | medium | sparse | 20162 | 0.00153 | 0.00433 | 0.01045 | 0.36× | 0.14× | 2.2% | 4.6% |
| Niespójny | bb_random | medium | medium | medium | 57809 | 0.00236 | 0.00721 | 0.01519 | 0.33× | 0.19× | 2.1% | 6.2% |
| Niespójny | bb_random | medium | medium | dense | 91908 | 0.00341 | 0.00990 | 0.01668 | 0.34× | 0.21× | 2.1% | 6.9% |
| Niespójny | bb_random | medium | large | sparse | 209768 | 0.01497 | 0.04540 | 0.06814 | 0.33× | 0.27× | 2.1% | 9.1% |
| Niespójny | bb_random | medium | large | medium | 544583 | 0.02895 | 0.05791 | 0.1487 | 0.50× | 0.36× | 3.1% | 12.1% |
| Niespójny | bb_random | medium | large | dense | 907282 | 0.04350 | 0.07661 | 0.1854 | 0.57× | 0.36× | 3.6% | 12.1% |
| Niespójny | bb_random | medium | huge | sparse | 1972149 | 0.2437 | 0.3656 | 1.1343 | 0.67× | 0.26× | 4.2% | 8.6% |
| Niespójny | bb_random | medium | huge | medium | 5588756 | 0.4256 | 0.3918 | 2.0004 | 1.09× | 0.28× | 6.8% | 9.4% |
| Niespójny | bb_random | medium | huge | dense | 9571396 | 0.5605 | 0.4915 | 2.6969 | 1.14× | 0.28× | 7.1% | 9.3% |
| Niespójny | bb_random | many | medium | sparse | 18517 | 0.00149 | 0.00364 | 0.04930 | 0.41× | 0.06× | 2.6% | 1.8% |
| Niespójny | bb_random | many | medium | medium | 38728 | 0.00211 | 0.00582 | 0.05159 | 0.37× | 0.06× | 2.3% | 2.1% |
| Niespójny | bb_random | many | medium | dense | 53224 | 0.00238 | 0.00670 | 0.06121 | 0.35× | 0.07× | 2.2% | 2.2% |
| Niespójny | bb_random | many | large | sparse | 200465 | 0.01527 | 0.03575 | 0.1244 | 0.43× | 0.20× | 2.7% | 6.7% |
| Niespójny | bb_random | many | large | medium | 525670 | 0.02605 | 0.06300 | 0.1654 | 0.41× | 0.25× | 2.6% | 8.2% |
| Niespójny | bb_random | many | large | dense | 927131 | 0.03935 | 0.09550 | 0.2231 | 0.41× | 0.26× | 2.6% | 8.7% |
| Niespójny | bb_random | many | huge | sparse | 1980401 | 0.2238 | 0.4864 | 1.1207 | 0.46× | 0.23× | 2.9% | 7.8% |
| Niespójny | bb_random | many | huge | medium | 5460196 | 0.3541 | 0.6122 | 1.6135 | 0.58× | 0.24× | 3.6% | 8.0% |
| Niespójny | bb_random | many | huge | dense | 9455642 | 0.4591 | 0.8092 | 2.1644 | 0.57× | 0.24× | 3.5% | 8.1% |
| Niespójny | bb_small_world | few | tiny | sparse | 94 | 0.000013 | 0.000026 | 0.00148 | 0.52× | 0.51× | 3.2% | 16.8% |
| Niespójny | bb_small_world | few | tiny | medium | 179 | 0.000015 | 0.000032 | 0.00376 | 0.47× | 0.11× | 2.9% | 3.6% |
| Niespójny | bb_small_world | few | tiny | dense | 326 | 0.000019 | 0.000046 | 0.00352 | 0.41× | 0.16× | 2.5% | 5.4% |
| Niespójny | bb_small_world | few | small | sparse | 994 | 0.000099 | 0.000252 | 0.00167 | 0.39× | 0.07× | 2.4% | 2.5% |
| Niespójny | bb_small_world | few | small | medium | 1982 | 0.000124 | 0.000340 | 0.00171 | 0.37× | 0.09× | 2.3% | 3.1% |
| Niespójny | bb_small_world | few | small | dense | 3940 | 0.000171 | 0.000503 | 0.00189 | 0.34× | 0.11× | 2.1% | 3.8% |
| Niespójny | bb_small_world | few | medium | sparse | 9994 | 0.00140 | 0.00334 | 0.00576 | 0.42× | 0.20× | 2.6% | 6.8% |
| Niespójny | bb_small_world | few | medium | medium | 19982 | 0.00158 | 0.00486 | 0.00672 | 0.33× | 0.22× | 2.1% | 7.5% |
| Niespójny | bb_small_world | few | medium | dense | 39940 | 0.00212 | 0.00635 | 0.00966 | 0.34× | 0.27× | 2.1% | 8.9% |
| Niespójny | bb_small_world | few | large | sparse | 99994 | 0.01332 | 0.03356 | 0.05537 | 0.40× | 0.32× | 2.5% | 10.8% |
| Niespójny | bb_small_world | few | large | medium | 199982 | 0.01753 | 0.03266 | 0.07841 | 0.54× | 0.35× | 3.4% | 11.7% |
| Niespójny | bb_small_world | few | large | dense | 399940 | 0.02634 | 0.03389 | 0.1157 | 0.78× | 0.39× | 4.9% | 13.0% |
| Niespójny | bb_small_world | few | huge | sparse | 999994 | 0.2225 | 0.2646 | 1.2574 | 0.84× | 0.25× | 5.3% | 8.2% |
| Niespójny | bb_small_world | few | huge | medium | 1999982 | 0.2928 | 0.2578 | 1.5944 | 1.14× | 0.27× | 7.1% | 8.9% |
| Niespójny | bb_small_world | few | huge | dense | 3999940 | 0.4384 | 0.3095 | 2.1777 | 1.41× | 0.31× | 8.8% | 10.4% |
| Niespójny | bb_small_world | medium | small | sparse | 944 | 0.000119 | 0.000266 | 0.00824 | 0.45× | 0.11× | 2.8% | 3.6% |
| Niespójny | bb_small_world | medium | small | medium | 1805 | 0.000134 | 0.000336 | 0.00562 | 0.40× | 0.20× | 2.5% | 6.8% |
| Niespójny | bb_small_world | medium | small | dense | 3276 | 0.000167 | 0.000457 | 0.00587 | 0.37× | 0.18× | 2.3% | 6.1% |
| Niespójny | bb_small_world | medium | medium | sparse | 9949 | 0.00128 | 0.00334 | 0.01038 | 0.38× | 0.13× | 2.4% | 4.2% |
| Niespójny | bb_small_world | medium | medium | medium | 19846 | 0.00153 | 0.00409 | 0.01096 | 0.38× | 0.15× | 2.4% | 5.0% |
| Niespójny | bb_small_world | medium | medium | dense | 39453 | 0.00190 | 0.00618 | 0.01311 | 0.32× | 0.16× | 2.0% | 5.4% |
| Niespójny | bb_small_world | medium | large | sparse | 99950 | 0.01130 | 0.03051 | 0.06584 | 0.37× | 0.29× | 2.3% | 9.6% |
| Niespójny | bb_small_world | medium | large | medium | 199850 | 0.01470 | 0.04561 | 0.06899 | 0.32× | 0.29× | 2.0% | 9.7% |
| Niespójny | bb_small_world | medium | large | dense | 399497 | 0.02317 | 0.05608 | 0.09198 | 0.41× | 0.32× | 2.6% | 10.8% |
| Niespójny | bb_small_world | medium | huge | sparse | 999950 | 0.1933 | 0.3289 | 0.9628 | 0.59× | 0.26× | 3.7% | 8.6% |
| Niespójny | bb_small_world | medium | huge | medium | 1999850 | 0.2398 | 0.3676 | 1.1667 | 0.65× | 0.26× | 4.1% | 8.6% |
| Niespójny | bb_small_world | medium | huge | dense | 3999500 | 0.3230 | 0.3793 | 1.4862 | 0.85× | 0.26× | 5.3% | 8.7% |
| Niespójny | bb_small_world | many | medium | sparse | 9452 | 0.00146 | 0.00337 | 0.04926 | 0.44× | 0.06× | 2.7% | 1.9% |
| Niespójny | bb_small_world | many | medium | medium | 18026 | 0.00169 | 0.00415 | 0.04957 | 0.41× | 0.06× | 2.5% | 1.9% |
| Niespójny | bb_small_world | many | medium | dense | 32633 | 0.00186 | 0.00499 | 0.05056 | 0.38× | 0.06× | 2.4% | 2.0% |
| Niespójny | bb_small_world | many | large | sparse | 99493 | 0.01077 | 0.02588 | 0.09789 | 0.42× | 0.17× | 2.6% | 5.6% |
| Niespójny | bb_small_world | many | large | medium | 198464 | 0.01461 | 0.03602 | 0.1186 | 0.41× | 0.19× | 2.5% | 6.4% |
| Niespójny | bb_small_world | many | large | dense | 394749 | 0.02024 | 0.04895 | 0.1389 | 0.41× | 0.22× | 2.6% | 7.3% |
| Niespójny | bb_small_world | many | huge | sparse | 999500 | 0.1733 | 0.3377 | 0.9408 | 0.51× | 0.23× | 3.2% | 7.5% |
| Niespójny | bb_small_world | many | huge | medium | 1998494 | 0.2253 | 0.4829 | 1.1091 | 0.47× | 0.23× | 2.9% | 7.6% |
| Niespójny | bb_small_world | many | huge | dense | 3994990 | 0.2889 | 0.6090 | 1.5003 | 0.47× | 0.23× | 3.0% | 7.6% |
| Niespójny | grid_bb | few | tiny | sparse | 111 | 0.000014 | 0.000029 | 0.00129 | 0.48× | 0.63× | 3.0% | 21.0% |
| Niespójny | grid_bb | few | tiny | medium | 144 | 0.000015 | 0.000031 | 0.00401 | 0.49× | 0.15× | 3.1% | 5.0% |
| Niespójny | grid_bb | few | tiny | dense | 212 | 0.000016 | 0.000034 | 0.00485 | 0.45× | 0.06× | 2.8% | 2.1% |
| Niespójny | grid_bb | few | small | sparse | 1310 | 0.000107 | 0.000301 | 0.00168 | 0.36× | 0.09× | 2.2% | 2.9% |
| Niespójny | grid_bb | few | small | medium | 1748 | 0.000118 | 0.000327 | 0.00167 | 0.36× | 0.08× | 2.3% | 2.8% |
| Niespójny | grid_bb | few | small | dense | 2187 | 0.000127 | 0.000362 | 0.00228 | 0.35× | 0.07× | 2.2% | 2.5% |
| Niespójny | grid_bb | few | medium | sparse | 12457 | 0.00132 | 0.00399 | 0.00585 | 0.34× | 0.21× | 2.1% | 7.0% |
| Niespójny | grid_bb | few | medium | medium | 17612 | 0.00156 | 0.00477 | 0.00590 | 0.33× | 0.23× | 2.1% | 7.8% |
| Niespójny | grid_bb | few | medium | dense | 26716 | 0.00179 | 0.00442 | 0.00696 | 0.40× | 0.24× | 2.5% | 7.9% |
| Niespójny | grid_bb | few | large | sparse | 144607 | 0.01323 | 0.03386 | 0.05332 | 0.39× | 0.26× | 2.4% | 8.7% |
| Niespójny | grid_bb | few | large | medium | 186986 | 0.01616 | 0.03110 | 0.05844 | 0.52× | 0.29× | 3.3% | 9.6% |
| Niespójny | grid_bb | few | large | dense | 301625 | 0.02029 | 0.03388 | 0.07775 | 0.60× | 0.33× | 3.8% | 10.9% |
| Niespójny | grid_bb | few | huge | sparse | 1575812 | 0.2279 | 0.3247 | 1.0953 | 0.70× | 0.24× | 4.4% | 8.1% |
| Niespójny | grid_bb | few | huge | medium | 1901426 | 0.2734 | 0.3120 | 1.4149 | 0.89× | 0.24× | 5.5% | 8.1% |
| Niespójny | grid_bb | few | huge | dense | 2439898 | 0.3011 | 0.3356 | 1.3537 | 0.90× | 0.27× | 5.6% | 8.9% |
| Niespójny | grid_bb | medium | small | sparse | 1066 | 0.000191 | 0.000475 | 0.00771 | 0.40× | 0.10× | 2.5% | 3.2% |
| Niespójny | grid_bb | medium | small | medium | 1453 | 0.000122 | 0.000322 | 0.00516 | 0.38× | 0.18× | 2.4% | 6.1% |
| Niespójny | grid_bb | medium | small | dense | 2120 | 0.000142 | 0.000378 | 0.00517 | 0.38× | 0.27× | 2.3% | 9.1% |
| Niespójny | grid_bb | medium | medium | sparse | 12947 | 0.00153 | 0.00354 | 0.00931 | 0.43× | 0.13× | 2.7% | 4.2% |
| Niespójny | grid_bb | medium | medium | medium | 17852 | 0.00132 | 0.00387 | 0.00980 | 0.35× | 0.13× | 2.2% | 4.5% |
| Niespójny | grid_bb | medium | medium | dense | 28233 | 0.00169 | 0.00497 | 0.01103 | 0.35× | 0.15× | 2.2% | 4.8% |
| Niespójny | grid_bb | medium | large | sparse | 136976 | 0.01154 | 0.03272 | 0.05257 | 0.35× | 0.24× | 2.2% | 8.1% |
| Niespójny | grid_bb | medium | large | medium | 189516 | 0.01457 | 0.04307 | 0.05777 | 0.34× | 0.25× | 2.1% | 8.4% |
| Niespójny | grid_bb | medium | large | dense | 286355 | 0.01627 | 0.04504 | 0.06561 | 0.36× | 0.27× | 2.3% | 9.0% |
| Niespójny | grid_bb | medium | huge | sparse | 1384342 | 0.2003 | 0.3639 | 0.9309 | 0.55× | 0.24× | 3.4% | 8.1% |
| Niespójny | grid_bb | medium | huge | medium | 1928976 | 0.2343 | 0.3364 | 1.0539 | 0.70× | 0.26× | 4.4% | 8.5% |
| Niespójny | grid_bb | medium | huge | dense | 2896820 | 0.2886 | 0.3543 | 1.3812 | 0.81× | 0.26× | 5.1% | 8.7% |
| Niespójny | grid_bb | many | medium | sparse | 10630 | 0.00150 | 0.00345 | 0.04494 | 0.45× | 0.05× | 2.8% | 1.7% |
| Niespójny | grid_bb | many | medium | medium | 14606 | 0.00169 | 0.00397 | 0.04533 | 0.42× | 0.05× | 2.6% | 1.7% |
| Niespójny | grid_bb | many | medium | dense | 21438 | 0.00170 | 0.00431 | 0.04572 | 0.39× | 0.06× | 2.5% | 1.8% |
| Niespójny | grid_bb | many | large | sparse | 130460 | 0.01089 | 0.02848 | 0.09036 | 0.38× | 0.14× | 2.4% | 4.8% |
| Niespójny | grid_bb | many | large | medium | 178117 | 0.01316 | 0.03366 | 0.09784 | 0.39× | 0.16× | 2.5% | 5.3% |
| Niespójny | grid_bb | many | large | dense | 273210 | 0.01559 | 0.04122 | 0.1059 | 0.38× | 0.18× | 2.4% | 5.8% |
| Niespójny | grid_bb | many | huge | sparse | 1367053 | 0.1895 | 0.3753 | 0.9964 | 0.51× | 0.23× | 3.2% | 7.5% |
| Niespójny | grid_bb | many | huge | medium | 1881786 | 0.2110 | 0.4368 | 1.0801 | 0.48× | 0.23× | 3.0% | 7.6% |
| Niespójny | grid_bb | many | huge | dense | 2881994 | 0.2498 | 0.4810 | 1.3033 | 0.52× | 0.23× | 3.2% | 7.8% |
| Niespójny | grid_grid | few | tiny | - | 134 | 0.000014 | 0.000029 | 0.00146 | 0.48× | 0.77× | 3.0% | 25.6% |
| Niespójny | grid_grid | few | small | - | 1525 | 0.000109 | 0.000314 | 0.00199 | 0.35× | 0.09× | 2.2% | 3.1% |
| Niespójny | grid_grid | few | medium | - | 18146 | 0.00147 | 0.00368 | 0.00740 | 0.40× | 0.22× | 2.5% | 7.2% |
| Niespójny | grid_grid | few | large | - | 189532 | 0.01483 | 0.03314 | 0.08135 | 0.45× | 0.33× | 2.8% | 11.1% |
| Niespójny | grid_grid | few | huge | - | 1762768 | 0.2400 | 0.3521 | 1.5406 | 0.68× | 0.22× | 4.2% | 7.2% |
| Niespójny | grid_grid | medium | small | - | 1231 | 0.000116 | 0.000299 | 0.00908 | 0.39× | 0.09× | 2.4% | 3.1% |
| Niespójny | grid_grid | medium | medium | - | 15637 | 0.00148 | 0.00376 | 0.00994 | 0.39× | 0.13× | 2.4% | 4.3% |
| Niespójny | grid_grid | medium | large | - | 174006 | 0.01279 | 0.03124 | 0.07418 | 0.41× | 0.31× | 2.6% | 10.4% |
| Niespójny | grid_grid | medium | huge | - | 1831115 | 0.2163 | 0.3470 | 1.1962 | 0.62× | 0.23× | 3.9% | 7.8% |
| Niespójny | grid_grid | many | medium | - | 12178 | 0.00158 | 0.00383 | 0.05028 | 0.41× | 0.07× | 2.6% | 2.3% |
| Niespójny | grid_grid | many | large | - | 158415 | 0.01236 | 0.03158 | 0.1135 | 0.39× | 0.18× | 2.4% | 6.1% |
| Niespójny | grid_grid | many | huge | - | 1724894 | 0.1971 | 0.3422 | 1.2594 | 0.58× | 0.21× | 3.6% | 6.9% |
| Niespójny | grid_random | few | tiny | sparse | 185 | 0.000016 | 0.000034 | 0.00134 | 0.48× | 0.64× | 3.0% | 21.4% |
| Niespójny | grid_random | few | tiny | medium | 298 | 0.000018 | 0.000041 | 0.00512 | 0.46× | 0.07× | 2.9% | 2.3% |
| Niespójny | grid_random | few | tiny | dense | 304 | 0.000018 | 0.000043 | 0.00492 | 0.42× | 0.09× | 2.6% | 3.1% |
| Niespójny | grid_random | few | small | sparse | 2098 | 0.000128 | 0.000352 | 0.00176 | 0.36× | 0.09× | 2.3% | 2.9% |
| Niespójny | grid_random | few | small | medium | 3574 | 0.000167 | 0.000476 | 0.00187 | 0.36× | 0.10× | 2.2% | 3.4% |
| Niespójny | grid_random | few | small | dense | 7653 | 0.000284 | 0.000858 | 0.00207 | 0.33× | 0.14× | 2.1% | 4.8% |
| Niespójny | grid_random | few | medium | sparse | 22742 | 0.00172 | 0.00449 | 0.00688 | 0.38× | 0.24× | 2.4% | 7.9% |
| Niespójny | grid_random | few | medium | medium | 52246 | 0.00254 | 0.00529 | 0.01046 | 0.49× | 0.25× | 3.0% | 8.3% |
| Niespójny | grid_random | few | medium | dense | 89697 | 0.00368 | 0.00718 | 0.01367 | 0.51× | 0.27× | 3.2% | 9.1% |
| Niespójny | grid_random | few | large | sparse | 233307 | 0.01665 | 0.03408 | 0.08052 | 0.49× | 0.34× | 3.1% | 11.2% |
| Niespójny | grid_random | few | large | medium | 456125 | 0.02891 | 0.03745 | 0.1217 | 0.77× | 0.37× | 4.8% | 12.4% |
| Niespójny | grid_random | few | large | dense | 669261 | 0.04063 | 0.04450 | 0.1633 | 0.87× | 0.37× | 5.5% | 12.4% |
| Niespójny | grid_random | few | huge | sparse | 2380125 | 0.3247 | 0.3314 | 1.7964 | 0.99× | 0.28× | 6.2% | 9.2% |
| Niespójny | grid_random | few | huge | medium | 4667923 | 0.5354 | 0.3999 | 2.8255 | 1.30× | 0.27× | 8.1% | 9.1% |
| Niespójny | grid_random | few | huge | dense | 7880126 | 0.7864 | 0.4617 | 3.8463 | 1.72× | 0.28× | 10.8% | 9.3% |
| Niespójny | grid_random | medium | small | sparse | 1951 | 0.000137 | 0.000357 | 0.01110 | 0.38× | 0.06× | 2.4% | 2.0% |
| Niespójny | grid_random | medium | small | medium | 3421 | 0.000172 | 0.000477 | 0.00581 | 0.36× | 0.22× | 2.3% | 7.2% |
| Niespójny | grid_random | medium | small | dense | 4042 | 0.000183 | 0.000522 | 0.00574 | 0.35× | 0.20× | 2.2% | 6.5% |
| Niespójny | grid_random | medium | medium | sparse | 22186 | 0.00165 | 0.00474 | 0.01047 | 0.35× | 0.14× | 2.2% | 4.8% |
| Niespójny | grid_random | medium | medium | medium | 51502 | 0.00242 | 0.00701 | 0.01334 | 0.35× | 0.17× | 2.2% | 5.6% |
| Niespójny | grid_random | medium | medium | dense | 75545 | 0.00295 | 0.00883 | 0.01440 | 0.34× | 0.19× | 2.1% | 6.3% |
| Niespójny | grid_random | medium | large | sparse | 227909 | 0.01429 | 0.04426 | 0.06570 | 0.32× | 0.28× | 2.0% | 9.4% |
| Niespójny | grid_random | medium | large | medium | 534110 | 0.02664 | 0.05135 | 0.1191 | 0.52× | 0.33× | 3.2% | 10.9% |
| Niespójny | grid_random | medium | large | dense | 914852 | 0.04628 | 0.06869 | 0.1696 | 0.67× | 0.37× | 4.2% | 12.5% |
| Niespójny | grid_random | medium | huge | sparse | 2383028 | 0.2603 | 0.3591 | 1.3387 | 0.72× | 0.26× | 4.5% | 8.7% |
| Niespójny | grid_random | medium | huge | medium | 5596534 | 0.4213 | 0.4151 | 1.9103 | 1.02× | 0.28× | 6.3% | 9.2% |
| Niespójny | grid_random | medium | huge | dense | 8762049 | 0.5532 | 0.4870 | 2.5894 | 1.14× | 0.27× | 7.1% | 9.1% |
| Niespójny | grid_random | many | medium | sparse | 19999 | 0.00162 | 0.00383 | 0.04647 | 0.42× | 0.06× | 2.7% | 1.9% |
| Niespójny | grid_random | many | medium | medium | 37823 | 0.00206 | 0.00579 | 0.04735 | 0.36× | 0.06× | 2.3% | 2.0% |
| Niespójny | grid_random | many | medium | dense | 43149 | 0.00232 | 0.00633 | 0.04736 | 0.37× | 0.07× | 2.3% | 2.2% |
| Niespójny | grid_random | many | large | sparse | 230880 | 0.01413 | 0.04053 | 0.1007 | 0.35× | 0.16× | 2.2% | 5.4% |
| Niespójny | grid_random | many | large | medium | 523137 | 0.02411 | 0.06169 | 0.1288 | 0.39× | 0.20× | 2.4% | 6.7% |
| Niespójny | grid_random | many | large | dense | 820252 | 0.03777 | 0.08401 | 0.1610 | 0.45× | 0.25× | 2.8% | 8.2% |
| Niespójny | grid_random | many | huge | sparse | 2354812 | 0.2382 | 0.4672 | 1.1227 | 0.51× | 0.24× | 3.2% | 8.0% |
| Niespójny | grid_random | many | huge | medium | 5311802 | 0.3487 | 0.5407 | 1.5892 | 0.64× | 0.23× | 4.0% | 7.8% |
| Niespójny | grid_random | many | huge | dense | 8315547 | 0.4322 | 0.6982 | 1.9275 | 0.62× | 0.24× | 3.9% | 8.1% |
| Niespójny | grid_small_world | few | tiny | sparse | 122 | 0.000014 | 0.000028 | 0.00130 | 0.50× | 0.55× | 3.1% | 18.4% |
| Niespójny | grid_small_world | few | tiny | medium | 147 | 0.000015 | 0.000031 | 0.00401 | 0.47× | 0.15× | 3.0% | 5.1% |
| Niespójny | grid_small_world | few | tiny | dense | 195 | 0.000015 | 0.000034 | 0.00429 | 0.46× | 0.10× | 2.9% | 3.2% |
| Niespójny | grid_small_world | few | small | sparse | 1376 | 0.000109 | 0.000300 | 0.00169 | 0.36× | 0.08× | 2.3% | 2.6% |
| Niespójny | grid_small_world | few | small | medium | 1776 | 0.000121 | 0.000334 | 0.00164 | 0.36× | 0.09× | 2.3% | 2.9% |
| Niespójny | grid_small_world | few | small | dense | 2691 | 0.000144 | 0.000405 | 0.00174 | 0.36× | 0.09× | 2.2% | 3.1% |
| Niespójny | grid_small_world | few | medium | sparse | 15736 | 0.00148 | 0.00364 | 0.00563 | 0.40× | 0.24× | 2.5% | 8.1% |
| Niespójny | grid_small_world | few | medium | medium | 19090 | 0.00158 | 0.00400 | 0.00611 | 0.39× | 0.23× | 2.5% | 7.6% |
| Niespójny | grid_small_world | few | medium | dense | 25784 | 0.00151 | 0.00510 | 0.00665 | 0.31× | 0.25× | 1.9% | 8.2% |
| Niespójny | grid_small_world | few | large | sparse | 146230 | 0.01315 | 0.02983 | 0.05534 | 0.44× | 0.28× | 2.8% | 9.3% |
| Niespójny | grid_small_world | few | large | medium | 191406 | 0.01597 | 0.03668 | 0.06524 | 0.44× | 0.28× | 2.7% | 9.3% |
| Niespójny | grid_small_world | few | large | dense | 301367 | 0.01972 | 0.03323 | 0.07978 | 0.59× | 0.33× | 3.7% | 11.1% |
| Niespójny | grid_small_world | few | huge | sparse | 1673971 | 0.2347 | 0.3503 | 1.3115 | 0.67× | 0.22× | 4.2% | 7.4% |
| Niespójny | grid_small_world | few | huge | medium | 1965455 | 0.2607 | 0.3970 | 1.4032 | 0.68× | 0.23× | 4.3% | 7.7% |
| Niespójny | grid_small_world | few | huge | dense | 2563830 | 0.2885 | 0.3415 | 1.4840 | 0.85× | 0.25× | 5.3% | 8.3% |
| Niespójny | grid_small_world | medium | small | sparse | 1119 | 0.000116 | 0.000289 | 0.00790 | 0.40× | 0.13× | 2.5% | 4.3% |
| Niespójny | grid_small_world | medium | small | medium | 1564 | 0.000126 | 0.000317 | 0.00576 | 0.40× | 0.43× | 2.5% | 14.4% |
| Niespójny | grid_small_world | medium | small | dense | 2330 | 0.000144 | 0.000388 | 0.00527 | 0.37× | 0.20× | 2.3% | 6.8% |
| Niespójny | grid_small_world | medium | medium | sparse | 12858 | 0.00139 | 0.00350 | 0.00953 | 0.40× | 0.13× | 2.5% | 4.2% |
| Niespójny | grid_small_world | medium | medium | medium | 18082 | 0.00143 | 0.00399 | 0.01036 | 0.36× | 0.13× | 2.3% | 4.4% |
| Niespójny | grid_small_world | medium | medium | dense | 27250 | 0.00165 | 0.00514 | 0.01150 | 0.32× | 0.14× | 2.0% | 4.7% |
| Niespójny | grid_small_world | medium | large | sparse | 138886 | 0.01137 | 0.02784 | 0.05559 | 0.41× | 0.25× | 2.6% | 8.3% |
| Niespójny | grid_small_world | medium | large | medium | 186818 | 0.01475 | 0.03667 | 0.05668 | 0.40× | 0.28× | 2.5% | 9.4% |
| Niespójny | grid_small_world | medium | large | dense | 288152 | 0.01625 | 0.04728 | 0.07113 | 0.34× | 0.28× | 2.2% | 9.5% |
| Niespójny | grid_small_world | medium | huge | sparse | 1460424 | 0.2061 | 0.3203 | 1.0254 | 0.64× | 0.25× | 4.0% | 8.3% |
| Niespójny | grid_small_world | medium | huge | medium | 1928236 | 0.2286 | 0.3860 | 1.0910 | 0.59× | 0.25× | 3.7% | 8.4% |
| Niespójny | grid_small_world | medium | huge | dense | 2964086 | 0.2691 | 0.3809 | 1.4728 | 0.71× | 0.25× | 4.4% | 8.3% |
| Niespójny | grid_small_world | many | medium | sparse | 11143 | 0.00141 | 0.00363 | 0.04830 | 0.40× | 0.06× | 2.5% | 2.0% |
| Niespójny | grid_small_world | many | medium | medium | 15553 | 0.00154 | 0.00401 | 0.05185 | 0.39× | 0.06× | 2.4% | 2.1% |
| Niespójny | grid_small_world | many | medium | dense | 23994 | 0.00166 | 0.00417 | 0.05110 | 0.39× | 0.07× | 2.5% | 2.3% |
| Niespójny | grid_small_world | many | large | sparse | 129814 | 0.01111 | 0.02923 | 0.1071 | 0.38× | 0.18× | 2.4% | 5.9% |
| Niespójny | grid_small_world | many | large | medium | 178531 | 0.01400 | 0.03330 | 0.1178 | 0.42× | 0.18× | 2.6% | 6.0% |
| Niespójny | grid_small_world | many | large | dense | 276202 | 0.01549 | 0.04046 | 0.1316 | 0.38× | 0.20× | 2.4% | 6.8% |
| Niespójny | grid_small_world | many | huge | sparse | 1359464 | 0.1864 | 0.3187 | 1.1194 | 0.59× | 0.22× | 3.7% | 7.4% |
| Niespójny | grid_small_world | many | huge | medium | 1883224 | 0.2133 | 0.4002 | 1.3397 | 0.53× | 0.21× | 3.3% | 7.1% |
| Niespójny | grid_small_world | many | huge | dense | 2853549 | 0.2468 | 0.4941 | 1.4723 | 0.50× | 0.23× | 3.1% | 7.6% |
| Niespójny | random_bb | few | tiny | sparse | 190 | 0.000017 | 0.000032 | 0.00145 | 0.52× | 1.16× | 3.3% | 38.8% |
| Niespójny | random_bb | few | tiny | medium | 412 | 0.000019 | 0.000048 | 0.00367 | 0.41× | 0.11× | 2.6% | 3.8% |
| Niespójny | random_bb | few | tiny | dense | 662 | 0.000025 | 0.000067 | 0.00643 | 0.37× | 0.05× | 2.3% | 1.7% |
| Niespójny | random_bb | few | small | sparse | 2258 | 0.000147 | 0.000405 | 0.00174 | 0.37× | 0.10× | 2.3% | 3.5% |
| Niespójny | random_bb | few | small | medium | 6448 | 0.000221 | 0.000685 | 0.00216 | 0.32× | 0.11× | 2.0% | 3.7% |
| Niespójny | random_bb | few | small | dense | 9662 | 0.000285 | 0.000990 | 0.00230 | 0.29× | 0.14× | 1.8% | 4.6% |
| Niespójny | random_bb | few | medium | sparse | 17441 | 0.00131 | 0.00494 | 0.00819 | 0.26× | 0.21× | 1.7% | 6.9% |
| Niespójny | random_bb | few | medium | medium | 57872 | 0.00260 | 0.00626 | 0.01107 | 0.42× | 0.26× | 2.6% | 8.6% |
| Niespójny | random_bb | few | medium | dense | 97129 | 0.00367 | 0.00884 | 0.01517 | 0.42× | 0.28× | 2.6% | 9.2% |
| Niespójny | random_bb | few | large | sparse | 231500 | 0.01889 | 0.03167 | 0.09166 | 0.60× | 0.34× | 3.7% | 11.3% |
| Niespójny | random_bb | few | large | medium | 613492 | 0.03648 | 0.03903 | 0.1613 | 0.93× | 0.37× | 5.8% | 12.2% |
| Niespójny | random_bb | few | large | dense | 1155884 | 0.06471 | 0.05178 | 0.2541 | 1.23× | 0.34× | 7.7% | 11.2% |
| Niespójny | random_bb | few | huge | sparse | 2087066 | 0.3029 | 0.2570 | 1.5694 | 1.18× | 0.28× | 7.3% | 9.4% |
| Niespójny | random_bb | few | huge | medium | 6819888 | 0.6747 | 0.3790 | 3.3094 | 1.77× | 0.31× | 11.1% | 10.4% |
| Niespójny | random_bb | few | huge | dense | 11106602 | 0.9402 | 0.4307 | 4.9737 | 2.18× | 0.32× | 13.6% | 10.5% |
| Niespójny | random_bb | medium | small | sparse | 1826 | 0.000129 | 0.000328 | 0.01354 | 0.39× | 0.05× | 2.5% | 1.6% |
| Niespójny | random_bb | medium | small | medium | 3937 | 0.000172 | 0.000484 | 0.00601 | 0.36× | 0.26× | 2.2% | 8.8% |
| Niespójny | random_bb | medium | small | dense | 5367 | 0.000209 | 0.000608 | 0.00579 | 0.35× | 0.17× | 2.2% | 5.7% |
| Niespójny | random_bb | medium | medium | sparse | 20160 | 0.00187 | 0.00502 | 0.01168 | 0.37× | 0.15× | 2.3% | 5.0% |
| Niespójny | random_bb | medium | medium | medium | 54618 | 0.00243 | 0.00666 | 0.01365 | 0.37× | 0.17× | 2.3% | 5.8% |
| Niespójny | random_bb | medium | medium | dense | 89942 | 0.00321 | 0.01046 | 0.01627 | 0.31× | 0.20× | 1.9% | 6.7% |
| Niespójny | random_bb | medium | large | sparse | 194048 | 0.01473 | 0.04261 | 0.07397 | 0.35× | 0.31× | 2.2% | 10.2% |
| Niespójny | random_bb | medium | large | medium | 548370 | 0.02744 | 0.05602 | 0.1189 | 0.49× | 0.35× | 3.1% | 11.7% |
| Niespójny | random_bb | medium | large | dense | 951440 | 0.04248 | 0.07867 | 0.1878 | 0.54× | 0.33× | 3.4% | 10.9% |
| Niespójny | random_bb | medium | huge | sparse | 1974946 | 0.2420 | 0.3561 | 1.0764 | 0.68× | 0.27× | 4.2% | 9.0% |
| Niespójny | random_bb | medium | huge | medium | 5488952 | 0.3944 | 0.3851 | 1.7618 | 1.02× | 0.29× | 6.4% | 9.6% |
| Niespójny | random_bb | medium | huge | dense | 8997001 | 0.5180 | 0.4617 | 2.2450 | 1.12× | 0.28× | 7.0% | 9.4% |
| Niespójny | random_bb | many | medium | sparse | 18212 | 0.00146 | 0.00376 | 0.04917 | 0.39× | 0.07× | 2.5% | 2.4% |
| Niespójny | random_bb | many | medium | medium | 40448 | 0.00197 | 0.00610 | 0.05148 | 0.33× | 0.06× | 2.1% | 2.1% |
| Niespójny | random_bb | many | medium | dense | 52924 | 0.00237 | 0.00707 | 0.04796 | 0.34× | 0.06× | 2.1% | 2.1% |
| Niespójny | random_bb | many | large | sparse | 201311 | 0.01478 | 0.03469 | 0.1122 | 0.43× | 0.18× | 2.7% | 5.9% |
| Niespójny | random_bb | many | large | medium | 560930 | 0.02481 | 0.06447 | 0.1472 | 0.38× | 0.23× | 2.4% | 7.5% |
| Niespójny | random_bb | many | large | dense | 929209 | 0.04000 | 0.09195 | 0.1662 | 0.43× | 0.24× | 2.7% | 8.0% |
| Niespójny | random_bb | many | huge | sparse | 1998640 | 0.2147 | 0.4691 | 1.0472 | 0.46× | 0.25× | 2.9% | 8.4% |
| Niespójny | random_bb | many | huge | medium | 5619710 | 0.3380 | 0.6002 | 1.5236 | 0.56× | 0.25× | 3.5% | 8.3% |
| Niespójny | random_bb | many | huge | dense | 9575022 | 0.4655 | 0.8008 | 1.8848 | 0.58× | 0.25× | 3.6% | 8.4% |
| Niespójny | random_grid | few | tiny | sparse | 213 | 0.000016 | 0.000035 | 0.00134 | 0.47× | 0.61× | 2.9% | 20.2% |
| Niespójny | random_grid | few | tiny | medium | 372 | 0.000019 | 0.000047 | 0.00344 | 0.41× | 0.12× | 2.6% | 4.0% |
| Niespójny | random_grid | few | tiny | dense | 528 | 0.000021 | 0.000056 | 0.00769 | 0.38× | 0.04× | 2.4% | 1.4% |
| Niespójny | random_grid | few | small | sparse | 2453 | 0.000133 | 0.000364 | 0.00174 | 0.37× | 0.09× | 2.3% | 3.1% |
| Niespójny | random_grid | few | small | medium | 5570 | 0.000203 | 0.000627 | 0.00197 | 0.33× | 0.11× | 2.0% | 3.5% |
| Niespójny | random_grid | few | small | dense | 8452 | 0.000263 | 0.000957 | 0.00225 | 0.30× | 0.13× | 1.9% | 4.4% |
| Niespójny | random_grid | few | medium | sparse | 24721 | 0.00163 | 0.00508 | 0.00726 | 0.33× | 0.23× | 2.0% | 7.8% |
| Niespójny | random_grid | few | medium | medium | 73686 | 0.00326 | 0.00655 | 0.01209 | 0.49× | 0.27× | 3.1% | 8.9% |
| Niespójny | random_grid | few | medium | dense | 88862 | 0.00352 | 0.00782 | 0.01250 | 0.44× | 0.27× | 2.7% | 9.1% |
| Niespójny | random_grid | few | large | sparse | 260888 | 0.01965 | 0.03261 | 0.06922 | 0.61× | 0.31× | 3.8% | 10.4% |
| Niespójny | random_grid | few | large | medium | 581708 | 0.03743 | 0.03886 | 0.1259 | 0.96× | 0.36× | 6.0% | 11.9% |
| Niespójny | random_grid | few | large | dense | 814748 | 0.04679 | 0.04546 | 0.1502 | 1.02× | 0.37× | 6.4% | 12.2% |
| Niespójny | random_grid | few | huge | sparse | 2621480 | 0.3535 | 0.3126 | 1.4903 | 1.14× | 0.29× | 7.1% | 9.6% |
| Niespójny | random_grid | few | huge | medium | 6077096 | 0.6118 | 0.4068 | 2.4763 | 1.48× | 0.31× | 9.3% | 10.2% |
| Niespójny | random_grid | few | huge | dense | 10061875 | 0.8728 | 0.4642 | 3.6049 | 1.82× | 0.31× | 11.4% | 10.2% |
| Niespójny | random_grid | medium | small | sparse | 1987 | 0.000149 | 0.000394 | 0.01419 | 0.38× | 0.09× | 2.4% | 2.9% |
| Niespójny | random_grid | medium | small | medium | 3708 | 0.000175 | 0.000470 | 0.00530 | 0.37× | 0.30× | 2.3% | 10.1% |
| Niespójny | random_grid | medium | small | dense | 4416 | 0.000183 | 0.000530 | 0.00537 | 0.35× | 0.31× | 2.2% | 10.2% |
| Niespójny | random_grid | medium | medium | sparse | 22167 | 0.00153 | 0.00423 | 0.01039 | 0.36× | 0.14× | 2.3% | 4.8% |
| Niespójny | random_grid | medium | medium | medium | 53666 | 0.00222 | 0.00676 | 0.01258 | 0.33× | 0.17× | 2.1% | 5.8% |
| Niespójny | random_grid | medium | medium | dense | 85991 | 0.00322 | 0.00992 | 0.01499 | 0.33× | 0.20× | 2.0% | 6.7% |
| Niespójny | random_grid | medium | large | sparse | 232183 | 0.01601 | 0.04260 | 0.06314 | 0.38× | 0.27× | 2.3% | 8.9% |
| Niespójny | random_grid | medium | large | medium | 536603 | 0.02723 | 0.05055 | 0.08993 | 0.54× | 0.31× | 3.4% | 10.2% |
| Niespójny | random_grid | medium | large | dense | 817673 | 0.03864 | 0.06645 | 0.1181 | 0.58× | 0.34× | 3.6% | 11.4% |
| Niespójny | random_grid | medium | huge | sparse | 2358368 | 0.2488 | 0.3543 | 0.9734 | 0.70× | 0.28× | 4.4% | 9.2% |
| Niespójny | random_grid | medium | huge | medium | 5472311 | 0.3932 | 0.4037 | 1.5334 | 0.97× | 0.28× | 6.1% | 9.3% |
| Niespójny | random_grid | medium | huge | dense | 8473950 | 0.4993 | 0.4780 | 2.0373 | 1.04× | 0.29× | 6.5% | 9.5% |
| Niespójny | random_grid | many | medium | sparse | 19944 | 0.00158 | 0.00384 | 0.04540 | 0.41× | 0.06× | 2.5% | 2.0% |
| Niespójny | random_grid | many | medium | medium | 36856 | 0.00200 | 0.00591 | 0.04568 | 0.35× | 0.06× | 2.2% | 2.0% |
| Niespójny | random_grid | many | medium | dense | 43517 | 0.00229 | 0.00636 | 0.04651 | 0.36× | 0.06× | 2.3% | 2.1% |
| Niespójny | random_grid | many | large | sparse | 230976 | 0.01376 | 0.03926 | 0.09864 | 0.35× | 0.17× | 2.2% | 5.6% |
| Niespójny | random_grid | many | large | medium | 523377 | 0.02398 | 0.06170 | 0.1243 | 0.39× | 0.20× | 2.4% | 6.8% |
| Niespójny | random_grid | many | large | dense | 812187 | 0.03481 | 0.08572 | 0.1542 | 0.41× | 0.23× | 2.5% | 7.5% |
| Niespójny | random_grid | many | huge | sparse | 2364670 | 0.2279 | 0.4628 | 0.9644 | 0.49× | 0.25× | 3.1% | 8.2% |
| Niespójny | random_grid | many | huge | medium | 5407895 | 0.3462 | 0.5397 | 1.3445 | 0.64× | 0.25× | 4.0% | 8.3% |
| Niespójny | random_grid | many | huge | dense | 8309444 | 0.4151 | 0.6896 | 1.6871 | 0.60× | 0.25× | 3.8% | 8.3% |
| Niespójny | random_random | few | tiny | sparse | 284 | 0.000027 | 0.000071 | 0.00938 | 0.38× | 0.08× | 2.4% | 2.8% |
| Niespójny | random_random | few | tiny | medium | 629 | 0.000025 | 0.000068 | 0.00377 | 0.37× | 0.16× | 2.3% | 5.4% |
| Niespójny | random_random | few | tiny | dense | 700 | 0.000027 | 0.000075 | 0.00538 | 0.37× | 0.15× | 2.3% | 4.9% |
| Niespójny | random_random | few | small | sparse | 2998 | 0.000205 | 0.000536 | 0.00176 | 0.38× | 0.10× | 2.4% | 3.5% |
| Niespójny | random_random | few | small | medium | 8968 | 0.000342 | 0.000991 | 0.00226 | 0.34× | 0.14× | 2.2% | 4.6% |
| Niespójny | random_random | few | small | dense | 14882 | 0.000604 | 0.00178 | 0.00267 | 0.35× | 0.16× | 2.2% | 5.3% |
| Niespójny | random_random | few | medium | sparse | 30000 | 0.00243 | 0.00674 | 0.00781 | 0.36× | 0.25× | 2.3% | 8.3% |
| Niespójny | random_random | few | medium | medium | 90000 | 0.00398 | 0.00858 | 0.01388 | 0.46× | 0.28× | 2.9% | 9.2% |
| Niespójny | random_random | few | medium | dense | 149953 | 0.00612 | 0.01094 | 0.01975 | 0.56× | 0.32× | 3.5% | 10.5% |
| Niespójny | random_random | few | large | sparse | 300000 | 0.03067 | 0.03883 | 0.09923 | 0.79× | 0.34× | 4.9% | 11.3% |
| Niespójny | random_random | few | large | medium | 900000 | 0.06480 | 0.05192 | 0.2243 | 1.25× | 0.33× | 7.8% | 11.0% |
| Niespójny | random_random | few | large | dense | 1500000 | 0.08955 | 0.06800 | 0.3192 | 1.32× | 0.32× | 8.2% | 10.8% |
| Niespójny | random_random | few | huge | sparse | 3000000 | 0.4530 | 0.3249 | 2.1014 | 1.40× | 0.30× | 8.7% | 10.1% |
| Niespójny | random_random | few | huge | medium | 9000000 | 1.0124 | 0.4838 | 4.7346 | 2.12× | 0.32× | 13.2% | 10.7% |
| Niespójny | random_random | few | huge | dense | 15000000 | 1.3941 | 0.6018 | 6.3661 | 2.32× | 0.32× | 14.5% | 10.8% |
| Niespójny | random_random | medium | small | sparse | 2784 | 0.000215 | 0.000604 | 0.01553 | 0.36× | 0.11× | 2.2% | 3.7% |
| Niespójny | random_random | medium | small | medium | 6004 | 0.000219 | 0.000668 | 0.00593 | 0.33× | 0.18× | 2.0% | 6.1% |
| Niespójny | random_random | medium | small | dense | 7435 | 0.000262 | 0.000865 | 0.00615 | 0.31× | 0.32× | 1.9% | 10.6% |
| Niespójny | random_random | medium | medium | sparse | 29980 | 0.00194 | 0.00494 | 0.01138 | 0.40× | 0.15× | 2.5% | 5.2% |
| Niespójny | random_random | medium | medium | medium | 89520 | 0.00313 | 0.00922 | 0.01679 | 0.34× | 0.19× | 2.1% | 6.4% |
| Niespójny | random_random | medium | medium | dense | 147830 | 0.00507 | 0.01438 | 0.02119 | 0.35× | 0.24× | 2.2% | 8.0% |
| Niespójny | random_random | medium | large | sparse | 299996 | 0.02491 | 0.05943 | 0.08639 | 0.42× | 0.33× | 2.6% | 11.0% |
| Niespójny | random_random | medium | large | medium | 899970 | 0.04681 | 0.07028 | 0.1446 | 0.67× | 0.35× | 4.2% | 11.7% |
| Niespójny | random_random | medium | large | dense | 1499899 | 0.06204 | 0.1010 | 0.2165 | 0.62× | 0.32× | 3.8% | 10.8% |
| Niespójny | random_random | medium | huge | sparse | 3000000 | 0.3137 | 0.3637 | 1.2762 | 0.86× | 0.28× | 5.4% | 9.2% |
| Niespójny | random_random | medium | huge | medium | 8999982 | 0.5383 | 0.4695 | 2.3099 | 1.15× | 0.29× | 7.2% | 9.6% |
| Niespójny | random_random | medium | huge | dense | 15000000 | 0.7182 | 0.6045 | 3.3342 | 1.19× | 0.28× | 7.4% | 9.5% |
| Niespójny | random_random | many | medium | sparse | 27660 | 0.00192 | 0.00479 | 0.04968 | 0.39× | 0.10× | 2.5% | 3.2% |
| Niespójny | random_random | many | medium | medium | 61676 | 0.00244 | 0.00716 | 0.05404 | 0.34× | 0.07× | 2.1% | 2.4% |
| Niespójny | random_random | many | medium | dense | 74113 | 0.00321 | 0.00838 | 0.05396 | 0.39× | 0.08× | 2.4% | 2.6% |
| Niespójny | random_random | many | large | sparse | 299750 | 0.01621 | 0.04212 | 0.1229 | 0.39× | 0.21× | 2.4% | 7.1% |
| Niespójny | random_random | many | large | medium | 894856 | 0.03735 | 0.09061 | 0.1899 | 0.41× | 0.25× | 2.6% | 8.3% |
| Niespójny | random_random | many | large | dense | 1477720 | 0.05599 | 0.1347 | 0.2572 | 0.42× | 0.25× | 2.6% | 8.4% |
| Niespójny | random_random | many | huge | sparse | 2999987 | 0.2652 | 0.5752 | 1.1845 | 0.46× | 0.25× | 2.9% | 8.4% |
| Niespójny | random_random | many | huge | medium | 8999426 | 0.4314 | 0.7150 | 1.9442 | 0.60× | 0.26× | 3.8% | 8.7% |
| Niespójny | random_random | many | huge | dense | 14997663 | 0.5691 | 1.0252 | 2.5736 | 0.56× | 0.25× | 3.5% | 8.2% |
| Niespójny | random_small_world | few | tiny | sparse | 172 | 0.000015 | 0.000031 | 0.00131 | 0.50× | 0.58× | 3.1% | 19.3% |
| Niespójny | random_small_world | few | tiny | medium | 448 | 0.000019 | 0.000050 | 0.00349 | 0.39× | 0.17× | 2.4% | 5.5% |
| Niespójny | random_small_world | few | tiny | dense | 470 | 0.000020 | 0.000053 | 0.00607 | 0.38× | 0.09× | 2.3% | 3.0% |
| Niespójny | random_small_world | few | small | sparse | 1870 | 0.000118 | 0.000324 | 0.00174 | 0.36× | 0.08× | 2.3% | 2.7% |
| Niespójny | random_small_world | few | small | medium | 6073 | 0.000214 | 0.000657 | 0.00207 | 0.33× | 0.11× | 2.0% | 3.7% |
| Niespójny | random_small_world | few | small | dense | 10629 | 0.000393 | 0.00139 | 0.00233 | 0.29× | 0.14× | 1.8% | 4.8% |
| Niespójny | random_small_world | few | medium | sparse | 22754 | 0.00175 | 0.00523 | 0.00728 | 0.34× | 0.22× | 2.1% | 7.4% |
| Niespójny | random_small_world | few | medium | medium | 66598 | 0.00337 | 0.00760 | 0.01138 | 0.45× | 0.27× | 2.8% | 8.9% |
| Niespójny | random_small_world | few | medium | dense | 89764 | 0.00388 | 0.00867 | 0.01276 | 0.45× | 0.28× | 2.8% | 9.4% |
| Niespójny | random_small_world | few | large | sparse | 213305 | 0.01795 | 0.03130 | 0.06812 | 0.57× | 0.30× | 3.6% | 10.1% |
| Niespójny | random_small_world | few | large | medium | 707898 | 0.04451 | 0.04389 | 0.1659 | 1.01× | 0.35× | 6.3% | 11.6% |
| Niespójny | random_small_world | few | large | dense | 1125415 | 0.06340 | 0.05353 | 0.2337 | 1.17× | 0.35× | 7.3% | 11.5% |
| Niespójny | random_small_world | few | huge | sparse | 2457919 | 0.3652 | 0.2893 | 1.6906 | 1.26× | 0.29× | 7.9% | 9.7% |
| Niespójny | random_small_world | few | huge | medium | 6679522 | 0.6634 | 0.3751 | 2.8877 | 1.73× | 0.31× | 10.8% | 10.2% |
| Niespójny | random_small_world | few | huge | dense | 10436276 | 0.8659 | 0.4195 | 3.8355 | 2.04× | 0.30× | 12.8% | 9.9% |
| Niespójny | random_small_world | medium | small | sparse | 1943 | 0.000182 | 0.000422 | 0.01449 | 0.43× | 0.08× | 2.7% | 2.7% |
| Niespójny | random_small_world | medium | small | medium | 4109 | 0.000180 | 0.000505 | 0.00547 | 0.36× | 0.21× | 2.2% | 7.1% |
| Niespójny | random_small_world | medium | small | dense | 5590 | 0.000211 | 0.000622 | 0.00557 | 0.34× | 0.17× | 2.1% | 5.6% |
| Niespójny | random_small_world | medium | medium | sparse | 19590 | 0.00151 | 0.00409 | 0.01029 | 0.37× | 0.14× | 2.3% | 4.5% |
| Niespójny | random_small_world | medium | medium | medium | 55455 | 0.00252 | 0.00732 | 0.01312 | 0.34× | 0.18× | 2.2% | 5.9% |
| Niespójny | random_small_world | medium | medium | dense | 97195 | 0.00337 | 0.01036 | 0.01606 | 0.33× | 0.20× | 2.0% | 6.7% |
| Niespójny | random_small_world | medium | large | sparse | 199655 | 0.01427 | 0.03984 | 0.06064 | 0.36× | 0.27× | 2.2% | 9.0% |
| Niespójny | random_small_world | medium | large | medium | 543664 | 0.02829 | 0.05560 | 0.09645 | 0.51× | 0.33× | 3.2% | 10.9% |
| Niespójny | random_small_world | medium | large | dense | 975796 | 0.04693 | 0.07844 | 0.1372 | 0.60× | 0.33× | 3.8% | 11.1% |
| Niespójny | random_small_world | medium | huge | sparse | 2007810 | 0.2480 | 0.3234 | 0.9661 | 0.77× | 0.27× | 4.8% | 9.1% |
| Niespójny | random_small_world | medium | huge | medium | 5307461 | 0.3864 | 0.4328 | 1.5275 | 0.89× | 0.28× | 5.6% | 9.3% |
| Niespójny | random_small_world | medium | huge | dense | 9902961 | 0.5581 | 0.5115 | 2.3086 | 1.09× | 0.28× | 6.8% | 9.3% |
| Niespójny | random_small_world | many | medium | sparse | 18854 | 0.00155 | 0.00375 | 0.04443 | 0.41× | 0.07× | 2.6% | 2.2% |
| Niespójny | random_small_world | many | medium | medium | 40754 | 0.00287 | 0.00684 | 0.04735 | 0.42× | 0.06× | 2.6% | 2.0% |
| Niespójny | random_small_world | many | medium | dense | 52970 | 0.00248 | 0.00684 | 0.04792 | 0.36× | 0.07× | 2.3% | 2.2% |
| Niespójny | random_small_world | many | large | sparse | 200989 | 0.01452 | 0.03556 | 0.09635 | 0.41× | 0.16× | 2.6% | 5.5% |
| Niespójny | random_small_world | many | large | medium | 551148 | 0.02662 | 0.06704 | 0.1287 | 0.40× | 0.21× | 2.5% | 7.1% |
| Niespójny | random_small_world | many | large | dense | 943056 | 0.03982 | 0.09292 | 0.1674 | 0.43× | 0.24× | 2.7% | 7.9% |
| Niespójny | random_small_world | many | huge | sparse | 1996965 | 0.2220 | 0.4291 | 0.9344 | 0.52× | 0.24× | 3.2% | 8.0% |
| Niespójny | random_small_world | many | huge | medium | 5339960 | 0.3417 | 0.5779 | 1.3520 | 0.59× | 0.25× | 3.7% | 8.3% |
| Niespójny | random_small_world | many | huge | dense | 9595310 | 0.4443 | 0.8120 | 1.8787 | 0.55× | 0.25× | 3.4% | 8.2% |
| Niespójny | small_world_bb | few | tiny | sparse | 96 | 0.000014 | 0.000026 | 0.00130 | 0.53× | 0.78× | 3.3% | 26.0% |
| Niespójny | small_world_bb | few | tiny | medium | 182 | 0.000015 | 0.000032 | 0.00228 | 0.47× | 0.20× | 3.0% | 6.7% |
| Niespójny | small_world_bb | few | tiny | dense | 323 | 0.000017 | 0.000044 | 0.00304 | 0.39× | 0.11× | 2.4% | 3.6% |
| Niespójny | small_world_bb | few | small | sparse | 996 | 0.000103 | 0.000262 | 0.00169 | 0.39× | 0.08× | 2.5% | 2.8% |
| Niespójny | small_world_bb | few | small | medium | 1988 | 0.000125 | 0.000344 | 0.00167 | 0.36× | 0.09× | 2.3% | 3.0% |
| Niespójny | small_world_bb | few | small | dense | 3956 | 0.000171 | 0.000510 | 0.00191 | 0.34× | 0.11× | 2.1% | 3.7% |
| Niespójny | small_world_bb | few | medium | sparse | 9996 | 0.00127 | 0.00323 | 0.00540 | 0.41× | 0.22× | 2.6% | 7.5% |
| Niespójny | small_world_bb | few | medium | medium | 19988 | 0.00159 | 0.00443 | 0.00687 | 0.36× | 0.24× | 2.2% | 7.9% |
| Niespójny | small_world_bb | few | medium | dense | 39955 | 0.00243 | 0.00656 | 0.00823 | 0.37× | 0.25× | 2.3% | 8.4% |
| Niespójny | small_world_bb | few | large | sparse | 99996 | 0.01267 | 0.02884 | 0.05792 | 0.44× | 0.32× | 2.8% | 10.7% |
| Niespójny | small_world_bb | few | large | medium | 199988 | 0.01685 | 0.03633 | 0.08035 | 0.47× | 0.33× | 2.9% | 11.0% |
| Niespójny | small_world_bb | few | large | dense | 399960 | 0.02472 | 0.03587 | 0.1078 | 0.69× | 0.37× | 4.3% | 12.2% |
| Niespójny | small_world_bb | few | huge | sparse | 999996 | 0.2160 | 0.2677 | 1.2576 | 0.81× | 0.24× | 5.0% | 8.1% |
| Niespójny | small_world_bb | few | huge | medium | 1999988 | 0.2833 | 0.2590 | 1.6192 | 1.09× | 0.28× | 6.8% | 9.3% |
| Niespójny | small_world_bb | few | huge | dense | 3999960 | 0.4216 | 0.3058 | 2.2216 | 1.38× | 0.29× | 8.6% | 9.8% |
| Niespójny | small_world_bb | medium | small | sparse | 944 | 0.000115 | 0.000264 | 0.00819 | 0.44× | 0.11× | 2.7% | 3.5% |
| Niespójny | small_world_bb | medium | small | medium | 1805 | 0.000133 | 0.000340 | 0.00536 | 0.39× | 0.20× | 2.4% | 6.7% |
| Niespójny | small_world_bb | medium | small | dense | 3259 | 0.000165 | 0.000457 | 0.00556 | 0.36× | 0.16× | 2.3% | 5.5% |
| Niespójny | small_world_bb | medium | medium | sparse | 9950 | 0.00144 | 0.00372 | 0.01017 | 0.39× | 0.13× | 2.4% | 4.2% |
| Niespójny | small_world_bb | medium | medium | medium | 19843 | 0.00155 | 0.00400 | 0.01031 | 0.39× | 0.14× | 2.4% | 4.7% |
| Niespójny | small_world_bb | medium | medium | dense | 39463 | 0.00199 | 0.00599 | 0.01226 | 0.34× | 0.16× | 2.1% | 5.4% |
| Niespójny | small_world_bb | medium | large | sparse | 99950 | 0.01129 | 0.03139 | 0.06320 | 0.36× | 0.28× | 2.3% | 9.2% |
| Niespójny | small_world_bb | medium | large | medium | 199850 | 0.01536 | 0.04611 | 0.06622 | 0.33× | 0.28× | 2.1% | 9.3% |
| Niespójny | small_world_bb | medium | large | dense | 399500 | 0.02273 | 0.05618 | 0.1150 | 0.40× | 0.31× | 2.5% | 10.4% |
| Niespójny | small_world_bb | medium | huge | sparse | 999950 | 0.1885 | 0.3344 | 1.0909 | 0.56× | 0.23× | 3.5% | 7.6% |
| Niespójny | small_world_bb | medium | huge | medium | 1999850 | 0.2416 | 0.3781 | 1.3360 | 0.64× | 0.22× | 4.0% | 7.4% |
| Niespójny | small_world_bb | medium | huge | dense | 3999500 | 0.3329 | 0.3794 | 1.5391 | 0.88× | 0.26× | 5.5% | 8.5% |
| Niespójny | small_world_bb | many | medium | sparse | 9448 | 0.00147 | 0.00367 | 0.04620 | 0.41× | 0.05× | 2.6% | 1.6% |
| Niespójny | small_world_bb | many | medium | medium | 17989 | 0.00162 | 0.00408 | 0.04797 | 0.40× | 0.05× | 2.5% | 1.8% |
| Niespójny | small_world_bb | many | medium | dense | 32604 | 0.00176 | 0.00517 | 0.05655 | 0.34× | 0.06× | 2.1% | 2.1% |
| Niespójny | small_world_bb | many | large | sparse | 99494 | 0.01143 | 0.02629 | 0.09377 | 0.44× | 0.16× | 2.7% | 5.2% |
| Niespójny | small_world_bb | many | large | medium | 198437 | 0.01508 | 0.03605 | 0.1139 | 0.42× | 0.19× | 2.6% | 6.4% |
| Niespójny | small_world_bb | many | large | dense | 394643 | 0.02007 | 0.04911 | 0.1496 | 0.41× | 0.21× | 2.6% | 7.1% |
| Niespójny | small_world_bb | many | huge | sparse | 999500 | 0.1760 | 0.3356 | 0.9979 | 0.52× | 0.21× | 3.3% | 7.1% |
| Niespójny | small_world_bb | many | huge | medium | 1998493 | 0.2203 | 0.4827 | 1.2127 | 0.46× | 0.21× | 2.9% | 7.1% |
| Niespójny | small_world_bb | many | huge | dense | 3994965 | 0.2985 | 0.6098 | 1.5122 | 0.49× | 0.23× | 3.1% | 7.5% |
| Niespójny | small_world_grid | few | tiny | sparse | 117 | 0.000014 | 0.000028 | 0.00131 | 0.51× | 0.75× | 3.2% | 24.9% |
| Niespójny | small_world_grid | few | tiny | medium | 164 | 0.000015 | 0.000031 | 0.00195 | 0.47× | 0.43× | 3.0% | 14.4% |
| Niespójny | small_world_grid | few | tiny | dense | 272 | 0.000017 | 0.000040 | 0.00370 | 0.42× | 0.13× | 2.6% | 4.4% |
| Niespójny | small_world_grid | few | small | sparse | 1182 | 0.000117 | 0.000276 | 0.00170 | 0.42× | 0.09× | 2.7% | 2.9% |
| Niespójny | small_world_grid | few | small | medium | 1812 | 0.000120 | 0.000335 | 0.00179 | 0.36× | 0.08× | 2.2% | 2.8% |
| Niespójny | small_world_grid | few | small | dense | 3041 | 0.000147 | 0.000438 | 0.00196 | 0.34× | 0.10× | 2.1% | 3.5% |
| Niespójny | small_world_grid | few | medium | sparse | 13986 | 0.00139 | 0.00376 | 0.00597 | 0.38× | 0.22× | 2.3% | 7.4% |
| Niespójny | small_world_grid | few | medium | medium | 17958 | 0.00141 | 0.00376 | 0.00596 | 0.38× | 0.25× | 2.4% | 8.4% |
| Niespójny | small_world_grid | few | medium | dense | 27824 | 0.00173 | 0.00473 | 0.00828 | 0.37× | 0.22× | 2.3% | 7.5% |
| Niespójny | small_world_grid | few | large | sparse | 145476 | 0.01255 | 0.02889 | 0.06714 | 0.44× | 0.35× | 2.7% | 11.5% |
| Niespójny | small_world_grid | few | large | medium | 190257 | 0.01661 | 0.03914 | 0.07283 | 0.43× | 0.35× | 2.7% | 11.6% |
| Niespójny | small_world_grid | few | large | dense | 301534 | 0.02161 | 0.03820 | 0.09791 | 0.57× | 0.36× | 3.5% | 11.8% |
| Niespójny | small_world_grid | few | huge | sparse | 1424935 | 0.2362 | 0.3321 | 1.3904 | 0.71× | 0.23× | 4.5% | 7.8% |
| Niespójny | small_world_grid | few | huge | medium | 1967722 | 0.2732 | 0.3016 | 1.6383 | 0.91× | 0.26× | 5.7% | 8.8% |
| Niespójny | small_world_grid | few | huge | dense | 3088968 | 0.3254 | 0.3412 | 1.8652 | 0.97× | 0.27× | 6.1% | 9.1% |
| Niespójny | small_world_grid | medium | small | sparse | 1119 | 0.000120 | 0.000285 | 0.00840 | 0.42× | 0.08× | 2.6% | 2.8% |
| Niespójny | small_world_grid | medium | small | medium | 1539 | 0.000129 | 0.000321 | 0.00557 | 0.40× | 0.29× | 2.5% | 9.5% |
| Niespójny | small_world_grid | medium | small | dense | 2289 | 0.000146 | 0.000382 | 0.00547 | 0.38× | 0.32× | 2.4% | 10.6% |
| Niespójny | small_world_grid | medium | medium | sparse | 13263 | 0.00132 | 0.00345 | 0.00967 | 0.38× | 0.14× | 2.4% | 4.7% |
| Niespójny | small_world_grid | medium | medium | medium | 18100 | 0.00134 | 0.00384 | 0.01030 | 0.35× | 0.14× | 2.2% | 4.7% |
| Niespójny | small_world_grid | medium | medium | dense | 28039 | 0.00165 | 0.00445 | 0.01108 | 0.37× | 0.16× | 2.3% | 5.4% |
| Niespójny | small_world_grid | medium | large | sparse | 133431 | 0.01207 | 0.02857 | 0.06603 | 0.43× | 0.29× | 2.7% | 9.8% |
| Niespójny | small_world_grid | medium | large | medium | 191161 | 0.01493 | 0.03682 | 0.06918 | 0.41× | 0.31× | 2.5% | 10.5% |
| Niespójny | small_world_grid | medium | large | dense | 285570 | 0.01596 | 0.04715 | 0.08745 | 0.34× | 0.31× | 2.1% | 10.3% |
| Niespójny | small_world_grid | medium | huge | sparse | 1369958 | 0.1987 | 0.3155 | 1.1940 | 0.63× | 0.23× | 3.9% | 7.6% |
| Niespójny | small_world_grid | medium | huge | medium | 1892835 | 0.2215 | 0.3962 | 1.2905 | 0.56× | 0.23× | 3.5% | 7.6% |
| Niespójny | small_world_grid | medium | huge | dense | 2821500 | 0.2616 | 0.3822 | 1.4238 | 0.68× | 0.25× | 4.3% | 8.5% |
| Niespójny | small_world_grid | many | medium | sparse | 11152 | 0.00141 | 0.00352 | 0.04749 | 0.41× | 0.07× | 2.5% | 2.3% |
| Niespójny | small_world_grid | many | medium | medium | 15690 | 0.00159 | 0.00410 | 0.05387 | 0.39× | 0.06× | 2.5% | 2.0% |
| Niespójny | small_world_grid | many | medium | dense | 23511 | 0.00173 | 0.00459 | 0.05209 | 0.39× | 0.06× | 2.4% | 2.1% |
| Niespójny | small_world_grid | many | large | sparse | 130514 | 0.01170 | 0.03033 | 0.1060 | 0.39× | 0.17× | 2.4% | 5.8% |
| Niespójny | small_world_grid | many | large | medium | 180076 | 0.01294 | 0.03364 | 0.1110 | 0.39× | 0.19× | 2.4% | 6.5% |
| Niespójny | small_world_grid | many | large | dense | 282969 | 0.01534 | 0.04279 | 0.1401 | 0.36× | 0.20× | 2.2% | 6.7% |
| Niespójny | small_world_grid | many | huge | sparse | 1384181 | 0.1888 | 0.3178 | 1.2358 | 0.59× | 0.21× | 3.7% | 6.8% |
| Niespójny | small_world_grid | many | huge | medium | 1870261 | 0.2086 | 0.3915 | 1.1945 | 0.53× | 0.22× | 3.3% | 7.2% |
| Niespójny | small_world_grid | many | huge | dense | 2921660 | 0.2484 | 0.5008 | 1.3567 | 0.50× | 0.22× | 3.1% | 7.3% |
| Niespójny | small_world_random | few | tiny | sparse | 138 | 0.000015 | 0.000029 | 0.00126 | 0.51× | 0.71× | 3.2% | 23.7% |
| Niespójny | small_world_random | few | tiny | medium | 350 | 0.000019 | 0.000048 | 0.00173 | 0.40× | 0.54× | 2.5% | 18.0% |
| Niespójny | small_world_random | few | tiny | dense | 362 | 0.000018 | 0.000046 | 0.00796 | 0.40× | 0.07× | 2.5% | 2.3% |
| Niespójny | small_world_random | few | small | sparse | 1602 | 0.000116 | 0.000315 | 0.00178 | 0.37× | 0.09× | 2.3% | 2.8% |
| Niespójny | small_world_random | few | small | medium | 5282 | 0.000211 | 0.000631 | 0.00213 | 0.34× | 0.12× | 2.1% | 3.9% |
| Niespójny | small_world_random | few | small | dense | 8392 | 0.000303 | 0.000957 | 0.00229 | 0.32× | 0.13× | 2.0% | 4.2% |
| Niespójny | small_world_random | few | medium | sparse | 17734 | 0.00143 | 0.00407 | 0.00658 | 0.36× | 0.25× | 2.2% | 8.4% |
| Niespójny | small_world_random | few | medium | medium | 56686 | 0.00290 | 0.00580 | 0.01142 | 0.50× | 0.25× | 3.2% | 8.5% |
| Niespójny | small_world_random | few | medium | dense | 91775 | 0.00372 | 0.00766 | 0.01450 | 0.49× | 0.28× | 3.1% | 9.3% |
| Niespójny | small_world_random | few | large | sparse | 186760 | 0.01694 | 0.02872 | 0.08121 | 0.59× | 0.36× | 3.7% | 12.1% |
| Niespójny | small_world_random | few | large | medium | 517716 | 0.03326 | 0.04293 | 0.1658 | 0.77× | 0.36× | 4.8% | 12.0% |
| Niespójny | small_world_random | few | large | dense | 889531 | 0.05622 | 0.04900 | 0.2578 | 1.12× | 0.36× | 7.0% | 12.0% |
| Niespójny | small_world_random | few | huge | sparse | 1481838 | 0.2592 | 0.3012 | 1.4932 | 0.86× | 0.25× | 5.4% | 8.5% |
| Niespójny | small_world_random | few | huge | medium | 4517754 | 0.5168 | 0.3345 | 2.8249 | 1.49× | 0.30× | 9.3% | 10.2% |
| Niespójny | small_world_random | few | huge | dense | 8267736 | 0.7274 | 0.3879 | 3.8369 | 1.85× | 0.31× | 11.6% | 10.2% |
| Niespójny | small_world_random | medium | small | sparse | 1904 | 0.000142 | 0.000350 | 0.01272 | 0.41× | 0.07× | 2.5% | 2.4% |
| Niespójny | small_world_random | medium | small | medium | 4220 | 0.000193 | 0.000531 | 0.00575 | 0.36× | 0.23× | 2.3% | 7.6% |
| Niespójny | small_world_random | medium | small | dense | 5903 | 0.000220 | 0.000681 | 0.00575 | 0.32× | 0.18× | 2.0% | 5.9% |
| Niespójny | small_world_random | medium | medium | sparse | 20022 | 0.00168 | 0.00477 | 0.01064 | 0.36× | 0.14× | 2.2% | 4.7% |
| Niespójny | small_world_random | medium | medium | medium | 54384 | 0.00234 | 0.00722 | 0.01312 | 0.33× | 0.18× | 2.0% | 6.0% |
| Niespójny | small_world_random | medium | medium | dense | 92622 | 0.00330 | 0.01095 | 0.01665 | 0.30× | 0.20× | 1.9% | 6.7% |
| Niespójny | small_world_random | medium | large | sparse | 203362 | 0.01400 | 0.04135 | 0.07686 | 0.34× | 0.31× | 2.1% | 10.2% |
| Niespójny | small_world_random | medium | large | medium | 583004 | 0.02938 | 0.05781 | 0.1169 | 0.51× | 0.35× | 3.2% | 11.6% |
| Niespójny | small_world_random | medium | large | dense | 951661 | 0.04676 | 0.07987 | 0.1796 | 0.59× | 0.35× | 3.7% | 11.5% |
| Niespójny | small_world_random | medium | huge | sparse | 1961326 | 0.2512 | 0.3301 | 1.2490 | 0.76× | 0.24× | 4.8% | 8.1% |
| Niespójny | small_world_random | medium | huge | medium | 5559699 | 0.4235 | 0.4419 | 1.8777 | 0.96× | 0.27× | 6.0% | 9.1% |
| Niespójny | small_world_random | medium | huge | dense | 10062377 | 0.5862 | 0.5279 | 2.8567 | 1.11× | 0.27× | 6.9% | 9.1% |
| Niespójny | small_world_random | many | medium | sparse | 18708 | 0.00153 | 0.00359 | 0.04885 | 0.42× | 0.07× | 2.6% | 2.5% |
| Niespójny | small_world_random | many | medium | medium | 39532 | 0.00228 | 0.00599 | 0.05075 | 0.39× | 0.07× | 2.4% | 2.3% |
| Niespójny | small_world_random | many | medium | dense | 55873 | 0.00239 | 0.00728 | 0.05352 | 0.33× | 0.07× | 2.1% | 2.5% |
| Niespójny | small_world_random | many | large | sparse | 198988 | 0.01364 | 0.03668 | 0.1184 | 0.37× | 0.18× | 2.3% | 6.2% |
| Niespójny | small_world_random | many | large | medium | 531713 | 0.02551 | 0.06287 | 0.1571 | 0.41× | 0.25× | 2.5% | 8.3% |
| Niespójny | small_world_random | many | large | dense | 942462 | 0.04091 | 0.09636 | 0.2205 | 0.43× | 0.26× | 2.7% | 8.7% |
| Niespójny | small_world_random | many | huge | sparse | 2019464 | 0.2268 | 0.4414 | 1.1645 | 0.51× | 0.23× | 3.2% | 7.6% |
| Niespójny | small_world_random | many | huge | medium | 5466480 | 0.3511 | 0.5892 | 1.7133 | 0.60× | 0.23× | 3.7% | 7.8% |
| Niespójny | small_world_random | many | huge | dense | 9335649 | 0.4609 | 0.8316 | 2.2172 | 0.55× | 0.24× | 3.5% | 8.0% |
| Niespójny | small_world_small_world | few | tiny | sparse | 100 | 0.000015 | 0.000028 | 0.00129 | 0.54× | 0.70× | 3.4% | 23.3% |
| Niespójny | small_world_small_world | few | tiny | medium | 190 | 0.000015 | 0.000033 | 0.00435 | 0.46× | 0.16× | 2.9% | 5.2% |
| Niespójny | small_world_small_world | few | tiny | dense | 349 | 0.000019 | 0.000046 | 0.00339 | 0.42× | 0.15× | 2.6% | 4.9% |
| Niespójny | small_world_small_world | few | small | sparse | 1000 | 0.000100 | 0.000261 | 0.00167 | 0.38× | 0.08× | 2.4% | 2.6% |
| Niespójny | small_world_small_world | few | small | medium | 1999 | 0.000126 | 0.000346 | 0.00185 | 0.36× | 0.10× | 2.3% | 3.2% |
| Niespójny | small_world_small_world | few | small | dense | 3990 | 0.000173 | 0.000518 | 0.00189 | 0.33× | 0.10× | 2.1% | 3.5% |
| Niespójny | small_world_small_world | few | medium | sparse | 10000 | 0.00132 | 0.00340 | 0.00562 | 0.39× | 0.21× | 2.5% | 7.1% |
| Niespójny | small_world_small_world | few | medium | medium | 20000 | 0.00153 | 0.00455 | 0.00645 | 0.34× | 0.24× | 2.1% | 7.9% |
| Niespójny | small_world_small_world | few | medium | dense | 40000 | 0.00236 | 0.00662 | 0.00875 | 0.35× | 0.25× | 2.2% | 8.2% |
| Niespójny | small_world_small_world | few | large | sparse | 100000 | 0.01184 | 0.02587 | 0.05704 | 0.46× | 0.32× | 2.9% | 10.7% |
| Niespójny | small_world_small_world | few | large | medium | 200000 | 0.01848 | 0.04257 | 0.06857 | 0.43× | 0.33× | 2.7% | 10.9% |
| Niespójny | small_world_small_world | few | large | dense | 400000 | 0.02300 | 0.03742 | 0.1014 | 0.62× | 0.36× | 3.8% | 12.2% |
| Niespójny | small_world_small_world | few | huge | sparse | 1000000 | 0.2191 | 0.2995 | 1.3275 | 0.73× | 0.23× | 4.6% | 7.7% |
| Niespójny | small_world_small_world | few | huge | medium | 2000000 | 0.2790 | 0.2660 | 1.6094 | 1.05× | 0.27× | 6.6% | 8.9% |
| Niespójny | small_world_small_world | few | huge | dense | 4000000 | 0.3880 | 0.3005 | 1.9278 | 1.29× | 0.30× | 8.1% | 9.9% |
| Niespójny | small_world_small_world | medium | small | sparse | 987 | 0.000118 | 0.000274 | 0.00784 | 0.43× | 0.13× | 2.7% | 4.2% |
| Niespójny | small_world_small_world | medium | small | medium | 1910 | 0.000139 | 0.000358 | 0.00551 | 0.39× | 0.27× | 2.4% | 9.0% |
| Niespójny | small_world_small_world | medium | small | dense | 3480 | 0.000172 | 0.000470 | 0.00561 | 0.37× | 0.19× | 2.3% | 6.4% |
| Niespójny | small_world_small_world | medium | medium | sparse | 9999 | 0.00130 | 0.00335 | 0.00997 | 0.39× | 0.12× | 2.4% | 3.9% |
| Niespójny | small_world_small_world | medium | medium | medium | 19985 | 0.00150 | 0.00443 | 0.01058 | 0.35× | 0.15× | 2.2% | 4.9% |
| Niespójny | small_world_small_world | medium | medium | dense | 39943 | 0.00216 | 0.00615 | 0.01319 | 0.35× | 0.16× | 2.2% | 5.5% |
| Niespójny | small_world_small_world | medium | large | sparse | 100000 | 0.01154 | 0.02805 | 0.06640 | 0.41× | 0.29× | 2.6% | 9.6% |
| Niespójny | small_world_small_world | medium | large | medium | 200000 | 0.01524 | 0.04250 | 0.07042 | 0.36× | 0.30× | 2.3% | 10.1% |
| Niespójny | small_world_small_world | medium | large | dense | 399993 | 0.02252 | 0.06058 | 0.1065 | 0.37× | 0.32× | 2.3% | 10.8% |
| Niespójny | small_world_small_world | medium | huge | sparse | 1000000 | 0.1925 | 0.2898 | 1.1360 | 0.66× | 0.22× | 4.2% | 7.5% |
| Niespójny | small_world_small_world | medium | huge | medium | 2000000 | 0.2395 | 0.4184 | 1.3009 | 0.57× | 0.24× | 3.6% | 7.9% |
| Niespójny | small_world_small_world | medium | huge | dense | 4000000 | 0.3143 | 0.4019 | 1.6188 | 0.78× | 0.25× | 4.9% | 8.3% |
| Niespójny | small_world_small_world | many | medium | sparse | 9884 | 0.00148 | 0.00349 | 0.04797 | 0.42× | 0.05× | 2.6% | 1.8% |
| Niespójny | small_world_small_world | many | medium | medium | 18992 | 0.00170 | 0.00450 | 0.04887 | 0.38× | 0.06× | 2.4% | 2.0% |
| Niespójny | small_world_small_world | many | medium | dense | 34808 | 0.00183 | 0.00502 | 0.05059 | 0.37× | 0.07× | 2.3% | 2.2% |
| Niespójny | small_world_small_world | many | large | sparse | 99991 | 0.01128 | 0.02606 | 0.1001 | 0.43× | 0.17× | 2.7% | 5.5% |
| Niespójny | small_world_small_world | many | large | medium | 199904 | 0.01437 | 0.03553 | 0.1188 | 0.40× | 0.20× | 2.5% | 6.7% |
| Niespójny | small_world_small_world | many | large | dense | 399515 | 0.02570 | 0.05772 | 0.1529 | 0.44× | 0.21× | 2.8% | 7.1% |
| Niespójny | small_world_small_world | many | huge | sparse | 1000000 | 0.1798 | 0.2889 | 1.1082 | 0.62× | 0.21× | 3.9% | 6.9% |
| Niespójny | small_world_small_world | many | huge | medium | 1999988 | 0.2230 | 0.4458 | 1.2602 | 0.50× | 0.21× | 3.1% | 7.1% |
| Niespójny | small_world_small_world | many | huge | dense | 3999946 | 0.2996 | 0.6608 | 1.5745 | 0.45× | 0.23× | 2.8% | 7.8% |

### 9.4. Interpretacja wyników

#### Co rzeczywiście przyspiesza

Największy zysk daje wersja równoległa dla dużych i gęstych grafów, ponieważ koszt
przejrzenia list sąsiedztwa jest wtedy wystarczająco duży, aby zamortyzować wywołania
`pool.map` i synchronizację kolejnych frontierów. Spośród 602 zagregowanych konfiguracji
60 osiągnęło speedup większy od 1. Najlepsze przykłady to: spójny
`random/dense/huge` (**3,16×**), spójny `random/medium/huge` (**2,82×**),
niespójny `random_random/few/dense/huge` (**2,32×**), niespójny
`random_bb/few/dense/huge` (**2,18×**) oraz niespójny
`bb_random/few/dense/huge` (**2,18×**).

W całym benchmarku wersja równoległa nie uzyskała jednak globalnego przyspieszenia.
Suma średnich czasów sekwencyjnych wyniosła **296,6524 s**, a suma raportowanych czasów
równoległych **346,1617 s**, co daje globalny speedup **0,857×**. Wynik ten jest dodatkowo
korzystny dla wersji równoległej, ponieważ `par_time` nie obejmuje konwersji do CSR ani
kopiowania danych do pamięci współdzielonej. Nie należy więc interpretować **0,857×** jako
pełnego speedupu end-to-end; po doliczeniu przygotowania danych byłby on niższy.

Wariant rozproszony ma naturalne warunki do równoległości dla grafu z kilkoma dużymi,
niezależnymi składowymi. Najbliższa temu jest konfiguracja `few=5`, ponieważ pozwala
obciążyć trzy workery bez tworzenia setek drobnych wiadomości. Sam fakt posiadania wielu
składowych nie wystarcza: przy `many=500` rośnie liczba serializacji i operacji
scatter-gather, a pojedyncze zadania stają się zbyt małe.

Suma średnich czasów baseline'u kontenerowego wyniosła **391,3110 s**, a wersji
rozproszonej **1415,3516 s**, czyli globalny speedup wyniósł **0,277×**. Przy agregacji
stosowanej w tabeli tylko jedna z 602 konfiguracji przekroczyła 1:
`random_bb/few/sparse/tiny` (**1,16×**). Następne wyniki to
`small_world_bb/few/sparse/tiny` (**0,78×**), `grid_grid/few/tiny` (**0,77×**),
`small_world_grid/few/sparse/tiny` (**0,75×**) i
`small_world_random/few/sparse/tiny` (**0,71×**).

Pozorne zwycięstwo dla grafu `tiny` nie jest dowodem skalowalności. Mierzone czasy są
rzędu pojedynczych milisekund, a pierwsza instancja niektórych konfiguracji zawiera
widoczny efekt rozgrzewania środowiska. Średnia ilorazów i iloraz średnich dają przez to
nieco inne rankingi. Wiarygodniejszym wnioskiem jest brak przyspieszenia dla dużych
grafów oraz globalny wynik **0,277×**, a nie pojedynczy rezultat `tiny`.

#### Gdzie pojawia się największy narzut

Profil sekwencyjny dla grafu `bb_bb/many/sparse/huge` (500 000 wierzchołków,
999 000 wpisów list sąsiedztwa i 500 składowych) objął 5 001 073 wywołania funkcji
i trwał **1,466 s**. `load_graph` zajęło **1,173 s** czasu skumulowanego, a
`sequential_bfs` **0,265 s**, w tym 500 wywołań `partial_bfs` zajęło **0,238 s**.
Około 80% czasu pełnego uruchomienia stanowiło więc tekstowe wczytanie i parsowanie
niemal miliona wierszy, a nie właściwy BFS.

W wersji równoległej profil pełnego wywołania trwał **3,307 s**. `load_graph` zajęło
**1,708 s**, `graph_to_csr` **0,489 s**, a raportowany fragment obliczeniowy
`parallel_bfs` tylko **0,038 s** czasu własnego. `pool.map` miało **1,408 s** czasu
skumulowanego, a znaczną część profilu stanowiło oczekiwanie i komunikacja
(`connection.wait`, `connection.poll`, `queues.empty`). Profil dotyczył dużego grafu
z wieloma składowymi, lecz wiele jego frontierów i zadań było małych. Wniosek powinien
zatem dotyczyć zbyt małej pracy na pojedyncze wywołanie IPC, a nie wyłącznie „małych
grafów”.

Profil koordynatora wariantu rozproszonego dla tego samego grafu trwał **4,868 s**.
Największe pozycje to:

- `load_graph`: **1,770 s**,
- całe `distributed_bfs`: **1,543 s**,
- `load_expected`: **0,695 s**,
- detekcja składowych: **0,630 s**,
- sekwencyjny baseline w kontenerze: **0,458 s**,
- utworzenie 500 podgrafów (`extract_subgraph`): **0,406 s**.

Profil potwierdza, że wąskim gardłem koordynatora jest przede wszystkim przygotowanie
danych. Dla całego CSV faza przygotowania podgrafów stanowiła około **41,4%** czasu
rozproszonego, detekcja składowych **29,9%**, wykonanie wraz z komunikacją **28,6%**,
a scheduling tylko **0,02%**.

Każdy worker przetworzył około 166-167 składowych. Jego profil trwał około
**5,05-5,11 s**, ale ponad **4,63 s** przypadało na blokujące `socket.recv`, czyli
oczekiwanie na zadania i dane. Łączny lokalny BFS workera zajmował tylko
**0,12-0,13 s**, deserializacja `pickle.loads` około **0,02-0,03 s**, a wysyłanie
wyników kilka milisekund. Nie potwierdza to tezy, że sama serializacja jest dominującym
kosztem. Największy problem stanowi sekwencyjna praca koordynatora przed wysłaniem zadań
oraz zbyt mały koszt obliczeń przypadający na pojedyncze zadanie.

#### Kiedy dodatkowa złożoność ma sens

Dodatkowa złożoność wersji równoległej ma sens dla największych i najgęstszych grafów,
gdy frontier wielokrotnie przekracza próg równoległości i każdy proces otrzymuje
wystarczająco dużo krawędzi do przejrzenia. Potwierdzają to wyniki `random/huge` oraz
część gęstych konfiguracji `few/huge`. Aby ocenić korzyść end-to-end, należałoby jednak
włączyć do `par_time` konwersję CSR i kopiowanie do pamięci współdzielonej.

Architektura rozproszona ma sens, gdy dane są już rozdzielone między węzły albo gdy
koordynator nie musi wcześniej samodzielnie wykrywać składowych i budować ich pełnych
kopii. Korzystny przypadek powinien zawierać co najmniej tyle dużych, zbliżonych kosztowo
zadań, ilu jest workerów, a czas lokalnych obliczeń powinien być znacznie większy od
kosztu serializacji i transportu. Badany model z centralnym przygotowaniem wszystkich
podgrafów nie spełnił tych warunków.

#### Kiedy dodatkowa złożoność jest przerostem formy nad treścią

Dla małych i rzadkich grafów wersja sekwencyjna jest najlepsza, ponieważ nie ponosi
kosztu tworzenia zadań, synchronizacji i IPC. Najsłabsze konfiguracje równoległe to
między innymi spójny `random/sparse/medium` (**0,04×**), spójny
`bb/sparse/medium` (**0,25×**) oraz niespójny `random_bb/few/sparse/medium`
(**0,26×**). W tych przypadkach praca na frontierze jest zbyt mała względem narzutu.

Wersja rozproszona jest przerostem formy dla grafu spójnego, ponieważ użyteczną pracę
wykonuje jeden worker. Jest również niekorzystna dla setek małych składowych: mimo że
wszystkie trzy workery są zajęte, koordynator musi wykryć 500 składowych, utworzyć
500 słowników podgrafów i wykonać 500 cykli wysłania oraz odbioru. Dlatego zwiększenie
liczby części nie oznacza automatycznie większej skalowalności.

Ostatecznie benchmark potwierdza trzy różne ograniczenia:

1. Dla małej pracy dominuje narzut uruchamiania i komunikacji.
2. Dla grafu spójnego podział wyłącznie po składowych nie daje równoległości.
3. Dla wielu małych składowych centralne przygotowanie i task shipping kosztują więcej
   niż lokalny BFS workerów.

Wniosek o przewadze równoległości jest więc uzasadniony tylko dla wybranych dużych,
gęstych konfiguracji. Wniosek o przewadze obecnej wersji rozproszonej nie znajduje
potwierdzenia w wynikach; implementacja jest wartościowa jako demonstracja architektury
coordinator-worker i analiza narzutów, ale nie jako szybszy zamiennik baseline'u.

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

| Etap                   | Do czego użyto AI                                     | Co zostało przyjęte | Co poprawiono ręcznie |
|------------------------|-------------------------------------------------------| --- | --- |
| [uzupełnić]            | [uzupełnić]                                           | [uzupełnić] | [uzupełnić] |
| [Rozbudowa benchmarka] | [Rozbudowa skryptu generatora grafów, miernika czasu] | [uzupełnić] | [uzupełnić] |

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
