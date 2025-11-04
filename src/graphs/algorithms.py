import heapq
from collections import deque
from typing import List, Tuple, Dict, Any
from .graph import Graph # Importa nossa classe Graph

def dijkstra(graph: Graph, start_node: str, end_node: str) -> Tuple[float, List[str]]:
    """
    Executa o algoritmo de Dijkstra para encontrar o caminho mais curto
    entre 'start_node' e 'end_node' usando os 'weight' das arestas.
    
    Retorna:
        - O custo total (float('inf') se não houver caminho).
        - O caminho (lista de nós, vazia se não houver caminho).
    """
    if start_node not in graph.nodes or end_node not in graph.nodes:
        return float('inf'), []

    # Distâncias: {nó: custo_do_start_ate_ele}
    distances: Dict[str, float] = {node: float('inf') for node in graph.get_nodes()}
    # Nó anterior no caminho mais curto: {nó: nó_anterior}
    previous_nodes: Dict[str, str | None] = {node: None for node in graph.get_nodes()}
    
    # Fila de prioridade: (custo, nó)
    pq: List[Tuple[float, str]] = [(0, start_node)]
    distances[start_node] = 0
    
    while pq:
        current_cost, current_node = heapq.heappop(pq)
        
        # Otimização: se o custo na fila é maior do que o já conhecido, ignora
        if current_cost > distances[current_node]:
            continue
            
        # Otimização: se chegamos ao destino, podemos parar
        if current_node == end_node:
            break
            
        # Itera sobre os vizinhos do nó atual
        for neighbor, edge_attrs in graph.adj[current_node].items():
            weight = edge_attrs.get('weight', 1.0) # Usa o peso da aresta
            new_cost = current_cost + weight
            
            # Se um caminho mais barato for encontrado
            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (new_cost, neighbor))
                
    # --- Reconstrução do caminho ---
    
    # Se a distância até o final ainda é infinita, não há caminho
    final_cost = distances[end_node]
    if final_cost == float('inf'):
        return float('inf'), []
        
    path: List[str] = []
    current: str | None = end_node
    
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
        
    path.reverse() # O caminho é construído do fim para o começo
    
    return final_cost, path