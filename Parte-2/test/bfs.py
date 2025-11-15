# algorithms.py

def bfs(self, fonte):
    visitado = {}
    camada = {}
    ordem = []
    fila = []
    ciclos = False

    # Inicializa a única fonte
    visitado[fonte] = True
    camada[fonte] = 0
    fila.append(fonte)

    # BFS
    while fila:
        u = fila.pop(0)
        ordem.append(u)

        for viz in self.adj.get(u, []):
            if viz not in visitado:
                visitado[viz] = True
                camada[viz] = camada[u] + 1
                fila.append(viz)
            else:
                if viz not in fila and camada[viz] <= camada[u]:
                    ciclos = True

    # resumo
    countOrdem = len(ordem)
    countCamadas = max(camada.values()) + 1 if camada else 0

    return {
        "ordem": countOrdem,
        "camadas": countCamadas,
        "ha_ciclos": ciclos,
    }



""" Veremos depois
# OPCIONAL: versão que retorna também o predecessor (árvore BFS)
def bfs_tree(graph, start_node):
    
    BFS que retorna:
    - ordem de visita
    - predecessor de cada nó (árvore BFS)
    

    if start_node not in graph.nodes:
        return [], {}

    visited = []
    queue = [start_node]
    parent = {start_node: None}

    while queue:
        current = queue.pop(0)
        visited.append(current)

        for nb in graph.get_neighbors(current):
            if nb not in parent:  # equivalente a "não visitado"
                parent[nb] = current
                queue.append(nb)

    return visited, parent

"""