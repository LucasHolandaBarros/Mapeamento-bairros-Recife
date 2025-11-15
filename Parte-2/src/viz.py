# Adicione esta função ao seu script principal
from pyvis.network import Network
from .graph import Graph


def visualize_ego_network(full_graph: Graph, ego_node: str, filename="ego_network.html"):
    """
    Cria uma visualização da rede ego de um nó usando pyvis.
    """
    if ego_node not in full_graph.nodes:
        print(f"Erro: Nó '{ego_node}' não encontrado no grafo.")
        return

    # 1. Pega o subgrafo induzido (ego + vizinhos + arestas entre eles)
    # Supondo que você tenha um método get_ego_network na sua classe Graph
    try:
        ego_subgraph = full_graph.get_ego_network(ego_node)
        print(f"Criando ego-network para '{ego_node}' com {ego_subgraph.get_order()} nós e {ego_subgraph.get_size()} arestas.")
    except AttributeError:
        print("Erro: Método 'get_ego_network' não encontrado na sua classe Graph.")
        print("Por favor, adicione o método 'get_ego_network' (do nosso chat anterior) à sua classe.")
        return

    # 2. Configura o Pyvis
    net = Network(height="800px", width="100%", heading=f"Rede Ego de {ego_node}", directed=True)
    
    # 3. Adiciona os nós ao Pyvis
    for node in ego_subgraph.get_nodes():
        if node == ego_node:
            # Destaca o nó "ego"
            net.add_node(node, label=node, color="#FF0000", size=30)
        else:
            # Nós "alter" (vizinhos)
            net.add_node(node, label=node, size=15)
            
    # 4. Adiciona as arestas ao Pyvis
    for u in ego_subgraph.get_nodes():
        for v in ego_subgraph.get_neighbors(u):
            edge_data = ego_subgraph.get_edge_data(u, v)
            weight = edge_data.get('weight', 1.0)
            
            # O 'value' controla a espessura da aresta (inverso da duração)
            # O 'title' é o que aparece ao passar o mouse
            net.add_edge(
                u, 
                v, 
                value=1.0 / weight, # Arestas mais curtas podem ser mais grossas
                title=f"Duração: {weight:.2f}h"
            )
            
    # 5. Gera o HTML
    net.show_buttons(filter_=['physics']) # Adiciona botões para "brincar" com a física
    net.save_graph(filename)
    print(f"Visualização da Rede Ego salva em: {filename}")