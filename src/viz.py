# src/viz.py

from pyvis.network import Network
from typing import List
from pathlib import Path
import sys

# Importa a classe Graph usando o mesmo estilo do seu 'solve.py'
from graphs.graph import Graph

def visualize_path(
    graph: Graph, 
    path: List[str], 
    output_filename: Path
):
    """
    Gera uma visualização HTML interativa (usando pyvis) do *grafo completo*,
    destacando um caminho (path) específico.
    """
    if not path:
        print("⚠️  [viz.py] Caminho vazio, não é possível gerar visualização.", file=sys.stderr)
        return

    print(f"🎨  [viz.py] Gerando visualização para o caminho: {' -> '.join(path)}")
    
    # 1. Configura a rede pyvis
    net = Network(
        height="800px", 
        width="100%", 
        notebook=False, 
        heading=f"Percurso: {path[0]} para {path[-1]}", # Título
        directed=False,
        bgcolor="#222222",
        font_color="white"
    )
    
    # 2. Mapeia nós e arestas do caminho para consulta rápida
    path_nodes = set(path)
    path_edges = set()
    for i in range(len(path) - 1):
        # Armazena a aresta (u, v) em ordem alfabética
        u, v = sorted((path[i], path[i+1]))
        path_edges.add((u, v))

    # --- Cores e Tamanhos ---
    highlight_color = "#FF0000" # Vermelho para o caminho
    default_color = "#97C2FC"   # Azul claro para outros nós
    default_edge_color = "#444444" # Cinza escuro para outras arestas
    
    # 3. Adiciona TODOS os nós do grafo
    for node in graph.get_nodes():
        if node in path_nodes:
            # Nó NO CAMINHO: Vermelho e grande
            net.add_node(node, label=node, color=highlight_color, size=25, font_size=15)
        else:
            # Nó COMUM: Azul e pequeno
            net.add_node(node, label=node, color=default_color, size=15, font_size=10)

    # 4. Adiciona TODAS as arestas do grafo
    added_edges = set() # Controle para não adicionar arestas duplicadas
    
    for u in graph.get_nodes():
        for v, attrs in graph.adj[u].items():
            # Garante ordem alfabética para checagem
            u_sorted, v_sorted = sorted((u, v))
            if (u_sorted, v_sorted) in added_edges:
                continue # Já adicionamos essa aresta (ex: B->A depois de A->B)
            
            added_edges.add((u_sorted, v_sorted))
            weight = attrs.get('weight', 1.0)
            
            if (u_sorted, v_sorted) in path_edges:
                # Aresta NO CAMINHO: Vermelha e espessa
                net.add_edge(u, v, label=str(weight), color=highlight_color, 
                             width=4, font_size=10)
            else:
                # Aresta COMUM: Cinza e fina
                net.add_edge(u, v, color=default_edge_color, width=1)

    # 5. Configura a "física" da simulação para melhor layout
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
          "springLength": 100
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      }
    }
    """)
    
    # 6. Salva o arquivo HTML
    try:
        net.save_graph(str(output_filename))
        print(f"✅  [viz.py] Visualização interativa salva em: {output_filename}")
    except Exception as e:
        print(f"🚨  [viz.py] Erro ao salvar visualização: {e}", file=sys.stderr)