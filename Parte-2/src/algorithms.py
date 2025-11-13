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

