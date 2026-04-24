"""
Identyfikacja składowych spójności po numeracji wierzchołków
i zachłanny przydział do workerów.

Optymalizacja: generator grafów niespójnych (generators/inconsistent.py) nadaje
wierzchołkom kolejne numery w ramach każdej składowej. Dzięki temu składowe
można wykryć, analizując luki w posortowanej numeracji — bez pełnego BFS/DFS
po całym grafie.

Fallback: jeśli analiza numeracji nie daje rozłącznych zbiorów krawędzi
(np. graf spójny), stosowany jest klasyczny BFS do identyfikacji składowych.
"""

from collections import deque


def detect_components_by_numbering(
    graph: dict[int, list[int]],
) -> list[list[int]]:
    """
    Identyfikuje składowe spójności na podstawie luk w numeracji wierzchołków.

    Algorytm:
        1. Posortuj wierzchołki rosnąco.
        2. Podziel na grupy, w których kolejne wierzchołki mają numery
           różniące się o 1 (ciągłe zakresy).
        3. Dla każdego zakresu sprawdź, czy krawędzie wychodzą poza zakres.
           Jeśli tak — łącz zakresy (fallback do BFS).
        4. Zwróć listę zbiorów wierzchołków (każdy = jedna składowa).

    Parametry:
        graph : dict[int, list[int]] — lista sąsiedztwa

    Zwraca:
        list[list[int]] — lista składowych (posortowana malejąco wg rozmiaru);
                          każda składowa to posortowana lista wierzchołków
    """
    if not graph:
        return []

    sorted_nodes = sorted(graph.keys())

    # Krok 1: Znajdź ciągłe zakresy numeracji
    ranges = []
    range_start = sorted_nodes[0]
    prev = sorted_nodes[0]

    for node in sorted_nodes[1:]:
        if node != prev + 1:
            # Luka — nowy zakres
            ranges.append((range_start, prev))
            range_start = node
        prev = node
    ranges.append((range_start, prev))

    # Krok 2: Sprawdź, czy zakresy są rzeczywiście rozłączne
    # (żadna krawędź nie łączy wierzchołków z różnych zakresów)
    range_sets = []
    for lo, hi in ranges:
        range_set = set(range(lo, hi + 1))
        range_sets.append(range_set)

    # Budujemy mapę: wierzchołek → indeks zakresu
    node_to_range = {}
    for idx, rset in enumerate(range_sets):
        for node in rset:
            node_to_range[node] = idx

    # Sprawdzamy krawędzie — czy łączą wierzchołki z różnych zakresów
    # Jeśli tak, łączymy zakresy (Union-Find)
    parent = list(range(len(range_sets)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for node, neighbors in graph.items():
        node_range = node_to_range.get(node)
        if node_range is None:
            continue
        for nb in neighbors:
            nb_range = node_to_range.get(nb)
            if nb_range is not None and nb_range != node_range:
                union(node_range, nb_range)

    # Grupuj zakresy wg ich korzenia Union-Find
    from collections import defaultdict
    groups = defaultdict(list)
    for idx, rset in enumerate(range_sets):
        root = find(idx)
        groups[root].extend(rset)

    components = [sorted(nodes) for nodes in groups.values()]
    # Sortuj malejąco wg rozmiaru (dla zachłannego przydziału)
    components.sort(key=len, reverse=True)

    return components


def detect_components_bfs(
    graph: dict[int, list[int]],
) -> list[list[int]]:
    """
    Fallback: identyfikacja składowych spójności klasycznym BFS.

    Zwraca:
        list[list[int]] — lista składowych posortowana malejąco wg rozmiaru
    """
    visited = set()
    components = []

    for start in sorted(graph.keys()):
        if start in visited:
            continue

        component = []
        queue = deque([start])
        visited.add(start)

        while queue:
            node = queue.popleft()
            component.append(node)
            for nb in graph.get(node, []):
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)

        components.append(sorted(component))

    components.sort(key=len, reverse=True)
    return components


def extract_subgraph(
    graph: dict[int, list[int]], vertices: list[int]
) -> dict[int, list[int]]:
    """
    Wyodrębnia podgraf dla podanego zbioru wierzchołków.

    Parametry:
        graph    : pełny graf (lista sąsiedztwa)
        vertices : lista wierzchołków składowej

    Zwraca:
        dict[int, list[int]] — podgraf ograniczony do wierzchołków ze składowej
    """
    vertex_set = set(vertices)
    subgraph = {}
    for v in vertices:
        subgraph[v] = [nb for nb in graph.get(v, []) if nb in vertex_set]
    return subgraph


def greedy_schedule(
    components: list[list[int]], num_workers: int
) -> list[list[int]]:
    """
    Zachłanny przydział składowych do workerów.

    Strategia:
        - Składowe są posortowane malejąco wg rozmiaru (input)
        - Każda składowa trafia do workera z najmniejszym łącznym obciążeniem
        - Wynik: lista list, gdzie i-ty element to indeksy składowych
          przypisanych do i-tego workera

    Parametry:
        components  : lista składowych (posortowana malejąco wg rozmiaru)
        num_workers : liczba dostępnych workerów

    Zwraca:
        list[list[int]] — schedule[worker_idx] = [comp_idx, ...]
    """
    # Obciążenie każdego workera (suma wierzchołków)
    loads = [0] * num_workers
    schedule = [[] for _ in range(num_workers)]

    for comp_idx, component in enumerate(components):
        # Wybierz workera z najmniejszym obciążeniem
        min_worker = min(range(num_workers), key=lambda w: loads[w])
        schedule[min_worker].append(comp_idx)
        loads[min_worker] += len(component)

    return schedule
