from typing import List, Tuple, Dict, Optional
from .graph import Graph 

# Função auxiliar para encontrar o nó com menor distância
def _encontrar_proximo_no_minimo(distancias: Dict[str, float], visitados: set[str]) -> Optional[str]:
    dist_minima = float('inf')
    no_minimo = None
    
    for no, dist in distancias.items():
        if dist < dist_minima and no not in visitados:
            dist_minima = dist
            no_minimo = no
            
    return no_minimo

# Função principal de Dijkstra
def dijkstra(graph: Graph, start_node: str, end_node: str) -> Tuple[Optional[List[str]], float]:

    if start_node not in graph.nodes or end_node not in graph.nodes:
        return None, float('inf')

    #  Inicialização
    distancias: Dict[str, float] = {node: float('inf') for node in graph.get_nodes()}
    predecessores: Dict[str, Optional[str]] = {node: None for node in graph.get_nodes()}
    visitados: set[str] = set() 
    
    distancias[start_node] = 0
    
    # Loop principal
    num_nos = graph.get_order()
    for _ in range(num_nos):
        
        # Encontra o nó não visitado com menor distância
        no_atual = _encontrar_proximo_no_minimo(distancias, visitados)
        
        # Se não há mais nós alcançáveis, pare
        if no_atual is None or distancias[no_atual] == float('inf'):
            break
            
        # Se chegamos ao destino, podemos parar.
        if no_atual == end_node:
            break
            
        visitados.add(no_atual)
        
        for vizinho in graph.get_neighbors(no_atual):
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
           
    # Reconstrução do Caminho
    custo_final = distancias[end_node]
    if custo_final == float('inf'):
        return float('inf'), []
        
    caminho: List[str] = []
    no = end_node
    while no is not None:
        caminho.append(no)
        no = predecessores[no]
        
    return custo_final, caminho[::-1]
