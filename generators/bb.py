import random

from utils import draw_graph


def generate_bb_graph(size, m=2, fitness_range=(0.1, 1.0), start_val=1, unidirectional=True):
    """
    Generuje graf według modelu Bianconi-Barabási.

    Model rozszerza klasyczny model Barabási-Alberta o parametr „fitness"
    (atrakcyjności) każdego wierzchołka. Prawdopodobieństwo podłączenia
    nowego wierzchołka do istniejącego zależy od iloczynu stopnia
    wierzchołka i jego fitness:  P(i) ∝ η_i · k_i

    Parametry
    ---------
    size : int
        Liczba wierzchołków w wynikowym grafie.
    m : int
        Liczba krawędzi dodawanych z każdym nowym wierzchołkiem.
        Musi spełniać 1 <= m < size.
    fitness_range : tuple[float, float]
        Zakres (min, max) z którego losowana jest wartość fitness
        każdego wierzchołka (rozkład jednostajny).
    start_val : int
        Wartość pierwszego wierzchołka (numeracja od start_val).
    unidirectional : bool
        Jeśli True, krawędzie są dwukierunkowe (graf nieskierowany).

    Zwraca
    ------
    dict[int, list[int]]
        Słownik sąsiedztwa (adjacency list).
    """
    if size < 1:
        raise ValueError("'size' musi być >= 1.")
    if m < 1:
        raise ValueError("'m' musi być >= 1.")
    if m >= size:
        raise ValueError("'m' musi być mniejsze niż 'size'.")

    nodes = list(range(start_val, start_val + size))
    graph = {node: [] for node in nodes}
    fitness = {node: random.uniform(*fitness_range) for node in nodes}

    # --- Inicjalizacja: pełna klika z pierwszych (m+1) wierzchołków ---
    initial_nodes = nodes[:m + 1]
    for i, u in enumerate(initial_nodes):
        for v in initial_nodes[i + 1:]:
            graph[u].append(v)
            if unidirectional:
                graph[v].append(u)

    # --- Dodawanie kolejnych wierzchołków ---
    for new_node in nodes[m + 1:]:
        existing_nodes = [n for n in nodes if n < new_node or n in initial_nodes]
        existing_nodes = [n for n in existing_nodes if n != new_node]

        # Oblicz wagi: fitness * stopień (min. stopień = 1, żeby nowe węzły
        # w klice miały szansę)
        weights = []
        for n in existing_nodes:
            degree = max(len(graph[n]), 1)
            weights.append(fitness[n] * degree)

        # Wybierz m celów bez powtórzeń (ważone losowanie)
        targets = set()
        pool = list(zip(existing_nodes, weights))
        while len(targets) < m and pool:
            total = sum(w for _, w in pool)
            r = random.uniform(0, total)
            cumulative = 0.0
            for idx, (node, w) in enumerate(pool):
                cumulative += w
                if cumulative >= r:
                    targets.add(node)
                    pool.pop(idx)
                    break

        # Dodaj krawędzie
        for target in targets:
            graph[new_node].append(target)
            if unidirectional:
                graph[target].append(new_node)

    return graph

draw_graph(generate_bb_graph(10, m=3, fitness_range=(0.2, 0.6), unidirectional=True))