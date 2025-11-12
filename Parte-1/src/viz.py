# src/viz.py

from pyvis.network import Network
from typing import List
from pathlib import Path
import pandas as pd
import sys
import json

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
def export_full_graph_json(graph: Graph, output_json: Path):
    """Exporta o grafo completo em formato JSON simples (para uso no HTML interativo)."""
    nodes = [{"id": n, "label": n} for n in graph.get_nodes()]
    edges = [{"from": u, "to": v, "weight": attrs.get("weight", 1.0)}
             for u in graph.get_nodes() for v, attrs in graph.adj[u].items()]
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=2)
    print(f"✅ Grafo completo exportado em: {output_json}")


#AJEITAR ESSA FUNÇÃO E A DO MICRORREGIOES INTERATIVA
def generate_interactive_html_inline(output_html: Path, graph_data: dict, ego_csv_path: Path):
    """
    Gera um HTML interativo com dropdowns e tooltip contendo microrregião.
    Compatível com JSON contendo "microrregioes" e "bairros_microrregiao".
    """
    import json as _json

    ego_df = pd.read_csv(ego_csv_path)
    ego_info = {
        row["bairro"]: {
            "grau": row["grau"],
            "densidade_ego": row["densidade_ego"]
        }
        for _, row in ego_df.iterrows()
    }

    # Junta todos os nós e arestas de todas as microrregiões
    all_nodes, all_edges = [], []
    for mic, data in graph_data["microrregioes"].items():
        for n in data["nodes"]:
            bairro_nome = n["label"]
            # adiciona grau e densidade se existir no CSV
            info = ego_info.get(bairro_nome, {})
            n["grau"] = info.get("grau", None)
            n["densidade_ego"] = info.get("densidade_ego", None)
        all_nodes.extend(data["nodes"])
        all_edges.extend(data["edges"])


      # Adiciona arestas entre microrregiões se existirem
    if "inter_edges" in graph_data:
        all_edges.extend(graph_data["inter_edges"])

    merged_data = {
        "nodes": all_nodes,
        "edges": all_edges,
        "bairros_microrregiao": graph_data["bairros_microrregiao"]
    }
  

    raw_json = _json.dumps(merged_data, ensure_ascii=False)

    template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<title>Grafo Interativo - Recife</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
body { margin:0; font-family:Arial,Helvetica,sans-serif; background:#f8f9fa; }
#graphContainer { height:84vh; width:100%; border-top:1px solid #ccc; }
header { background:#007bff; color:#fff; padding:10px; text-align:center; font-size:22px; }
.controls { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; align-items:center; padding:10px; background:#fff; }
select, button { padding:6px 8px; font-size:14px; }
#legend { position:fixed; bottom:20px; left:20px; background:rgba(255,255,255,0.95); padding:8px; border-radius:6px; }
</style>
</head>
<body>
<header>Mapa Interativo dos Bairros do Recife</header>

<div class="controls">
  <label>Origem:</label>
  <select id="origin"></select>
  <label>Destino:</label>
  <select id="dest"></select>
  <button id="btnHighlight">Calcular e destacar caminho</button>
  <button id="btnFit">Centralizar</button>
</div>

<div class="controls">
  <label>Buscar bairro:</label>
  <select id="searchSelect"></select>
  <button id="btnSearch">🔍 Buscar bairro</button>
</div>

<div id="graphContainer"></div>
<div id="legend"><b>Legenda</b><br>🔵 Bairros comuns<br>🔴 Caminho destacado<br>🟢 Bairro buscado</div>

<script>
const rawData = __RAW_JSON_PLACEHOLDER__;
const bairroToMicro = rawData.bairros_microrregiao;

// --- Dropdowns de origem/destino e busca ---
const originSel = document.getElementById('origin');
const destSel = document.getElementById('dest');
const searchSel = document.getElementById('searchSelect');

// Preenche os selects
rawData.nodes.forEach(n => {
  const opt1 = document.createElement('option');
  const opt2 = document.createElement('option');
  const opt3 = document.createElement('option');
  opt1.value = opt1.textContent = n.label;
  opt2.value = opt2.textContent = n.label;
  opt3.value = opt3.textContent = n.label;
  originSel.appendChild(opt1);
  destSel.appendChild(opt2);
  searchSel.appendChild(opt3);
});

// --- Criação dos nós e arestas ---
const nodes = new vis.DataSet(rawData.nodes.map(n => ({
  id: n.id,
  label: n.label,
  title: `
  ${n.label}
  Grau: ${n.grau ?? 'N/D'}
  Microrregião: ${bairroToMicro[n.label] ?? 'Desconhecida'}
  Densidade ego: ${n.densidade_ego ?? 'N/D'}
  `,
  color:{ background:'#007bff', border:'#007bff' }, size:8
})));

const edges = new vis.DataSet(rawData.edges.map((e,i) => ({
  id: 'e'+i, from: e.from, to: e.to, weight: e.weight, color:{ color:'#d3d3d3' }, width:1
})));

// --- Configuração da rede ---
const container = document.getElementById('graphContainer');
const options = {
  nodes: { shape:'dot', font:{size:14}, borderWidth:1 },
  edges: { smooth:true },
  physics: {
    enabled:true, solver:'forceAtlas2Based',
    forceAtlas2Based:{gravitationalConstant:-60, springLength:120},
    stabilization:{iterations:100}
  },
  interaction: { dragNodes:true, zoomView:true, hover:true, tooltipDelay:150 }
};
const network = new vis.Network(container, {nodes, edges}, options);

// --- Funções auxiliares ---
function buildLabelToId() {
  const map = {};
  rawData.nodes.forEach(n => map[n.label] = n.id);
  return map;
}

// Implementação simples de Dijkstra
function dijkstraAdj(startLabel, goalLabel) {
  const labelToId = buildLabelToId();
  const start = labelToId[startLabel], goal = labelToId[goalLabel];
  if (!start || !goal) return { cost: Infinity, path: [] };
  const adj = {};
  rawData.nodes.forEach(n => adj[n.id] = []);
  rawData.edges.forEach(e => {
    adj[e.from].push({ to: e.to, w: e.weight });
    adj[e.to].push({ to: e.from, w: e.weight });
  });
  const dist = {}, prev = {};
  Object.keys(adj).forEach(u => { dist[u] = Infinity; prev[u] = null; });
  dist[start] = 0;
  const pq = [{ v: start, d: 0 }];
  while (pq.length) {
    pq.sort((a,b) => a.d - b.d);
    const u = pq.shift().v;
    if (u === goal) break;
    for (const e of adj[u]) {
      const alt = dist[u] + (e.w || 1);
      if (alt < dist[e.to]) { dist[e.to] = alt; prev[e.to] = u; pq.push({ v: e.to, d: alt }); }
    }
  }
  if (dist[goal] === Infinity) return { cost: Infinity, path: [] };
  const path = []; let cur = goal;
  while (cur) { path.unshift(cur); cur = prev[cur]; if (cur === null) break; }
  return { cost: dist[goal], path };
}

// --- Reset visual ---
function resetVisual() {
  nodes.get().forEach(n => {
    nodes.update({
      id: n.id,
      color: { background:'#007bff', border:'#007bff' },
      size: 8
    });
  });
  edges.get().forEach(e => {
    edges.update({
      id: e.id,
      color: { color:'#d3d3d3' },
      width: 1
    });
  });
  network.redraw();
}

// --- Destacar caminho ---
function highlightFoundPathByIds(idPath) {
  resetVisual();
  idPath.forEach(pid => nodes.update({ id: pid, color:{ background:'#FF4136', border:'#FF4136' }, size:16 }));
  for (let i=0;i<idPath.length-1;i++) {
    const a=idPath[i], b=idPath[i+1];
    edges.get().forEach(e => {
      if ((e.from===a && e.to===b) || (e.from===b && e.to===a)) {
        edges.update({ id:e.id, color:{ color:'#FF4136' }, width:3 });
      }
    });
  }
  network.fit({ nodes:idPath, padding:80 });
}

// --- Buscar bairro (dropdown) ---
document.getElementById('btnSearch').addEventListener('click', () => {
  const selected = searchSel.value;
  if (!selected) return;
  const labelToId = buildLabelToId();
  const foundId = labelToId[selected];
  if (!foundId) { alert('Bairro não encontrado'); return; }
  resetVisual();
  nodes.update({ id: foundId, color:{ background:'#2ECC40', border:'#2ECC40' }, size:18 });
  network.focus(foundId, { scale:1.5, animation:true });
});

// --- Botões principais ---
document.getElementById('btnHighlight').addEventListener('click', () => {
  const origin = originSel.value;
  const dest = destSel.value;
  if (!origin || !dest) { alert('Escolha origem e destino'); return; }
  const res = dijkstraAdj(origin, dest);
  if (!res.path || res.path.length === 0) { alert('Nenhum caminho encontrado'); return; }
  highlightFoundPathByIds(res.path);
});

document.getElementById('btnFit').addEventListener('click', () => network.fit());
</script>
</body>
</html>
"""
    html_final = template.replace("__RAW_JSON_PLACEHOLDER__", raw_json)
    output_html.write_text(html_final, encoding="utf-8")



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

def visualize_microrregioes(output_html, json_file):
    """
    Cria um HTML interativo para alternar entre grafos de microrregiões,
    com espaçamento melhorado entre os vértices (novo formato JSON).
    """
    print(f"🎨 Gerando visualização interativa das microrregiões...")

    json_file = Path(json_file)
    if not json_file.exists():
        raise FileNotFoundError(f"🚨 Arquivo JSON não encontrado: {json_file}")

    with open(json_file, "r", encoding="utf-8") as f:
        microrregioes_data = json.load(f)

    # Novo formato: dados estão dentro da chave "microrregioes"
    if "microrregioes" in microrregioes_data:
        microrregioes_data = microrregioes_data["microrregioes"]

    output_html = Path(output_html)
    output_html.parent.mkdir(parents=True, exist_ok=True)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Microrregiões de Recife</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 0; }}
            header {{ background: #007bff; color: white; padding: 12px; text-align: center; font-size: 22px; }}
            select {{ margin: 20px; padding: 8px; font-size: 16px; }}
            #graphContainer {{ width: 100%; height: 85vh; }}
        </style>
        <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <script>
            let data = {json.dumps(microrregioes_data, ensure_ascii=False)};

            function updateGraph() {{
                const microrregiao = document.getElementById('microSelect').value;
                const microData = data[microrregiao];

                const nodes = new vis.DataSet(microData.nodes);
                const edges = new vis.DataSet(microData.edges);

                const container = document.getElementById('graphContainer');
                const networkData = {{ nodes, edges }};
                const options = {{
                    nodes: {{
                        shape: 'dot',
                        size: 12,
                        font: {{ size: 14 }}
                    }},
                    edges: {{
                        color: '#007bff',
                        smooth: false
                    }},
                    physics: {{
                        enabled: true,
                        solver: 'forceAtlas2Based',
                        forceAtlas2Based: {{
                            gravitationalConstant: -60,
                            centralGravity: 0.005,
                            springLength: 150,
                            springConstant: 0.02
                        }},
                        stabilization: {{
                            iterations: 100
                        }}
                    }},
                    interaction: {{
                        dragNodes: true,
                        zoomView: true
                    }}
                }};
                new vis.Network(container, networkData, options);
            }}

            window.onload = updateGraph;
        </script>
    </head>
    <body>
        <header>Mapa Interativo das Microrregiões de Recife</header>
        <div style="text-align:center;">
            <label for="microSelect">Escolha uma microrregião:</label>
            <select id="microSelect" onchange="updateGraph()">
    """

    # Adiciona opções ao dropdown
    for microrregiao in microrregioes_data.keys():
        html_content += f'<option value="{microrregiao}">{microrregiao}</option>\n'

    html_content += """
            </select>
        </div>
        <div id="graphContainer"></div>
    </body>
    </html>
    """

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Interface salva em: {output_html}")

