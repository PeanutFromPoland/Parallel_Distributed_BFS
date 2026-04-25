from collections import deque


def detect_components_by_numbering(graph):
    if not graph:
        return []

    sorted_nodes = sorted(graph.keys())

    ranges = []
    range_start = sorted_nodes[0]
    prev = sorted_nodes[0]

    for node in sorted_nodes[1:]:
        if node != prev + 1:
            ranges.append((range_start, prev))
            range_start = node
        prev = node
    ranges.append((range_start, prev))

    range_sets = []
    for lo, hi in ranges:
        range_set = set(range(lo, hi + 1))
        range_sets.append(range_set)

    node_to_range = {}
    for idx, rset in enumerate(range_sets):
        for node in rset:
            node_to_range[node] = idx

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

    from collections import defaultdict
    groups = defaultdict(list)
    for idx, rset in enumerate(range_sets):
        root = find(idx)
        groups[root].extend(rset)

    components = [sorted(nodes) for nodes in groups.values()]
    components.sort(key=len, reverse=True)

    return components


def detect_components_bfs(graph):
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


def extract_subgraph(graph, vertices):
    if len(vertices) == len(graph):
        return graph

    vertex_set = set(vertices)
    return {
        v: [nb for nb in graph.get(v, []) if nb in vertex_set]
        for v in vertices
    }


def greedy_schedule(components, num_workers, weights=None):
    if weights is None:
        weights = [len(component) for component in components]

    loads = [0] * num_workers
    schedule = [[] for _ in range(num_workers)]

    component_order = sorted(range(len(components)), key=lambda i: weights[i], reverse=True)
    for comp_idx in component_order:
        min_worker = min(range(num_workers), key=lambda w: loads[w])
        schedule[min_worker].append(comp_idx)
        loads[min_worker] += weights[comp_idx]

    return schedule
