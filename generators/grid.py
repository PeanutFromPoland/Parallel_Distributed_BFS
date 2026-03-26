from itertools import product

from utils import draw_grid_graph


def generate_grid_graph(dimensions, start_val=None, end_val=None):
    """
    Generuje graf typu siatka (grid) w n wymiarach.

    Każdy wierzchołek to n-krotka współrzędnych. Krawędzie łączą wierzchołki
    sąsiadujące wzdłuż dokładnie jednego wymiaru (odległość Manhattańska == 1).

    Parametry
    ---------
    dimensions : int | tuple[int, ...] | list[int]
        - int  → traktowane jako rozmiar siatki w każdym wymiarze,
                  wymaga podania start_val (określającego liczbę wymiarów).
        - tuple/list → rozmiar siatki w każdym wymiarze, np. (4, 5, 3)
                       oznacza siatkę 4×5×3.
    start_val : tuple[int, ...] | list[int] | None
        Punkt początkowy zakresu w każdym wymiarze (inclusive).
        Domyślnie (0, 0, ..., 0).
    end_val : tuple[int, ...] | list[int] | None
        Punkt końcowy zakresu w każdym wymiarze (exclusive).
        Jeśli podano `dimensions` jako tuplę/listę, to `end_val` jest
        wyliczane automatycznie jako start_val[i] + dimensions[i].
    """

    # --- Normalizacja parametrów ---
    if isinstance(dimensions, int):
        if start_val is None:
            raise ValueError(
                "Gdy 'dimensions' jest liczbą całkowitą, 'start_val' musi być "
                "podane (jako tupla/lista), aby określić liczbę wymiarów."
            )
        ndim = len(start_val)
        dims = tuple([dimensions] * ndim)
    elif isinstance(dimensions, (tuple, list)):
        dims = tuple(dimensions)
        ndim = len(dims)
    else:
        raise TypeError(
            f"'dimensions' musi być int, tuple lub list, otrzymano {type(dimensions).__name__}"
        )

    if any(d <= 0 for d in dims):
        raise ValueError("Wszystkie wymiary muszą być większe od 0.")

    if start_val is None:
        start_val = tuple([0] * ndim)
    else:
        start_val = tuple(start_val)

    if len(start_val) != ndim:
        raise ValueError(
            f"Długość 'start_val' ({len(start_val)}) musi odpowiadać "
            f"liczbie wymiarów ({ndim})."
        )

    if end_val is not None:
        end_val = tuple(end_val)
        if len(end_val) != ndim:
            raise ValueError(
                f"Długość 'end_val' ({len(end_val)}) musi odpowiadać "
                f"liczbie wymiarów ({ndim})."
            )
    else:
        end_val = tuple(s + d for s, d in zip(start_val, dims))

    # --- Generowanie zakresów współrzędnych w każdym wymiarze ---
    ranges = [range(s, e) for s, e in zip(start_val, end_val)]

    # --- Generowanie wierzchołków (kartezjanowy iloczyn zakresów) ---
    vertices = list(product(*ranges))

    vertex_set = set(vertices)

    # --- Budowanie grafu ---
    graph = {}
    for v in vertices:
        neighbors = []
        for dim in range(ndim):
            for delta in (-1, +1):
                neighbor = list(v)
                neighbor[dim] += delta
                neighbor = tuple(neighbor)
                if neighbor in vertex_set:
                    neighbors.append(neighbor)
        graph[v] = neighbors

    return graph
