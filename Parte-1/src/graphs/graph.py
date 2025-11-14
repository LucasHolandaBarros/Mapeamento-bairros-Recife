import json
from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple, Optional

class Graph:
   
    def __init__(self):
        # Lista de adjacência: defaultdict(dict)
        self.adj: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        # Atributos dos nós: dict
        self.nodes: Dict[str, Dict[str, Any]] = {}

    def add_node(self, node: str, **attrs):
        """Adiciona um nó ao grafo com atributos (ex: microrregiao)."""
        if node not in self.adj:
            self.adj[node] = {}
        self.nodes[node] = attrs

    def add_edge(self, u: str, v: str, weight: float = 1.0, **attrs):
        """
        Adiciona uma aresta não-direcionada entre u e v.
        Armazena o peso e outros atributos da aresta.
        """
        # Garante que os nós existam na lista de adjacência
        if u not in self.adj: self.add_node(u)
        if v not in self.adj: self.add_node(v)
            
        # Adiciona a aresta em ambas as direções
        attrs['weight'] = weight
        self.adj[u][v] = attrs
        self.adj[v][u] = attrs

    def get_nodes(self) -> List[str]:
        """Retorna uma lista de todos os nós (bairros)."""
        return list(self.nodes.keys())

    def get_node_attributes(self, node: str) -> Dict[str, Any]:
        """Retorna os atributos de um nó específico."""
        return self.nodes.get(node, {})

    def get_neighbors(self, node: str) -> List[str]:
        """Retorna os vizinhos de um nó."""
        if node not in self.adj:
            return []
        return list(self.adj[node].keys())

    def get_degree(self, node: str) -> int:
        """Retorna o grau de um nó (número de vizinhos)."""
        return len(self.get_neighbors(node))

    # --- Métodos para a Parte 3 (Métricas) ---

    def get_order(self) -> int:
        """Retorna a Ordem do grafo (|V|)."""
        return len(self.nodes)

    def get_size(self) -> int:
        """
        Retorna o Tamanho do grafo (|E|).
        Soma os graus de todos os nós e divide por 2.
        """
        total_degree = sum(len(neighbors) for neighbors in self.adj.values())
        return total_degree // 2

    def get_density(self) -> float:
        """Retorna a Densidade do grafo."""
        V = self.get_order()
        if V < 2:
            return 0.0
        
        E = self.get_size()
        return (2 * E) / (V * (V - 1))
    
    # COLOQUE ESTE MÉTODO DENTRO DA SUA CLASSE GRAPH
    
    def get_edge_data(self, u: str, v: str) -> Dict[str, Any]:
        """
        Retorna os atributos de uma aresta específica de u para v.
        """
        # Acessa o dicionário de adjacência para u, 
        # e então pega os dados da aresta para v.
        # Retorna {} se u ou v não existirem.
        return self.adj.get(u, {}).get(v, {})

    # --- Métodos para Subgrafos (Parte 3) ---

    def get_induced_subgraph(self, nodes_to_keep: List[str]) -> 'Graph':
        """
        Cria um subgrafo induzido contendo apenas os nós da lista
        'nodes_to_keep' e as arestas *entre* eles.
        """
        subgraph = Graph()
        nodes_set = set(nodes_to_keep)
        
        # 1. Adiciona os nós e seus atributos ao subgrafo
        for node_name in nodes_to_keep:
            if node_name in self.nodes:
                attrs = self.get_node_attributes(node_name)
                subgraph.add_node(node_name, **attrs)
        
        # 2. Adiciona as arestas *apenas* se ambos os nós estiverem no set
        for u in subgraph.get_nodes():
            # Itera sobre os vizinhos no grafo *original*
            for v, attrs in self.adj[u].items():
                if v in nodes_set:
                    # Adiciona a aresta (o método add_edge cuida da duplicata)
                    # Adicionamos apenas se u < v para evitar processamento duplicado
                    if u < v:
                        subgraph.add_edge(u, v, **attrs)
                        
        return subgraph

    def get_ego_network(self, node: str) -> 'Graph':
        """
        Retorna o subgrafo "ego-network" de um nó:
        o nó (ego) + seus vizinhos diretos (alters) +
        as arestas entre todos eles.
        """
        if node not in self.adj:
            # Retorna um grafo vazio se o nó não existir
            return Graph()
            
        neighbors = self.get_neighbors(node)
        ego_nodes = [node] + neighbors
        
        # O subgrafo induzido com esses nós é a ego-network
        return self.get_induced_subgraph(ego_nodes)