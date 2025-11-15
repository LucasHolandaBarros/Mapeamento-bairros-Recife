from typing import Dict, List, Tuple, Optional
from graph import Graph
from solve import load_graph_from_csv

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

            if peso_aresta < 0:
                raise ValueError(f"Peso negativo detectado na aresta: {no_atual} -> {vizinho}")

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
        
    return caminho[::-1], custo_final


if __name__ == "__main__":
    graph = load_graph_from_csv( "Parte-2/dados/BrFlights2_filtrado.csv")

    print(dijkstra(graph, "Porto Alegre", "Toronto"))
    print(dijkstra(graph, "Recife", "Buenos Aires"))
    print(dijkstra(graph, "Dallas/Fort Worth", "Sao Paulo"))