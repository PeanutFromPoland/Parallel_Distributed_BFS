# Rozproszony BFS — Docker Compose

Implementacja rozproszonego algorytmu BFS (Breadth-First Search) w architekturze
**coordinator–worker**, konteneryzowana za pomocą Docker Compose.

## Architektura

```
┌─────────────────┐
│   Coordinator   │  Ładuje grafy, identyfikuje składowe,
│  (coordinator)  │  zachłannie przydziela do workerów,
│                 │  zbiera wyniki, weryfikuje poprawność
└────┬───┬───┬────┘
     │   │   │        TCP (pickle + nagłówek długości)
     ▼   ▼   ▼
┌────┐ ┌────┐ ┌────┐
│ W1 │ │ W2 │ │ W3 │  Workery: odbierają podgrafy,
└────┘ └────┘ └────┘  wykonują sekwencyjny BFS,
                       odsyłają tablice odległości
```

### Optymalizacje

1. **Jawna detekcja składowych BFS** — koordynator wykrywa rzeczywiste
   składowe grafu przed rozdzieleniem pracy. Ten koszt jest wliczany do czasu
   wersji rozproszonej, bo jest konieczny do poprawnego podziału zadań.

2. **Zachłanny przydział workerów** — składowe sortowane malejąco wg liczby
   krawędzi, każda trafia do workera z najmniejszym obciążeniem (LPT scheduling)

3. **Binarny protokół komunikacji** — wiadomości TCP mają nagłówek długości
   i payload `pickle`, co usuwa koszt konwersji kluczy `int` na tekst.

## Wymagania

- Docker Desktop (z Docker Compose v2)
- Wygenerowane grafy w katalogu `../graphs/` (uruchom `python generate_graphs.py`
  w katalogu głównym projektu)

## Uruchomienie

```bash
# 1. Wygeneruj grafy (jeśli nie istnieją)
cd ..
python generate_graphs.py
cd distributed

# 2. Zbuduj i uruchom
docker compose up --build

# 3. (Opcjonalnie) Uruchom w tle
docker compose up --build -d
docker compose logs -f

# 4. Zatrzymaj
docker compose down
```

## Profilowanie jednego dużego grafu

Osobny wariant Compose uruchamia ten sam zestaw węzłów (`coordinator`,
`worker-1`, `worker-2`, `worker-3`), ale ogranicza benchmark do jednego
wskazanego grafu i zapisuje profil `cProfile` dla każdego węzła:

```bash
docker compose -f docker-compose.yml -f docker-compose.profile.yml up --build
```

Domyślnie profilowany jest graf:

```text
/app/graphs/inconsistent/bb_bb/many/sparse/huge_001.txt
```

Inny graf można wskazać zmienną `PROFILE_GRAPH_PATH`:

```bash
PROFILE_GRAPH_PATH=/app/graphs/inconsistent/grid_grid/many/huge_001.txt \
docker compose -f docker-compose.yml -f docker-compose.profile.yml up --build
```

Profile binarne i tekstowe podsumowania trafiają do:

```text
../results/profiles/
```

Domyślny poziom logowania podczas profilowania to `WARNING`, aby obsługa
logów nie zniekształcała wyników. Można go zmienić zmienną
`PROFILE_LOG_LEVEL`.

## Konfiguracja

### Zmienne środowiskowe (coordinator)

| Zmienna         | Domyślna wartość                            | Opis                               |
|-----------------|---------------------------------------------|------------------------------------|
| `WORKERS`       | `worker-1:5000,worker-2:5000,worker-3:5000` | Lista workerów                     |
| `GRAPHS_DIR`    | `/app/graphs`                               | Katalog grafów                     |
| `BENCHMARK_RUNS`| `3`                                         | Liczba prób algorytmu na graf      |
| `RESULTS_DIR`   | `/app/results`                              | Katalog CSV i profilu              |
| `CSV_PATH`      | `/app/results/distributed_bfs_results.csv` | Ścieżka pliku CSV                  |
| `PROFILE_PATH`  | `/app/results/coordinator.prof`             | Ścieżka profilu `cProfile`         |
| `LOG_LEVEL`     | `WARNING`                                   | Poziom logów (`INFO` w Compose)     |

### Zmienne środowiskowe (worker)

| Zmienna       | Domyślna wartość | Opis              |
|---------------|------------------|--------------------|
| `WORKER_PORT` | `5000`           | Port nasłuchiwania |
| `LOG_LEVEL`   | `WARNING`        | Poziom logów (`DEBUG` w Compose) |

### Skalowanie workerów

Pełny test skalowania dla 4, 8, 12 i 16 procesów oraz 2, 3, 5 i 10 workerów
uruchamia skrypt z katalogu głównego:

```powershell
python benchmark_scaling.py
```

Wyniki trafiają do `results/scaling/`. Skrypt automatycznie pomija kompletne,
poprawne CSV zgodne z aktualnym zestawem grafów. Istniejące wyniki bazowe dla
16 procesów i 3 workerów są używane ponownie. Wymuszenie ponownego wykonania:

```powershell
python benchmark_scaling.py --force
```

Samodzielna konfiguracja `docker-compose.scaling.yml` zawiera maksymalnie
10 nazwanych workerów i jest używana automatycznie przez skrypt.

## Struktura plików

```
distributed/
├── docker-compose.yml          # Orkiestracja kontenerów
├── README.md                   # Ten plik
├── coordinator/
│   ├── Dockerfile              # Obraz koordynatora
│   ├── coordinator.py          # Główna logika (scatter/gather/verify)
│   ├── graph_loader.py         # Ładowanie grafów i expected
│   └── component_detector.py   # Detekcja składowych + scheduling
├── worker/
│   ├── Dockerfile              # Obraz workera
│   └── worker.py               # BFS worker (TCP server)
└── shared/
    ├── __init__.py
    └── protocol.py             # Protokół TCP (send_msg/recv_msg)
```

## Protokół komunikacji

Format wiadomości: `<4B długość big-endian><pickle payload>`

| Kierunek | Typ        | Payload                                           |
|----------|------------|---------------------------------------------------|
| C → W    | `task`     | `{"subgraph": {...}, "start": int}`               |
| W → C    | `result`   | `{"start": int, "dist": {node: dist}}`            |
| C → W    | `shutdown` | `{}`                                              |

## Weryfikacja

Coordinator automatycznie:
1. Wykonuje sekwencyjny BFS (baseline) dla każdego grafu
2. Wykonuje rozproszony BFS (3 workery)
3. Porównuje wynik z oczekiwanym (`*_expected.txt`)
4. Powtarza oba algorytmy domyślnie 3 razy dla każdego grafu
5. Drukuje tabelę ze średnimi czasami, odchyleniem, speedupem i weryfikacją
6. Eksportuje wszystkie próby i statystyki do `results/distributed_bfs_results.csv`
7. W wariancie profilującym zapisuje profile każdego węzła do
   `results/profiles/`

Liczbę powtórzeń można zmienić przez zmienną `BENCHMARK_RUNS` w
`docker-compose.yml`.

### Zakres pomiaru czasu

- Czas sekwencyjny obejmuje samo przejście BFS po już wczytanym grafie.
- Czas rozproszony obejmuje detekcję składowych, przygotowanie podgrafów,
  harmonogram zadań, komunikację TCP oraz BFS wykonywany przez workery.
- CSV zawiera również osobne czasy detekcji, przygotowania podgrafów,
  harmonogramowania oraz wykonania i komunikacji dla każdej próby, a także
  średnią, medianę, minimum, maksimum i odchylenie standardowe.
- Połączenie z workerami, start kontenerów, wczytanie grafu i wczytanie pliku
  `*_expected.txt` nie są wliczane do żadnego z porównywanych czasów.
- Obecny podział pracy odbywa się po składowych. Dla grafu spójnego pracuje
  tylko jeden worker, więc narzut komunikacji zwykle dominuje nad zyskiem.
