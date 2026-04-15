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
    # Utrzymujemy listę wag przyrostowo zamiast przeliczać od nowa
    # w każdej iteracji.  Używamy random.choices (implementacja w C)
    # zamiast ręcznej pętli kumulacyjnej.
    existing_nodes = list(initial_nodes)
    weights = [fitness[n] * max(len(graph[n]), 1) for n in existing_nodes]
    node_to_idx = {n: i for i, n in enumerate(existing_nodes)}

    for new_node in nodes[m + 1:]:
        # Wybierz m celów bez powtórzeń (ważone losowanie)
        # Dla m=2: losujemy jednego, zerujemy mu wagę, losujemy drugiego
        targets = set()
        zeroed_indices = []

        for _ in range(min(m, len(existing_nodes))):
            if not existing_nodes:
                break
            [chosen] = random.choices(existing_nodes, weights=weights, k=1)
            if chosen in targets:
                # Powtórka – spróbuj jeszcze raz (max kilka prób)
                for _retry in range(10):
                    [chosen] = random.choices(existing_nodes, weights=weights, k=1)
                    if chosen not in targets:
                        break
            targets.add(chosen)
            # Tymczasowo zerujemy wagę, żeby nie wylosować ponownie
            idx = node_to_idx[chosen]
            zeroed_indices.append((idx, weights[idx]))
            weights[idx] = 0.0

        # Przywróć wyzerowane wagi i zaktualizuj stopnie
        for idx, old_w in zeroed_indices:
            weights[idx] = old_w

        # Dodaj krawędzie
        for target in targets:
            graph[new_node].append(target)
            if unidirectional:
                graph[target].append(new_node)
            # Aktualizuj wagę target (stopień wzrósł o 1)
            tidx = node_to_idx[target]
            weights[tidx] = fitness[target] * len(graph[target])

        # Dodaj nowy wierzchołek do listy istniejących
        node_to_idx[new_node] = len(existing_nodes)
        existing_nodes.append(new_node)
        weights.append(fitness[new_node] * max(len(graph[new_node]), 1))

    return graph

draw_graph(generate_bb_graph(10, m=3, fitness_range=(0.2, 0.6), unidirectional=True))