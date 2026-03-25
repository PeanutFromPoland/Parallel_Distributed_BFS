import matplotlib.pyplot as plt
import networkx as nx


def draw_graph(graph: dict):
    G = nx.Graph()
    for node, neighbors in graph.items():
        G.add_node(node)
        for neighbor in neighbors:
            if neighbor in graph:
                G.add_edge(node, neighbor)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 8))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color="#4fc3f7",
        edge_color="#90a4ae",
        node_size=500,
        font_size=8,
        font_weight="bold",
    )
    plt.title("Graf – układ domyślny")
    plt.tight_layout()
    plt.show()


def draw_grid_graph(graph: dict):
    G = nx.Graph()
    for node, neighbors in graph.items():
        G.add_node(node)
        for neighbor in neighbors:
            if neighbor in graph:
                G.add_edge(node, neighbor)

    # Pozycje wprost z krotek (x, y)
    pos = {node: node for node in G.nodes()}

    plt.figure(figsize=(8, 8))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color="#81c784",
        edge_color="#90a4ae",
        node_size=500,
        font_size=7,
        font_weight="bold",
    )
    plt.title("Graf – siatka (grid)")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()
