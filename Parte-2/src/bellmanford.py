from graph import Graph

def bellman_ford(self, fonte):
   
    dist = {n: float('inf') for n in self.nodes}
    pred = {n: None for n in self.nodes}
    dist[fonte] = 0

    V = len(self.nodes)

    for i in range(V - 1):
        for u in self.adj:
            for v, attrs in self.adj[u].items():
                peso = attrs.get('weight', 1)
                if dist[u] + peso < dist[v]:
                    dist[v] = dist[u] + peso
                    pred[v] = u

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
