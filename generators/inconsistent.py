import random

from . import *

def generate_inconsistent_graph(start_val, parts_count=1, seed=42, graph_size_range=(10, 100)):
    functions = [generate_grid_graph, generate_random_graph, generate_ba_graph, generate_bb_graph]
    random.seed(seed)
    random.shuffle(functions)

    graph = {}
    for i in range(parts_count):
        size = random.randint(graph_size_range[0], graph_size_range[1])
        random.choice(functions)(size, )