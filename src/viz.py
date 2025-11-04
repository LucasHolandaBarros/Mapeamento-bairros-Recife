from pyvis.network import Network
from typing import List
from pathlib import Path
import sys

# --- Imports RELATIVAS (CORRIGIDO) ---
from .graphs.graph import Graph  # <-- MUDANÇA AQUI

# --- Definições de Caminho ---
SRC_DIR = Path(__file__).resolve().parent 
BASE_DIR = SRC_DIR.parent 

def visualize_path(
    graph: Graph, 
    path: List[str], 
    output_filename: Path
):
    """
    Gera uma visualização HTML interativa (usando pyvis) do *grafo completo*,
    destacando um caminho (path) específico.
    (O corpo desta função está 100% correto)
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
    
    # 2. Mapeia nós e arestas do caminho
    path_nodes = set(path)
    path_edges = set()
    for i in range(len(path) - 1):
        u, v = sorted((path[i], path[i+1]))
        path_edges.add((u, v))

    # --- Cores e Tamanhos ---
    highlight_color = "#FF0000" # Vermelho
    default_color = "#97C2FC"   # Azul
    default_edge_color = "#E0E0E0" # Cinza
    
    # 3. Adiciona TODOS os nós
    for node in graph.get_nodes():
        if node in path_nodes:
            net.add_node(node, label=node, color=highlight_color, size=25, font_size=15)
        else:
            net.add_node(node, label=node, color=default_color, size=15)

    # 4. Adiciona TODAS as arestas
    added_edges = set()
    for u in graph.get_nodes():
        for v, attrs in graph.adj[u].items():
            u_sorted, v_sorted = sorted((u, v))
            if (u_sorted, v_sorted) in added_edges:
                continue
            
            added_edges.add((u_sorted, v_sorted))
            weight = attrs.get('weight', 1.0)
            
            if (u_sorted, v_sorted) in path_edges:
                net.add_edge(u, v, label=str(weight), color=highlight_color, width=4, font_size=12)
            else:
                net.add_edge(u, v, label=str(weight), color=default_edge_color, width=1, font_size=8)

    # 5. Configura a física
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": { "springLength": 100 },
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


# --- Bloco de Teste Executável ---
# Este código só roda quando você executa: python -m src.viz
if __name__ == "__main__":
    
    print("🚀  Rodando [viz.py] em modo de teste...")
    
    # 1. Importa as funções necessárias (só aqui)
    try:
        # --- MUDANÇA AQUI (adicionando '.graphs') ---
        from .graphs.io import load_graph_from_csvs
        from .graphs.algorithms import dijkstra
    except ImportError as e:
        print(f"🚨  [viz.py] Erro ao importar módulos: {e}", file=sys.stderr)
        print("   Certifique-se de rodar da RAIZ do projeto (pasta 'projeto-grafos/')", file=sys.stderr)
        print("   Use o comando correto: python -m src.viz", file=sys.stderr)
        sys.exit(1)

    # 2. Define o diretório de saída
    OUTPUT_DIR = BASE_DIR / "out" 
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 3. Carrega o grafo
    try:
        graph = load_graph_from_csvs()
    except SystemExit:
        print("❌  [viz.py] Falha ao carregar o grafo. Abortando.", file=sys.stderr)
        sys.exit(1)
        
    if graph.get_order() == 0:
        print("⚠️  [viz.py] O grafo está vazio. Verifique seus CSVs.", file=sys.stderr)
        sys.exit(1)

    # 4. Define o caminho que queremos testar
    start_raw = "Nova Descoberta"
    end_raw = "Setúbal"
    
    start_node = start_raw
    end_node = end_raw
    
    if end_node == "Setúbal":
        end_node = "Boa Viagem"
        
    print(f"🗺️   [viz.py] Calculando Dijkstra: {start_node} -> {end_node}")
    
    # 5. Roda o Dijkstra
    cost, path = dijkstra(graph, start_node, end_node)
    
    if not path:
        print(f"🚨  [viz.py] Nenhum caminho encontrado entre {start_node} e {end_node}.", file=sys.stderr)
        sys.exit(1)

    # 6. Define o nome do arquivo de saída
    output_file_test = OUTPUT_DIR / "arvore_percurso_TESTE.html"
    
    # 7. Chama a função de visualização
    visualize_path(graph, path, output_file_test)
    
    print(f"\n🎉  [viz.py] Teste concluído. Abra {output_file_test} no seu navegador.")