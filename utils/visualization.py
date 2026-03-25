import matplotlib.pyplot as plt
import networkx as nx

def is_unidirectional(graph: dict):
    pass

def draw_graph(graph: dict, title="Graf"):
    G = nx.DiGraph()
    for node, neighbors in graph.items():
        G.add_node(node)
        for neighbor in neighbors:
            if neighbor in graph:
                G.add_edge(node, neighbor)

    edge_set = set(G.edges())
    bidirectional = []
    unidirectional = []
    seen_pairs = set()
    for u, v in edge_set:
        pair = (min(u, v), max(u, v))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        if (v, u) in edge_set:
            bidirectional.append((u, v))
        else:
            unidirectional.append((u, v))

    for u, v in list(edge_set):
        pair = (min(u, v), max(u, v))
        if pair not in {(min(a, b), max(a, b)) for a, b in bidirectional + unidirectional}:
            unidirectional.append((u, v))

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 8))

    nx.draw_networkx_nodes(
        G, pos,
        node_color="#4fc3f7",
        node_size=500,
    )
    nx.draw_networkx_labels(
        G, pos,
        font_size=8,
        font_weight="bold",
    )

    if unidirectional:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=unidirectional,
            edge_color="#90a4ae",
            arrows=True,
            arrowstyle="-|>",
            arrowsize=15,
            connectionstyle="arc3,rad=0.0",
        )

    if bidirectional:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=bidirectional,
            edge_color="#90a4ae",
            arrows=True,
            arrowstyle="-",
            arrowsize=15,
            connectionstyle="arc3,rad=0.1",
        )

    plt.title(title)
    plt.tight_layout()
    plt.show()


def draw_grid_graph(graph: dict, title="Graf – siatka (grid)"):
    G = nx.Graph()
    for node, neighbors in graph.items():
        G.add_node(node)
        for neighbor in neighbors:
            if neighbor in graph:
                G.add_edge(node, neighbor)

    pos = {node: node for node in G.nodes()}

    plt.figure(figsize=(12, 12))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color="#81c784",
        edge_color="#90a4ae",
        node_size=500,
        font_size=7,
        font_weight="bold",
    )
    plt.title(title)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()
