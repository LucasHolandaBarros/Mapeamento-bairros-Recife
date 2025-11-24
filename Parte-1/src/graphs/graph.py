from collections import defaultdict
from typing import Any, Dict, List

class Graph:
   
    def __init__(self):
        # Lista de adjacência
        self.adj: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        # Atributos dos nós
        self.nodes: Dict[str, Dict[str, Any]] = {}

    # Aciona um nó no grafo com seus atributos
    def add_node(self, node: str, **attrs):

        if node not in self.adj:
            self.adj[node] = {}
        self.nodes[node] = attrs

    def add_edge(self, u: str, v: str, weight: float = 1.0, **attrs):
        # Garante que os nós existam na lista de adjacência
        if u not in self.adj: self.add_node(u)
        if v not in self.adj: self.add_node(v)
            
        # Adiciona a aresta em ambas as direções
        attrs['weight'] = weight
        self.adj[u][v] = attrs
        self.adj[v][u] = attrs

    # Retornado lsista de todos oas nós
    def get_nodes(self) -> List[str]:
        return list(self.nodes.keys())

    # Retorna os atributos de um nó
    def get_node_attributes(self, node: str) -> Dict[str, Any]:
        return self.nodes.get(node, {})

    # Retorna a lista de vizinhos de um nó
    def get_neighbors(self, node: str) -> List[str]:
        if node not in self.adj:
            return []
        return list(self.adj[node].keys())

    # Retorna o grau de um nó
    def get_degree(self, node: str) -> int:
        return len(self.get_neighbors(node))

    # Retorna a Ordem do grafo (numero de nós)
    def get_order(self) -> int:
        return len(self.nodes)

    # Retorna o Tamanho do grafo (numero de arestas)
    def get_size(self) -> int:
        total_degree = sum(len(neighbors) for neighbors in self.adj.values())
        return total_degree // 2

    # Retorna a Densidade do grafo
    def get_density(self) -> float:
        V = self.get_order()
        if V < 2:
            return 0.0
        
        E = self.get_size()
        return (2 * E) / (V * (V - 1))
    
    # Retorna os atributos de uma aresta 
    def get_edge_data(self, u: str, v: str) -> Dict[str, Any]:
        return self.adj.get(u, {}).get(v, {})

    # Cria um subgrafo induzido (microrregiões)
    def get_induced_subgraph(self, nodes_to_keep: List[str]) -> 'Graph':
        subgraph = Graph()
        nodes_set = set(nodes_to_keep)
        
        # Adiciona os nós e seus atributos ao subgrafo
        for node_name in nodes_to_keep:
            if node_name in self.nodes:
                attrs = self.get_node_attributes(node_name)
                subgraph.add_node(node_name, **attrs)
        
        # Adiciona as arestas *apenas* se ambos os nós estiverem no set
        for u in subgraph.get_nodes():
            for v, attrs in self.adj[u].items():
                if v in nodes_set:
                    if u < v:
                        subgraph.add_edge(u, v, **attrs)
                        
        return subgraph

    def get_ego_network(self, node: str) -> 'Graph':
        if node not in self.adj:
            return Graph()
            
        neighbors = self.get_neighbors(node)
        ego_nodes = [node] + neighbors
        
        return self.get_induced_subgraph(ego_nodes)