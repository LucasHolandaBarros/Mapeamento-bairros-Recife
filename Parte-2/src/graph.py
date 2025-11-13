import json
from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple, Optional

class Graph:
    
    def __init__(self):
        """
        Inicializa um grafo dirigido.
        self.adj armazena {origem: {destino: {atributos da aresta}}}
        """
        self.adj: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        self.nodes: Dict[str, Dict[str, Any]] = {}

    def add_node(self, node: str, **attrs):
        """Adiciona um nó ao grafo com atributos (ex: cidade)."""
        if node not in self.adj:
            self.adj[node] = {}
        self.nodes[node] = attrs

    def add_directed_edge(self, u: str, v: str, weight: float = 1.0, **attrs):
        """
        Adiciona uma aresta DIRIGIDA de 'u' para 'v'.
        Armazena o peso e outros atributos da aresta.
        """
        if u not in self.adj: self.add_node(u)
        if v not in self.adj: self.add_node(v)
            
        attrs['weight'] = weight
        self.adj[u][v] = attrs

    def get_nodes(self) -> List[str]:
        """Retorna uma lista de todos os nós (cidades)."""
        return list(self.nodes.keys())

    def get_node_attributes(self, node: str) -> Dict[str, Any]:
        """Retorna os atributos de um nó específico."""
        return self.nodes.get(node, {})

    def get_neighbors(self, node: str) -> List[str]:
        """Retorna os vizinhos de SAÍDA de um nó (destinos diretos)."""
        if node not in self.adj:
            return []
        return list(self.adj[node].keys())
        
    def get_edge_data(self, u: str, v: str) -> Dict[str, Any]:
        """Retorna os atributos de uma aresta específica (u -> v)."""
        return self.adj.get(u, {}).get(v, {})

    def get_out_degree(self, node: str) -> int:
        """Retorna o grau de SAÍDA de um nó (número de voos saindo)."""
        return len(self.get_neighbors(node))

    def get_order(self) -> int:
        """Retorna a Ordem do grafo (|V| - número de cidades)."""
        return len(self.nodes)

    def get_size(self) -> int:
        """
        Retorna o Tamanho do grafo (|E| - número de voos).
        Soma o grau de saída de todos os nós.
        """
        total_degree = sum(len(neighbors) for neighbors in self.adj.values())
        return total_degree
    
    # COLOQUE ESTE MÉTODO DENTRO DA SUA CLASSE GRAPH
    
    def get_induced_subgraph(self, nodes_to_keep: List[str]) -> 'Graph':
        """
        Cria um subgrafo induzido contendo apenas os nós da lista
        'nodes_to_keep' e as arestas *entre* eles.
        """
        subgraph = Graph() # Cria uma nova instância de Graph
        nodes_set = set(nodes_to_keep)
        
        # 1. Adiciona os nós e seus atributos ao subgrafo
        for node_name in nodes_to_keep:
            if node_name in self.nodes:
                attrs = self.get_node_attributes(node_name)
                subgraph.add_node(node_name, **attrs)
        
        # 2. Adiciona as arestas *apenas* se ambos os nós estiverem no set
        
        # Itera sobre os nós que acabamos de adicionar ao subgrafo
        for u in subgraph.get_nodes():
            # Itera sobre os vizinhos no grafo *original*
            if u not in self.adj: continue # Segurança, caso o nó não esteja no adj original
            
            for v, attrs in self.adj[u].items():
                # Adiciona a aresta *apenas* se o destino (v) também estiver no set
                if v in nodes_set:
                    # Precisamos passar os atributos e o peso separados
                    # Criamos uma cópia para não modificar o original
                    edge_attrs = attrs.copy()
                    weight = edge_attrs.pop('weight', 1.0) # Remove o peso e o usa
                    
                    # Adiciona a aresta dirigida ao subgrafo
                    subgraph.add_directed_edge(u, v, weight=weight, **edge_attrs)
                        
        return subgraph
    
    def get_ego_network(self, node: str) -> 'Graph':
        """
        Retorna o subgrafo "ego-network" de um nó:
        o nó (ego) + seus vizinhos diretos (alters) +
        as arestas entre todos eles.
        
        NOTA: Para grafos dirigidos, "vizinhos" pode significar 
        vizinhos de saída, entrada ou ambos. Esta implementação 
        usa vizinhos de SAÍDA.
        """
        if node not in self.adj:
            return Graph()
            
        neighbors = self.get_neighbors(node)
        ego_nodes = [node] + neighbors
        
        # O subgrafo induzido com esses nós é a ego-network
        return self.get_induced_subgraph(ego_nodes)