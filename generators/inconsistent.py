import random
import math

from .random import generate_random_graph
from .bb import generate_bb_graph
from .small_world import generate_small_world_graph
from .grid import generate_grid_graph
from utils import draw_graph

# Mapowanie nazw typów → funkcji generatorów
GENERATOR_MAP = {
    "random": generate_random_graph,
    "bb": generate_bb_graph,
    "small_world": generate_small_world_graph,
    "grid": generate_grid_graph,
}


def _partition_vertices(total, parts_count, rng):
    """
    Rozdziela 'total' wierzchołków na 'parts_count' podgrafów.

    Każdy podgraf dostaje co najmniej 2 wierzchołki (minimum dla sensownego
    grafu). Pozostałe wierzchołki są losowo przydzielane do podgrafów.

    Zwraca listę rozmiarów, np. [15, 23, 12].
    """
    min_per_part = 2
    if total < min_per_part * parts_count:
        raise ValueError(
            f"Zbyt mało wierzchołków ({total}) dla {parts_count} spójnych "
            f"podgrafów (minimum {min_per_part} wierzchołki na podgraf)."
        )

    sizes = [min_per_part] * parts_count
    remaining = total - min_per_part * parts_count

    # Losowy przydział pozostałych wierzchołków
    for _ in range(remaining):
        idx = rng.randint(0, parts_count - 1)
        sizes[idx] += 1

    return sizes


def _remap_graph(graph, offset):
    """
    Przenumerowuje wierzchołki grafu, dodając 'offset' do każdego klucza i
    wartości. Obsługuje zarówno klucze int, jak i tuple (dla grafów grid).

    Zwraca nowy słownik sąsiedztwa z przenumerowanymi wierzchołkami.
    """
    remapped = {}

    # Ustal mapowanie starych kluczy → nowe klucze
    old_keys = sorted(graph.keys())
    mapping = {}
    for i, key in enumerate(old_keys):
        mapping[key] = offset + i

    for old_key, neighbors in graph.items():
        new_key = mapping[old_key]
        remapped[new_key] = [mapping[n] for n in neighbors]

    return remapped


def _generate_subgraph(gen_type, size, start_val, rng):
    """
    Generuje pojedynczy podgraf spójny za pomocą wybranego generatora.

    Parametry
    ---------
    gen_type : str
        Typ generatora: 'random', 'bb', 'small_world', 'grid'.
    size : int
        Liczba wierzchołków.
    start_val : int
        Numer pierwszego wierzchołka.
    rng : random.Random
        Instancja generatora losowego.

    Zwraca
    ------
    dict[int, list[int]]
        Słownik sąsiedztwa z wierzchołkami numerowanymi od start_val.
    """
    gen_func = GENERATOR_MAP.get(gen_type)
    if gen_func is None:
        raise ValueError(
            f"Nieznany typ generatora: '{gen_type}'. "
            f"Dostępne: {list(GENERATOR_MAP.keys())}"
        )

    seed = rng.randint(0, 2 ** 31)

    if gen_type == "random":
        graph = gen_func(
            size=size,
            threshold=0.3,
            consistency=True,
            start_val=start_val,
            unidirectional=True,
            seed=seed,
        )
    elif gen_type == "bb":
        m = min(2, size - 1)
        random.seed(seed)
        graph = gen_func(
            size=size,
            m=m,
            start_val=start_val,
            unidirectional=True,
        )
    elif gen_type == "small_world":
        k = min(4, size - 1)
        if k % 2 != 0:
            k = max(2, k - 1)
        graph = gen_func(
            size=size,
            k=k,
            rewiring_prob=0.1,
            consistency=True,
            start_val=start_val,
            unidirectional=True,
            seed=seed,
        )
    elif gen_type == "grid":
        # Dobieramy wymiary siatki tak, aby iloczyn ≈ size
        # Tworzymy siatkę 2D o wymiarach w × h ≈ size
        w = max(1, int(math.sqrt(size)))
        h = max(1, size // w)
        # Ewentualna korekta – upewniamy się, że w * h == size
        # Jeśli nie, zwiększamy h
        while w * h < size:
            h += 1

        graph = gen_func(
            dimensions=(w, h),
        )
        # Grid generuje klucze jako tuple – przenumerowujemy na int
        graph = _remap_graph(graph, start_val)

    return graph


def generate_inconsistent_graph(
    total_vertices,
    parts_count,
    part_types,
    seed=42,
):
    """
    Generuje graf niespójny składający się z kilku podgrafów spójnych.

    Parametry
    ---------
    total_vertices : int
        Łączna liczba wierzchołków w wynikowym grafie.
    parts_count : int
        Liczba podgrafów spójnych (komponentów spójności).
    part_types : list[str]
        Lista typów generatorów dla kolejnych podgrafów.
        Dozwolone wartości: 'random', 'bb', 'small_world', 'grid'.
        Długość listy musi być równa parts_count.
    seed : int
        Ziarno losowości dla powtarzalności wyników.

    Zwraca
    ------
    dict[int, list[int]]
        Słownik sąsiedztwa wynikowego grafu niespójnego.
        Wierzchołki numerowane od 1.

    Przykład
    --------
    >>> g = generate_inconsistent_graph(
    ...     total_vertices=30,
    ...     parts_count=3,
    ...     part_types=["random", "bb", "small_world"],
    ...     seed=123,
    ... )
    >>> len(g)
    30
    """
    if len(part_types) != parts_count:
        raise ValueError(
            f"Długość 'part_types' ({len(part_types)}) musi być równa "
            f"'parts_count' ({parts_count})."
        )

    for pt in part_types:
        if pt not in GENERATOR_MAP:
            raise ValueError(
                f"Nieznany typ generatora: '{pt}'. "
                f"Dostępne: {list(GENERATOR_MAP.keys())}"
            )

    rng = random.Random(seed)

    # Rozdziel wierzchołki na podgrafy
    sizes = _partition_vertices(total_vertices, parts_count, rng)

    # Generuj podgrafy i łącz je w jeden graf niespójny
    combined_graph = {}
    current_start = 1  # Numeracja wierzchołków zaczyna się od 1

    for i in range(parts_count):
        subgraph = _generate_subgraph(
            gen_type=part_types[i],
            size=sizes[i],
            start_val=current_start,
            rng=rng,
        )
        combined_graph.update(subgraph)
        # Używamy len(subgraph), bo grid może wygenerować nieco więcej
        # wierzchołków niż zaalokowano (w*h ≥ size)
        current_start += len(subgraph)

    return combined_graph


if __name__ == "__main__":
    graph = generate_inconsistent_graph(
        total_vertices=30,
        parts_count=3,
        part_types=["random", "bb", "small_world"],
        seed=42,
    )
    print(f"Wierzchołki: {len(graph)}")
    print(f"Krawędzie: {sum(len(v) for v in graph.values()) // 2}")
    draw_graph(graph)