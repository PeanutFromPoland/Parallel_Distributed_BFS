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
docker compose logs -f coordinator

# 4. Zatrzymaj
docker compose down
```

## Konfiguracja

### Zmienne środowiskowe (coordinator)

| Zmienna     | Domyślna wartość                              | Opis                                |
|-------------|-----------------------------------------------|-------------------------------------|
| `WORKERS`   | `worker-1:5000,worker-2:5000,worker-3:5000`   | Lista adresów workerów (host:port)  |
| `GRAPHS_DIR`| `/app/graphs`                                 | Ścieżka do katalogu z grafami       |

### Zmienne środowiskowe (worker)

| Zmienna       | Domyślna wartość | Opis              |
|---------------|------------------|--------------------|
| `WORKER_PORT` | `5000`           | Port nasłuchiwania |

### Skalowanie workerów

Aby zmienić liczbę workerów, edytuj `docker-compose.yml` i zmienną `WORKERS`
w sekcji coordinator.

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
4. Drukuje tabelę z czasami, speedupem i wynikami weryfikacji

### Zakres pomiaru czasu

- Czas sekwencyjny obejmuje samo przejście BFS po już wczytanym grafie.
- Czas rozproszony obejmuje detekcję składowych, przygotowanie podgrafów,
  harmonogram zadań, komunikację TCP oraz BFS wykonywany przez workery.
- Połączenie z workerami, start kontenerów, wczytanie grafu i wczytanie pliku
  `*_expected.txt` nie są wliczane do żadnego z porównywanych czasów.
- Obecny podział pracy odbywa się po składowych. Dla grafu spójnego pracuje
  tylko jeden worker, więc narzut komunikacji zwykle dominuje nad zyskiem.
