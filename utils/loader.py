def export_to_txt(graph, name = "graph"):
    count_of_nodes = len(graph)
    count_of_edges = sum(len(l) for l in graph.values())
    with open(f"{name}.txt", 'w', encoding='utf-8') as file:
        file.write(str(count_of_nodes) + ' ' + str(count_of_edges) + '\n')
        for node in graph:
            for neighbor in graph[node]:
                if len(node) > 1:
                    file.write(str("".join(str(node[i]) + ' ' for i in range(len(node)))) + ' ' + str("".join(str(neighbor[i]) + ' ' for i in range(len(neighbor)))) + '\n')
                else:
                    file.write(str(node) + ' ' + str(neighbor) + '\n')

def import_from_txt(name):
    if not name.endswith('.txt'):
        name += '.txt'

    with open(name, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            nums = line.split(' ')
            p0, p1 = nums[0:len(nums)//2 - 1], nums[len(nums)//2: -1]
            p0, p1 = tuple(int(i) for i in p0), tuple(int(i) for i in p1)
            print(p0, p1)
