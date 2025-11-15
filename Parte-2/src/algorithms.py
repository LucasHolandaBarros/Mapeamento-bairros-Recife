import heapq
from typing import Dict, List, Tuple, Optional

# Importa a classe Graph do outro arquivo
from graph import Graph

def dijkstra(graph: Graph, start_node: str, end_node: str) -> Tuple[Optional[List[str]], float]:
    
    if start_node not in graph.nodes or end_node not in graph.nodes:
        return None, float('inf')

    # {nó: (custo, predecessor)}
    distancias: Dict[str, float] = {node: float('inf') for node in graph.get_nodes()}
    predecessores: Dict[str, Optional[str]] = {node: None for node in graph.get_nodes()}
    
    # Fila de prioridade (min-heap): armazena (custo_acumulado, nó_atual)
    pq: List[Tuple[float, str]] = [(0, start_node)]
    
    distancias[start_node] = 0
    
    while pq:
        custo_atual, no_atual = heapq.heappop(pq)
        
        if custo_atual > distancias[no_atual]:
            continue
            
        if no_atual == end_node:
            break
            
        for vizinho in graph.get_neighbors(no_atual):
            edge_data = graph.get_edge_data(no_atual, vizinho)
            
            if 'weight' not in edge_data:
                continue
                
            peso_aresta = edge_data['weight']
            novo_custo = custo_atual + peso_aresta
            
            if novo_custo < distancias[vizinho]:
                distancias[vizinho] = novo_custo
                predecessores[vizinho] = no_atual
                heapq.heappush(pq, (novo_custo, vizinho))
                
    # --- Reconstrução do Caminho ---
    custo_final = distancias[end_node]
    if custo_final == float('inf'):
        return None, custo_final
        
    caminho: List[str] = []
    no = end_node
    while no is not None:
        caminho.append(no)
        no = predecessores[no]
        
    return caminho[::-1], custo_final


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


def dfs(self, fonte):
    visitado = {}
    camada = {}
    ordem = []
    ciclos = False

    def dfs_visit(u, profundidade):
        nonlocal ciclos
        visitado[u] = True
        camada[u] = profundidade
        ordem.append(u)

        for viz in self.adj.get(u, []):
            if viz not in visitado:
                dfs_visit(viz, profundidade + 1)
            else:
                # ciclo se voltamos para um nó já visitado
                if camada[viz] <= profundidade:
                    ciclos = True

    # inicia DFS
    dfs_visit(fonte, 0)

    # resumo
    qtd_nos = len(ordem)
    qtd_camadas = max(camada.values()) + 1 if camada else 0

    return {
        "ordem": qtd_nos,
        "camadas": qtd_camadas,
        "ha_ciclos": ciclos
    }


def bellman_ford(self, fonte):
    """
    Bellman-Ford para grafos dirigidos com pesos (podem ser negativos).
    Retorna:
        - dist: distância mínima da fonte para cada nó
        - pred: predecessor de cada nó no caminho mínimo
        - ha_ciclo_negativo: True se existir ciclo negativo
    """
    # inicialização
    dist = {n: float('inf') for n in self.nodes}
    pred = {n: None for n in self.nodes}
    dist[fonte] = 0

    # número de nós
    V = len(self.nodes)

    # relaxamento de todas as arestas |V|-1 vezes
    for i in range(V - 1):
        for u in self.adj:
            for v, attrs in self.adj[u].items():
                peso = attrs.get('weight', 1)
                if dist[u] + peso < dist[v]:
                    dist[v] = dist[u] + peso
                    pred[v] = u

    # checagem de ciclos negativos
    ha_ciclo_negativo = False
    for u in self.adj:
        for v, attrs in self.adj[u].items():
            peso = attrs.get('weight', 1)
            if dist[u] + peso < dist[v]:
                ha_ciclo_negativo = True
                break
        if ha_ciclo_negativo:
            break

    return {
        "distancias": dist,
        "predecessores": pred,
        "ha_ciclo_negativo": ha_ciclo_negativo
    }