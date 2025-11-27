from collections import defaultdict
from typing import Any, Dict, List

class Graph:
   
    def __init__(self):
        self.adj: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)

        self.nodes: Dict[str, Dict[str, Any]] = {}

    def add_node(self, node: str, **attrs):

        if node not in self.adj:
            self.adj[node] = {}
        self.nodes[node] = attrs

    def add_edge(self, u: str, v: str, weight: float = 1.0, **attrs):
        if u not in self.adj: self.add_node(u)
        if v not in self.adj: self.add_node(v)
            
        attrs['weight'] = weight
        self.adj[u][v] = attrs
        self.adj[v][u] = attrs

    def get_nodes(self) -> List[str]:
        return list(self.nodes.keys())

    def get_node_attributes(self, node: str) -> Dict[str, Any]:
        return self.nodes.get(node, {})

    def get_neighbors(self, node: str) -> List[str]:
        if node not in self.adj:
            return []
        return list(self.adj[node].keys())

    def get_degree(self, node: str) -> int:
        return len(self.get_neighbors(node))

    def get_order(self) -> int:
        return len(self.nodes)

    def get_size(self) -> int:
        total_degree = sum(len(neighbors) for neighbors in self.adj.values())
        return total_degree // 2

    def get_density(self) -> float:
        V = self.get_order()
        if V < 2:
            return 0.0
        
        E = self.get_size()
        return (2 * E) / (V * (V - 1))
    
    def get_edge_data(self, u: str, v: str) -> Dict[str, Any]:
        return self.adj.get(u, {}).get(v, {})

    def get_induced_subgraph(self, nodes_to_keep: List[str]) -> 'Graph':
        subgraph = Graph()
        nodes_set = set(nodes_to_keep)
        
        for node_name in nodes_to_keep:
            if node_name in self.nodes:
                attrs = self.get_node_attributes(node_name)
                subgraph.add_node(node_name, **attrs)
        
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