from typing import Dict, List, Tuple, Optional
from .graph import Graph
import time
import tracemalloc  

def _encontrar_proximo_no_minimo(distancias: Dict[str, float], visitados: set[str]) -> Optional[str]:
   
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

    distancias: Dict[str, float] = {node: float('inf') for node in graph.get_nodes()}
    predecessores: Dict[str, Optional[str]] = {node: None for node in graph.get_nodes()}
    visitados: set[str] = set()
    
    distancias[start_node] = 0
    

    num_nos = graph.get_order()
    for _ in range(num_nos):
        
        
        no_atual = _encontrar_proximo_no_minimo(distancias, visitados)
       
        if no_atual is None or distancias[no_atual] == float('inf'):
            break
            
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

            if peso_aresta < 0:
                raise ValueError(f"Peso negativo detectado na aresta: {no_atual} -> {vizinho}")

            novo_custo = distancias[no_atual] + peso_aresta
            
            if novo_custo < distancias[vizinho]:
                distancias[vizinho] = novo_custo
                predecessores[vizinho] = no_atual
                
    
    custo_final = distancias[end_node]
    if custo_final == float('inf'):
        return None, custo_final
        
    caminho: List[str] = []
    no = end_node
    while no is not None:
        caminho.append(no)
        no = predecessores[no]
        
    return caminho[::-1], custo_final


def bfs(graph, fonte):
    visitado = {}
    camada = {}
    ordem = []
    ciclos = False

    fila = [fonte]
    inicio = 0
    visitado[fonte] = True
    camada[fonte] = 0

    while inicio < len(fila):
        u = fila[inicio]
        inicio += 1
        ordem.append(u)

        for viz in graph.get_neighbors(u):
            if viz not in visitado:
                visitado[viz] = True
                camada[viz] = camada[u] + 1
                fila.append(viz)
            else:
                if viz not in fila[inicio:] and camada[viz] <= camada[u]:
                    ciclos = True

    return {
        "ordem": len(ordem),
        "camadas": max(camada.values()) + 1 if camada else 0,
        "ha_ciclos": ciclos
    }


def dfs(graph, fonte):
    visitado = {}
    camada = {}
    ordem = []
    ciclos = False

    pilha = [(fonte, 0)]
    while pilha:
        u, profundidade = pilha.pop()
        if u not in visitado:
            visitado[u] = True
            camada[u] = profundidade
            ordem.append(u)

            vizinhos = graph.get_neighbors(u)
            for viz in reversed(vizinhos):
                pilha.append((viz, profundidade + 1))
        else:
            if camada[u] <= profundidade:
                ciclos = True

    return {
        "ordem": len(ordem),
        "camadas": max(camada.values()) + 1 if camada else 0,
        "ha_ciclos": ciclos
    }


def bellman_ford(graph, fonte):
    dist = {n: float('inf') for n in graph.get_nodes()}
    pred = {n: None for n in graph.get_nodes()}
    dist[fonte] = 0

    V = len(graph.get_nodes())
    for _ in range(V - 1):
        for u in graph.get_nodes():
            for v in graph.get_neighbors(u):
                peso = graph.get_edge_data(u, v).get('weight', 1)
                if dist[u] + peso < dist[v]:
                    dist[v] = dist[u] + peso
                    pred[v] = u

    ha_ciclo_negativo = False
    for u in graph.get_nodes():
        for v in graph.get_neighbors(u):
            peso = graph.get_edge_data(u, v).get('weight', 1)
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


def medir_desempenho(func, *args, medir_memoria=False, **kwargs):
   
    resultado = {}
    if medir_memoria:   
        tracemalloc.start()
    
    start_time = time.perf_counter()
    retorno = func(*args, **kwargs)
    end_time = time.perf_counter()
    
    resultado['tempo'] = end_time - start_time
    
    if medir_memoria:
        mem_atual, mem_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        resultado['memoria_MB'] = mem_pico / (1024 * 1024)
    
    return retorno, resultado

