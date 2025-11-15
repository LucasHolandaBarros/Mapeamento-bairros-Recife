from graph import Graph

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
