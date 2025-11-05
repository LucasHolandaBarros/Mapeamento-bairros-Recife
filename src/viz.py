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
    
# Parte 8:

# Heatmap por bairro
def visualize_degree_heatmap(graph: Graph, output_filename: Path):
    """
    Mostra os bairros coloridos por intensidade de grau (número de conexões) com legenda integrada
    e correspondência exata das cores dos vértices.
    """
    from matplotlib import cm, colors
    from pyvis.network import Network
    import numpy as np

    print("🎨  Gerando mapa de cores por grau...")

    net = Network(
        height="800px",
        width="100%",
        bgcolor="#222",
        font_color="white",
        notebook=False
    )

    # Ajuste da física para aproximar os nós
    net.force_atlas_2based(
        gravity=-50, central_gravity=0.01, spring_length=50, spring_strength=0.05, damping=0.4
    )

    # Calcula grau e cores
    graus = {n: graph.get_degree(n) for n in graph.get_nodes()}
    max_grau = max(graus.values()) if graus else 1

    norm = colors.Normalize(vmin=0, vmax=max_grau)
    cmap = cm.ScalarMappable(norm=norm, cmap='plasma')

    for node, grau in graus.items():
        color = colors.to_hex(cmap.to_rgba(grau))
        net.add_node(node, label=f"{node} ({grau})", color=color, size=10 + grau * 2)

    for u in graph.get_nodes():
        for v in graph.adj[u]:
            net.add_edge(u, v, color="#555", width=1)

    # Salva o grafo temporariamente
    net.save_graph(str(output_filename))

    # --- Cria legenda com cores exatas ---
    with open(output_filename, "r", encoding="utf-8") as f:
        html = f.read()

    # Define ticks no gradiente (0%, 25%, 50%, 75%, 100%)
    ticks = np.linspace(0, max_grau, 5)
    tick_colors = [colors.to_hex(cmap.to_rgba(g)) for g in ticks]
    tick_positions = ["0%", "25%", "50%", "75%", "100%"]

    # Cria CSS para o gradiente usando cores dos ticks
    gradient_stops = ", ".join([f"{c} {p}" for c, p in zip(tick_colors, tick_positions)])

    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 20px;
        left: 50px;
        width: 300px;
        height: 20px;
        background: linear-gradient(to right, {gradient_stops});
        border: 1px solid white;
        z-index: 9999;
    "></div>
    <div style="
        position: fixed;
        bottom: 5px;
        left: 50px;
        width: 300px;
        display: flex;
        justify-content: space-between;
        color: white;
        font-size: 12px;
        z-index: 9999;
    ">
        {int(ticks[0])}<span>{int(ticks[1])}</span><span>{int(ticks[2])}</span><span>{int(ticks[3])}</span>{int(ticks[4])}
    </div>
    """

    # Insere antes do </body>
    html = html.replace("</body>", legend_html + "</body>")

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Mapa de calor de graus salvo com legenda ajustada: {output_filename}")

# Ranking de densidade ego-subrede por microrregiao
def plot_density_ranking(output_filename: Path, ego_csv_file: Path, bairros_csv_file: Path = None):
    import matplotlib
    matplotlib.use("Agg")
    import pandas as pd
    import matplotlib.pyplot as plt
    from pathlib import Path

    if not ego_csv_file.exists():
        print(f"⚠️ Arquivo '{ego_csv_file}' não encontrado.")
        return

    df_ego = pd.read_csv(ego_csv_file)

    # Se for fornecido, carrega os microrregiões do CSV de bairros
    if bairros_csv_file:
        if not bairros_csv_file.exists():
            print(f"⚠️ Arquivo '{bairros_csv_file}' não encontrado.")
            return
        df_bairros = pd.read_csv(bairros_csv_file)
        if "bairro" not in df_bairros.columns or "microrregiao" not in df_bairros.columns:
            print(f"⚠️ Colunas 'bairro' ou 'microrregiao' ausentes em {bairros_csv_file}.")
            return

        # Faz merge para adicionar microrregião ao df_ego
        df_ego = df_ego.merge(df_bairros[["bairro", "microrregiao"]], on="bairro", how="left")

    if "microrregiao" not in df_ego.columns:
        print("⚠️ Coluna 'microrregiao' ausente em ego_bairro.csv.")
        return

    # Calcula densidade média por microrregião
    df_group = df_ego.groupby("microrregiao")["densidade_ego"].mean()

    # Ordena pelo nome da microrregião
    df_group = df_group.sort_index(ascending=True)

    plt.figure(figsize=(10, 6))
    df_group.plot(kind="bar", color="cornflowerblue", edgecolor="black")
    plt.title("Ranking de Densidade Média de Ego-Subredes por Microrregião")
    plt.ylabel("Densidade Média")
    plt.xlabel("Microrregião")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_filename.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_filename)
    plt.close()
    print(f"✅ Gráfico de densidade salvo em: {output_filename}")


# Subgrafo dos 10 bairros com maior grau
def visualize_top_degree_subgraph(graph: Graph, output_filename: Path, top_n: int = 10):
    """
    Gera uma visualização com os bairros mais conectados (maior grau),
    com vértices mais afastados para melhor legibilidade.
    """
    from pyvis.network import Network

    print(f"🌐  Gerando subgrafo dos {top_n} bairros com maior grau...")

    # Selecionar top N nós por grau
    graus = sorted(
        [(n, graph.get_degree(n)) for n in graph.get_nodes()],
        key=lambda x: x[1],
        reverse=True
    )
    top_nodes = [n for n, _ in graus[:top_n]]
    subgraph = graph.get_induced_subgraph(top_nodes)

    # Criar rede PyVis
    net = Network(height="750px", width="100%", bgcolor="#222", font_color="white", notebook=False)

    # Adicionar nós e arestas
    for node in subgraph.get_nodes():
        net.add_node(node, label=node, size=32, color="#00FFAA")

    for u in subgraph.get_nodes():
        for v in subgraph.adj[u]:
            net.add_edge(u, v, color="#999")

    # 🔧 Ajuste de física — aumenta o afastamento dos vértices
    net.barnes_hut(
        gravity=-15000,        # aumenta repulsão geral
        central_gravity=0.15,  # mantém estrutura coesa mas menos centrada
        spring_length=50,     # aumenta a distância "ideal" entre nós conectados
        spring_strength=0.005, # torna as arestas mais soltas
        damping=0.85           # suaviza movimento
    )

    # Salvar visualização
    net.save_graph(str(output_filename))
    print(f"✅ Subgrafo dos top {top_n} bairros salvo em: {output_filename}")

    # Nota analítica
    print("🧠 Insight: Bairros mais conectados aparecem próximos, mas agora com mais espaçamento visual.")
