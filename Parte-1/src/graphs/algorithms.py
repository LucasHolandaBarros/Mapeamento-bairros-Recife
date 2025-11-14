from collections import deque
from typing import List, Tuple, Dict, Optional
from .graph import Graph # Importa nossa classe Graph

def _encontrar_proximo_no_minimo(distancias: Dict[str, float], visitados: set[str]) -> Optional[str]:
    """
    Função auxiliar LENTA (O(V)) para encontrar o próximo nó.
    Itera por TODOS os nós para achar o não visitado com menor distância.
    """
    dist_minima = float('inf')
    no_minimo = None
    
    for no, dist in distancias.items():
        if dist < dist_minima and no not in visitados:
            dist_minima = dist
            no_minimo = no
            
    return no_minimo

def dijkstra(graph: Graph, start_node: str, end_node: str) -> Tuple[Optional[List[str]], float]:
    """
    Encontra o caminho mais curto usando a implementação "ingênua" de Dijkstra.
    Esta versão é O(V^2) e MUITO mais lenta que a versão com heapq.
    
    Retorna: (caminho, custo_total) ou (None, float('inf')) se não houver caminho.
    """
    if start_node not in graph.nodes or end_node not in graph.nodes:
        return None, float('inf')

    # 1. Inicialização
    distancias: Dict[str, float] = {node: float('inf') for node in graph.get_nodes()}
    predecessores: Dict[str, Optional[str]] = {node: None for node in graph.get_nodes()}
    visitados: set[str] = set() # Nós que já processamos
    
    distancias[start_node] = 0
    
    # 2. Loop principal
    # Em vez de 'while pq:', loopamos até visitar todos os nós
    num_nos = graph.get_order()
    for _ in range(num_nos):
        
        # ----- ESTA É A DIFERENÇA (O(V)) -----
        # Encontra o nó não visitado com menor distância
        no_atual = _encontrar_proximo_no_minimo(distancias, visitados)
        # ------------------------------------
        
        # Se não há mais nós alcançáveis, pare
        if no_atual is None or distancias[no_atual] == float('inf'):
            break
            
        # Otimização: Se chegamos ao destino, podemos parar.
        if no_atual == end_node:
            break
            
        visitados.add(no_atual)
        
        # 3. "Relaxamento" (igual à outra versão)
        for vizinho in graph.get_neighbors(no_atual):
            # Não precisamos re-processar nós já finalizados
            if vizinho in visitados:
                continue

            edge_data = graph.get_edge_data(no_atual, vizinho)
            if 'weight' not in edge_data:
                continue
                
            peso_aresta = edge_data['weight']
            novo_custo = distancias[no_atual] + peso_aresta
            
            if novo_custo < distancias[vizinho]:
                distancias[vizinho] = novo_custo
                predecessores[vizinho] = no_atual
                
    # --- 4. Reconstrução do Caminho (igual à outra versão) ---
    custo_final = distancias[end_node]
    if custo_final == float('inf'):
        return None, custo_final
        
    caminho: List[str] = []
    no = end_node
    while no is not None:
        caminho.append(no)
        no = predecessores[no]
        
    return custo_final, caminho[::-1]
