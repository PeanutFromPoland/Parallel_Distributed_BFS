import random
import math

from .random import generate_random_graph
from .bb import generate_bb_graph
from .small_world import generate_small_world_graph
from .grid import generate_grid_graph

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

    remaining = total - min_per_part * parts_count
    if remaining == 0:
        return [min_per_part] * parts_count
    if parts_count == 1:
        return [total]

    # Losowy słaby podział remaining metodą stars-and-bars. Koszt zależy od
    # liczby części, a nie od liczby wszystkich wierzchołków.
    sequence_length = remaining + parts_count - 1
    separators = sorted(rng.sample(range(sequence_length), parts_count - 1))
    extras = [separators[0]]
    extras.extend(
        separators[i] - separators[i - 1] - 1
        for i in range(1, len(separators))
    )
    extras.append(sequence_length - separators[-1] - 1)
    return [min_per_part + extra for extra in extras]


def _factor_pair_near_square(size):
    width = int(math.sqrt(size))
    while width > 1 and size % width != 0:
        width -= 1
    return width, size // width


def _density_degree(density):
    return max(1, round(density * 8))


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


def _generate_subgraph(gen_type, size, start_val, rng, density):
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
            threshold=density,
            consistency=True,
            start_val=start_val,
            unidirectional=True,
            seed=seed,
        )
    elif gen_type == "bb":
        m = min(_density_degree(density), size - 1)
        random.seed(seed)
        graph = gen_func(
            size=size,
            m=m,
            start_val=start_val,
            unidirectional=True,
        )
    elif gen_type == "small_world":
        if size == 2:
            graph = {
                start_val: [start_val + 1],
                start_val + 1: [start_val],
            }
        else:
            k = min(2 * _density_degree(density), size - 1)
            if k % 2 != 0:
                k -= 1
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
        w, h = _factor_pair_near_square(size)
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
    density=0.3,
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
        Cyklicznie powtarzana lista typów generatorów dla kolejnych podgrafów.
        Dozwolone wartości: 'random', 'bb', 'small_world', 'grid'.
    seed : int
        Ziarno losowości dla powtarzalności wyników.
    density : float
        Profil gęstości stosowany do komponentów innych niż grid.

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
    if not part_types:
        raise ValueError("'part_types' nie może być puste.")
    if not 0 < density <= 1:
        raise ValueError("'density' musi należeć do przedziału (0, 1].")

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
            gen_type=part_types[i % len(part_types)],
            size=sizes[i],
            start_val=current_start,
            rng=rng,
            density=density,
        )
        combined_graph.update(subgraph)
        current_start += len(subgraph)

    return combined_graph


if __name__ == "__main__":
    from utils import draw_graph

    graph = generate_inconsistent_graph(
        total_vertices=30,
        parts_count=3,
        part_types=["random", "bb", "small_world"],
        seed=42,
    )
    print(f"Wierzchołki: {len(graph)}")
    print(f"Krawędzie: {sum(len(v) for v in graph.values()) // 2}")
    draw_graph(graph)
